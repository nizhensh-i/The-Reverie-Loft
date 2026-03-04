#!/usr/bin/env bash

# 前后端环境创初始化脚本

# 检查依赖
# ↓
# 创建 venv
# ↓
# 激活 venv
# ↓
# 升级 pip
# ↓
# 安装 backend 依赖
# ↓
# 创建 env
# ↓
# 数据库迁移
# ↓
# 安装 frontend 依赖
# ↓
# 创建 frontend env

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
# 激活虚拟环境
########################################

log "激活虚拟环境..."

source .venv/bin/activate

########################################
# 升级 pip
########################################

log "升级 pip..."

pip install --upgrade pip >/dev/null

success "pip 已升级"

########################################
# 安装后端依赖
########################################

log "安装后端依赖..."

pip install -r backend/requirements/dev.txt

success "后端依赖安装完成"

########################################
# 创建 backend/.env
########################################

if [ ! -f "backend/.env" ]; then
  log "创建 backend/.env..."

  cp backend/.env.example backend/.env

  SECRET_KEY=$(openssl rand -hex 32)
  JWT_SECRET_KEY=$(openssl rand -hex 32)

  echo "" >> backend/.env
  echo "SECRET_KEY=$SECRET_KEY" >> backend/.env
  echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> backend/.env

  success "backend/.env 创建完成并生成随机密钥"
else
  warn "backend/.env 已存在，跳过创建"
fi

########################################
# 数据库迁移
########################################

log "执行数据库迁移..."

(
  cd backend
  flask deploy
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
echo ""