#!/usr/bin/env bash

# 前后端环境初始化脚本

set -e

########################################
# 颜色
########################################

GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
BLUE="\033[1;34m"
NC="\033[0m"

log() {
  echo -e "${BLUE}▶ $1${NC}"
}

success() {
  echo -e "${GREEN}✔ $1${NC}"
}

warn() {
  echo -e "${YELLOW}⚠ $1${NC}"
}

error() {
  echo -e "${RED}✖ $1${NC}"
}

upsert_env_var() {
  local file="$1"
  local key="$2"
  local value="$3"
  if grep -q "^${key}=" "$file"; then
    sed -i.bak "s|^${key}=.*|${key}=${value}|" "$file"
    rm -f "${file}.bak"
  else
    echo "${key}=${value}" >> "$file"
  fi
}

ensure_env_var() {
  local file="$1"
  local key="$2"
  local value="$3"
  local current
  current="$(grep "^${key}=" "$file" 2>/dev/null | tail -n 1 | cut -d'=' -f2- || true)"
  if [ -z "$current" ]; then
    upsert_env_var "$file" "$key" "$value"
  fi
}

########################################
# 检查依赖
########################################

log "检查系统依赖..."

command -v python3 >/dev/null || { error "未检测到 python3，请先安装 Python3"; exit 1; }
command -v npm >/dev/null || { error "未检测到 npm，请先安装 Node.js"; exit 1; }
command -v openssl >/dev/null || { error "未检测到 openssl"; exit 1; }

success "依赖检查通过"

########################################
# 创建 Python 虚拟环境
########################################

log "准备 Python 虚拟环境..."

if [ ! -d ".venv" ]; then
  log "创建 .venv 虚拟环境..."
  python3 -m venv .venv
  success "虚拟环境创建完成"
else
  warn ".venv 已存在，跳过创建"
fi

########################################
# 升级 pip
########################################

log "升级 pip..."

.venv/bin/python -m pip install --upgrade pip >/dev/null

success "pip 已升级"

########################################
# 安装后端依赖
########################################

log "安装后端依赖..."

.venv/bin/pip install -r backend/requirements/dev.txt

success "后端依赖安装完成"

########################################
# 创建 backend/.env
########################################

if [ ! -f "backend/.env" ]; then
  log "创建 backend/.env..."

  cp backend/.env.example backend/.env
else
  warn "backend/.env 已存在，将按需补全缺失项"
fi

SECRET_KEY="$(openssl rand -hex 32)"
JWT_SECRET_KEY="$(openssl rand -hex 32)"

ensure_env_var "backend/.env" "SECRET_KEY" "$SECRET_KEY"
ensure_env_var "backend/.env" "JWT_SECRET_KEY" "$JWT_SECRET_KEY"
# DEV_DATABASE_URL 为空时自动兜底 sqlite 文件库，保证首次初始化可完成。
ensure_env_var "backend/.env" "DEV_DATABASE_URL" "sqlite:///dev.db"

success "backend/.env 已完成幂等初始化（密钥/数据库连接）"

########################################
# 数据库迁移
########################################

log "执行数据库迁移..."

(
  cd backend
  ../.venv/bin/flask deploy
)

success "数据库迁移完成"

########################################
# 安装前端依赖
########################################

log "安装前端依赖..."

(
  cd frontend
  npm install
)

success "前端依赖安装完成"

########################################
# 创建 frontend env
########################################

if [ ! -f "frontend/.env.development" ]; then
  log "创建前端环境变量..."

  cp frontend/.env.development.example frontend/.env.development

  success "frontend/.env.development 创建完成"
else
  warn "frontend/.env.development 已存在，跳过创建"
fi

########################################
# 完成
########################################

echo ""
success "环境初始化完成！"
echo ""

echo "下一步启动服务："
echo "  ./start.sh"
echo "（start.sh 会自动使用 .venv，无需手动激活虚拟环境）"
echo ""
