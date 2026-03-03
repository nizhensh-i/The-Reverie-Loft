#!/bin/bash

set -euo pipefail

function deploy_step() {
  echo "$1"
}

function backend_init_defaults() {
  LOCAL_BACKEND_DIR="${LOCAL_BACKEND_DIR:-./backend}"
  COMPOSE_FILE_BASE="${COMPOSE_FILE_BASE:-${COMPOSE_FILE:-}}"

  BACKEND_IMAGE="${BACKEND_IMAGE:-nizhenshi/flasky_backend}"
  BACKEND_TAG="${BACKEND_TAG:-latest}"

  BACKEND_SERVICE_NAME="${BACKEND_SERVICE_NAME:-backend}"
  MYSQL_SERVICE_NAME="${MYSQL_SERVICE_NAME:-mysql}"
  REDIS_SERVICE_NAME="${REDIS_SERVICE_NAME:-myredis}"

  SSH_PORT="${SSH_PORT:-22}"
  REMOTE_TAR_DIR="${REMOTE_TAR_DIR:-/home/ubuntu/user}"
}

function backend_apply_mode_defaults() {
  local mode="$1"

  if [[ -z "${COMPOSE_FILE_BASE}" ]]; then
    if [[ "$mode" == "local" ]]; then
      COMPOSE_FILE_BASE="docker-compose.dev.yaml"
    else
      COMPOSE_FILE_BASE="docker-compose.prod.yaml"
    fi
  fi
}

function backend_compose_files_local() {
  echo "-f ${COMPOSE_FILE_BASE}"
}

function backend_compose_files_remote() {
  echo "-f ${COMPOSE_FILE_BASE}"
}

function backend_require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "部署失败：未检测到命令 $cmd"
    return 1
  fi
}

function backend_require_compose() {
  if ! docker compose version >/dev/null 2>&1; then
    echo "部署失败：未检测到 docker compose"
    return 1
  fi
}

function backend_ensure_runtime_env_files() {
  local mode="$1"
  local env_file
  local redis_env_file="${LOCAL_BACKEND_DIR}/.env-redis"
  local mysql_env_file="${LOCAL_BACKEND_DIR}/.env-mysql"

  if [[ "$mode" == "remote" ]]; then
    env_file="${LOCAL_BACKEND_DIR}/.env.prod"
  else
    env_file="${LOCAL_BACKEND_DIR}/.env"
  fi

  if [[ ! -f "$env_file" ]]; then
    if [[ "$mode" == "local" && -f "${LOCAL_BACKEND_DIR}/.env.example" ]]; then
      cp "${LOCAL_BACKEND_DIR}/.env.example" "$env_file"
      echo "已生成 ${env_file}，请按需修改配置后重试。"
    else
      echo "部署失败：缺少 ${env_file}，且未找到 .env.example"
      return 1
    fi
  fi

  if [[ ! -f "$redis_env_file" ]]; then
    cat > "$redis_env_file" <<'EOR'
# Redis 容器参数
REDIS_PASSWORD=1234
REDIS_SAVE=60 1
REDIS_LOGLEVEL=warning
EOR
    echo "已生成 ${redis_env_file}（默认值）"
  fi

  if [[ ! -f "$mysql_env_file" ]]; then
    cat > "$mysql_env_file" <<'EOM'
# MySQL 容器参数
MYSQL_RANDOM_ROOT_PASSWORD=yes
MYSQL_DATABASE=flasky
MYSQL_USER=flasky
MYSQL_PASSWORD=1234
EOM
    echo "已生成 ${mysql_env_file}（默认值）"
  fi
}

function backend_build_image() {
  local image_ref="${BACKEND_IMAGE}:${BACKEND_TAG}"
  if [[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]]; then
    docker build --platform linux/amd64 -t "$image_ref" "$LOCAL_BACKEND_DIR"
  else
    docker build -t "$image_ref" "$LOCAL_BACKEND_DIR"
  fi
}

