#!/bin/bash

set -euo pipefail

source ./backend/deploy/backend.sh

function print_help() {
  cat <<'USAGE'
Usage:
  ./deploy.sh <target> [action]

Targets:
  local
  remote
  help

Actions:
  init
  update (default for remote)
  restart
  status
  logs
  down

Quick Start:
  ./deploy.sh local           # development compose
  ./deploy.sh remote init     # production compose
  ./deploy.sh remote update
USAGE
}

function require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "部署失败：未检测到命令 $cmd"
    exit 1
  fi
}

function ensure_local_config() {
  local cfg="deploy/local.env"
  local example="deploy/local.env.example"

  if [[ ! -f "$cfg" ]]; then
    if [[ -f "$example" ]]; then
      cp "$example" "$cfg"
      echo "已生成 ${cfg}，可按需修改。"
    else
      echo "部署失败：缺少 ${cfg}，且未找到 ${example}"
      exit 1
    fi
  fi

  set -a
  # shellcheck source=/dev/null
  source "$cfg"
  set +a
}

function run_local() {
  local action="${1:-init}"
  require_cmd docker
  ensure_local_config
  backend_local "$action"
}

function run_remote() {
  local action="${1:-update}"
  require_cmd docker
  backend_remote "$action"
}

TARGET="${1:-help}"
ACTION="${2:-}"

case "$TARGET" in
  local)
    run_local "$ACTION"
    ;;
  remote)
    run_remote "$ACTION"
    ;;
  help|-h|--help)
    print_help
    ;;
  *)
    echo "未知 target: $TARGET"
    print_help
    exit 1
    ;;
esac