function backend_compose_local() {
  local compose_action="$1"
  local compose_files
  compose_files="$(backend_compose_files_local)"
  (
    cd "$LOCAL_BACKEND_DIR"
    BACKEND_IMAGE="$BACKEND_IMAGE" BACKEND_TAG="$BACKEND_TAG" docker compose ${compose_files} $compose_action
  )
}

function backend_local() {
  local action="${1:-init}"

  backend_init_defaults
  backend_apply_mode_defaults "local"

  deploy_step "正在检查环境..."
  backend_require_cmd docker
  backend_require_compose

  deploy_step "正在准备配置..."
  backend_ensure_runtime_env_files "local"

  case "$action" in
    init)
      deploy_step "正在构建镜像..."
      backend_build_image
      deploy_step "正在更新服务..."
      backend_compose_local "up -d ${MYSQL_SERVICE_NAME} ${REDIS_SERVICE_NAME} ${BACKEND_SERVICE_NAME}"
      ;;
    update)
      deploy_step "正在构建镜像..."
      backend_build_image
      deploy_step "正在更新服务..."
      backend_compose_local "up -d --no-deps --force-recreate ${BACKEND_SERVICE_NAME}"
      ;;
    restart)
      deploy_step "正在更新服务..."
      backend_compose_local "restart ${BACKEND_SERVICE_NAME}"
      ;;
    status)
      deploy_step "正在获取服务状态..."
      backend_compose_local "ps"
      ;;
    logs)
      deploy_step "正在读取后端日志..."
      backend_compose_local "logs --tail=200 ${BACKEND_SERVICE_NAME}"
      ;;
    down)
      deploy_step "正在停止后端服务..."
      backend_compose_local "stop ${BACKEND_SERVICE_NAME}"
      ;;
    *)
      echo "部署失败：不支持的 action: $action"
      return 1
      ;;
  esac

  deploy_step "部署完成。"
}

function backend_remote_ssh() {
  local cmd="$1"
  if [[ -n "${REMOTE_PASSWORD:-}" ]]; then
    backend_require_cmd sshpass
    sshpass -p "$REMOTE_PASSWORD" ssh -p "$SSH_PORT" -o StrictHostKeyChecking=accept-new "$REMOTE_USER@$REMOTE_HOST" "$cmd"
  else
    ssh -p "$SSH_PORT" -o StrictHostKeyChecking=accept-new "$REMOTE_USER@$REMOTE_HOST" "$cmd"
  fi
}

function backend_remote_scp() {
  local src="$1"
  local dst="$2"
  if [[ -n "${REMOTE_PASSWORD:-}" ]]; then
    backend_require_cmd sshpass
    sshpass -p "$REMOTE_PASSWORD" scp -P "$SSH_PORT" "$src" "$REMOTE_USER@$REMOTE_HOST:$dst"
  else
    scp -P "$SSH_PORT" "$src" "$REMOTE_USER@$REMOTE_HOST:$dst"
  fi
}

function backend_load_remote_config() {
  local remote_config_file="${1:-deploy/remote.env}"

  if [[ ! -f "$remote_config_file" ]]; then
    if [[ -f "deploy/remote.env.example" ]]; then
      cp deploy/remote.env.example "$remote_config_file"
      echo "已生成 $remote_config_file，请先填写必填项后重试。"
    else
      echo "部署失败：缺少 $remote_config_file"
    fi
    return 1
  fi

  set -a
  # shellcheck source=/dev/null
  source "$remote_config_file"
  set +a

  backend_init_defaults

  if [[ -z "${REMOTE_HOST:-}" || -z "${REMOTE_USER:-}" || -z "${REMOTE_BACKEND_DIR:-}" ]]; then
    echo "部署失败：remote 配置缺少必填项（REMOTE_HOST/REMOTE_USER/REMOTE_BACKEND_DIR）"
    return 1
  fi
}

function backend_remote_prepare_files() {
  local backend_tar="$1"
  local image_ref="${BACKEND_IMAGE}:${BACKEND_TAG}"

  deploy_step "正在构建镜像..."
  backend_build_image
  docker save -o "$backend_tar" "$image_ref"

  deploy_step "正在上传服务器..."
  backend_remote_ssh "mkdir -p '$REMOTE_BACKEND_DIR' '$REMOTE_TAR_DIR'"
  backend_remote_scp "$LOCAL_BACKEND_DIR/$COMPOSE_FILE_BASE" "$REMOTE_BACKEND_DIR/$COMPOSE_FILE_BASE"
  backend_remote_scp "$LOCAL_BACKEND_DIR/.env.prod" "$REMOTE_BACKEND_DIR/.env.prod"
  backend_remote_scp "$LOCAL_BACKEND_DIR/.env-redis" "$REMOTE_BACKEND_DIR/.env-redis"
  backend_remote_scp "$LOCAL_BACKEND_DIR/.env-mysql" "$REMOTE_BACKEND_DIR/.env-mysql"
  backend_remote_scp "$backend_tar" "$REMOTE_TAR_DIR/$backend_tar"
}

function backend_remote() {
  local action="${1:-update}"
  local remote_compose_files

  deploy_step "正在检查环境..."
  backend_require_cmd docker
  backend_require_compose
  backend_require_cmd ssh
  backend_require_cmd scp

  deploy_step "正在准备配置..."
  backend_load_remote_config
  backend_apply_mode_defaults "remote"
  backend_ensure_runtime_env_files "remote"
  remote_compose_files="$(backend_compose_files_remote)"

  case "$action" in
    init|update)
      local tar_file
      tar_file="flasky_backend_${BACKEND_TAG}.tar"
      backend_remote_prepare_files "$tar_file"
      deploy_step "正在更新服务..."
      if [[ "$action" == "init" ]]; then
        backend_remote_ssh "
          set -e
          docker load -i '$REMOTE_TAR_DIR/$tar_file'
          cd '$REMOTE_BACKEND_DIR'
          BACKEND_IMAGE='$BACKEND_IMAGE' BACKEND_TAG='$BACKEND_TAG' docker compose ${remote_compose_files} up -d $MYSQL_SERVICE_NAME $REDIS_SERVICE_NAME $BACKEND_SERVICE_NAME
        "
      else
        backend_remote_ssh "
          set -e
          docker load -i '$REMOTE_TAR_DIR/$tar_file'
          cd '$REMOTE_BACKEND_DIR'
          BACKEND_IMAGE='$BACKEND_IMAGE' BACKEND_TAG='$BACKEND_TAG' docker compose ${remote_compose_files} up -d --no-deps --force-recreate $BACKEND_SERVICE_NAME
        "
      fi
      rm -f "$tar_file"
      ;;
    restart)
      deploy_step "正在更新服务..."
      backend_remote_ssh "cd '$REMOTE_BACKEND_DIR' && docker compose ${remote_compose_files} restart $BACKEND_SERVICE_NAME"
      ;;
    status)
      deploy_step "正在获取服务状态..."
      backend_remote_ssh "cd '$REMOTE_BACKEND_DIR' && docker compose ${remote_compose_files} ps"
      ;;
    logs)
      deploy_step "正在读取后端日志..."
      backend_remote_ssh "cd '$REMOTE_BACKEND_DIR' && docker compose ${remote_compose_files} logs --tail=200 $BACKEND_SERVICE_NAME"
      ;;
    down)
      deploy_step "正在停止后端服务..."
      backend_remote_ssh "cd '$REMOTE_BACKEND_DIR' && docker compose ${remote_compose_files} stop $BACKEND_SERVICE_NAME"
      ;;
    *)
      echo "部署失败：不支持的 action: $action"
      return 1
      ;;
  esac

  deploy_step "部署完成。"
}
