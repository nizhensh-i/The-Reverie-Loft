<div align="center">

# Loft

### 一个现代化、功能丰富的社交平台

**基于 Vue3 + Flask 构建的开源社交系统**

面向真实生产场景的开源社交平台模板，支持实时聊天、内容互动与“依赖缺失可降级”运行。

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/nizhensh-i/The-Reverie-Loft/actions/workflows/python-tests.yml/badge.svg)](https://github.com/nizhensh-i/The-Reverie-Loft/actions/workflows/python-tests.yml)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7.x-DC382D.svg)](https://redis.io/)

[项目简介](#-项目简介) • [快速上手](#-快速上手) • [配置指南](#-第三方服务配置指南) • [部署文档](#-部署指南) • [FAQ](#-常见问题)

</div>

---

## ⭐ Highlights

- 后端采用 clean 风格分层（`domain / services / infrastructure`）+ 依赖注入容器
- 支持实时通信：HTTP API + Socket.IO 双服务拆分
- 中间件可降级：Redis / 邮件 / 对象存储 / OAuth 缺失时系统仍可启动
- 内置部署脚本：`deploy.sh local/remote` 统一编排 dev/prod compose
- 前后端解耦，前端 Vite 开发代理直连后端服务

## 🎬 演示

- 在线预览：TODO
- 演示视频：TODO
- GIF 演示：TODO

## 🖼️ 预览图

> 当前使用项目内真实页面截图；后续可替换为一张拼接图（PC + Mobile）。

![Loft Preview PC](docs/用户首页.png)
![Loft Preview Mobile](docs/绑定邮箱页面.png)

---

## 📖 项目简介

Loft 是一个全栈开源社交平台项目，采用现代化技术栈构建，并已在后端落地 clean 风格分层（domain / services / infrastructure）与依赖能力降级机制。

### ✨ 核心功能

- 👤 **用户系统**：注册、登录、个人资料管理
- 📱 **第三方登录**：支持 GitHub、Google、QQ、微博 OAuth
- 💬 **实时聊天**：基于 WebSocket 的即时通讯
- 📝 **内容发布**：支持文字、图片动态发布
- 👍 **互动功能**：点赞、评论、关注
- 🔐 **权限管理**：基于 JWT 的安全认证
- 📊 **数据分析**：操作日志、用户行为统计
- 🎨 **响应式设计**：完美支持 PC 和移动端

### 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| **前端** | Vue 3 + Vite | 现代化构建工具与响应式框架 |
| | Element Plus | UI 组件库 |
| | Vue Router | 前端路由管理 |
| | Pinia | 状态管理 |
| **后端** | Flask 3.x | Python Web 框架 |
| | SQLAlchemy | ORM 数据库操作 |
| | Flask-JWT-Extended | JWT 认证 |
| | Flask-SocketIO | WebSocket 实时通信 |
| | dependency-injector | 依赖注入容器 |
| **数据库** | MySQL 8.x | 关系型数据存储（核心必需） |
| | Redis 7.x | 缓存/限流/消息能力（可降级） |
| **部署** | Shell 脚本 + Docker Compose | `deploy.sh` 编排本地/远程部署 |
| | Nginx | 可选反向代理与 HTTPS 终止 |

### 🧠 能力降级设计

Loft 在基础设施层实现了 capability 检测与降级策略：

- Redis 不可用：缓存/限流/实时消息/异步任务进入降级模式（例如 Celery 回退为内存 eager 执行）
- 邮件未配置：邮件服务降级，验证码邮件不可发送，但主流程可运行
- 七牛云未配置：上传与签名访问降级，相关接口返回受限
- OAuth 未配置：第三方登录入口自动不可用，不影响账号密码体系

---

## 🚀 快速上手

> 默认推荐非 Docker 启动（`start.sh`），外部依赖最少。Docker 是可选方式。

### 前置要求（非 Docker 主路径）

- Python 3.12（建议）
- Node.js 18+（建议）与 npm/pnpm
- MySQL 8.x
- Git

### 第 0 步：准备 MySQL 并建库

```sql
CREATE DATABASE flasky CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> 如果你用的是其他库名，请在 `backend/.env` 的 `DEV_DATABASE_URL` 中保持一致。

### ⚡ 三步启动项目（推荐）

#### 第一步：克隆仓库

```bash
git clone https://github.com/your-username/loft.git
cd loft
```

#### 第二步：安装依赖并配置环境变量

```bash
# 后端依赖
cd backend
pip install -r requirements/dev.txt

# 配置后端环境变量
cp .env.example .env

# 回到项目根目录安装前端依赖
cd ../frontend
npm install

# 配置前端环境变量（开发）
cp .env.development.example .env.development

cd ..
```

**最低必填配置（核心）**

```bash
# backend/.env 最小示例
SECRET_KEY=replace-with-random-string
JWT_SECRET_KEY=replace-with-random-string
DEV_DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/flasky?charset=utf8mb4
```

可选：使用以下命令生成随机密钥。

```bash
openssl rand -hex 32
```

#### 第三步：执行迁移并启动

```bash
cd backend
flask deploy
cd ..

./start.sh
```

启动后默认开发访问地址：
- 前端：`http://localhost:5172`
- 后端 HTTP：`http://localhost:4289`
- 后端 Socket.IO：`http://localhost:4290`

端口可自定义（通过环境变量）：
- 前端：`VITE_PORT`（`frontend/.env.development`）
- 后端 HTTP：`FLASK_RUN_PORT`（`backend/.env`）
- 后端 Socket.IO：`SOCKETIO_RUN_PORT`（`backend/.env`，默认 `4290`）

---

## 🔧 第三方服务配置指南

项目支持“可用即启用、缺失即降级”的能力模型。请按优先级配置：

### 1) 核心必需（不建议缺失）

| 配置项 | 位置 | 说明 |
|------|------|------|
| `SECRET_KEY` / `JWT_SECRET_KEY` | `backend/.env` | Flask/JWT 基础安全密钥 |
| `DEV_DATABASE_URL`（开发）或 `DATABASE_URL`（生产） | `backend/.env` / `backend/.env.prod` | MySQL 连接 |

### 2) 可选降级（缺失可启动，但对应功能受限）

| 能力 | 关键配置 | 未配置影响 |
|------|------|------|
| Redis | `DEV_REDIS_URL` / `REDIS_URL` / `REDIS_HOST` | 缓存、限流、实时消息、异步任务进入降级模式 |
| 邮件 | `MAIL_USERNAME` / `MAIL_PASSWORD` | 邮件验证码、通知不可用（系统可运行） |
| 七牛云对象存储 | `QINIU_ACCESS_KEY` / `QINIU_SECRET_KEY` / `QINIU_BUCKET_NAME` / `QINIU_DOMAIN` | 图片上传与签名访问不可用 |
| OAuth 登录 | 各平台 `*_CLIENT_ID` / `*_CLIENT_SECRET` | 对应第三方登录入口不可用 |

### 3) 配置示例

```bash
# MySQL（开发）
DEV_DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/flasky?charset=utf8mb4

# Redis（可选）
DEV_REDIS_URL=redis://:1234@127.0.0.1:6379/0

# 七牛云（可选）
QINIU_DOMAIN=https://your-bucket-domain.example.com
```

> 安全提示：请勿将真实密钥提交到仓库，示例值仅用于演示。

---

## 🧱 项目结构

```text
loft/
├── frontend/                    # Vue3 + Vite 前端
│   ├── src/
│   │   ├── api/                # 请求封装与接口定义
│   │   ├── stores/             # Pinia 状态
│   │   ├── views/              # 页面视图
│   │   └── router/             # 路由
│   └── .env.development.example
├── backend/                     # Flask 后端
│   ├── app/
│   │   ├── domain/             # 领域模型/策略/端口协议
│   │   ├── services/           # 应用服务（用例编排）
│   │   ├── infrastructure/     # DB/Redis/OAuth/Storage/Adapter 实现
│   │   ├── api/                # /api/v1 路由
│   │   ├── auth/               # /auth 路由
│   │   └── container.py        # 依赖注入容器装配
│   ├── migrations/             # Alembic 迁移脚本
│   ├── flasky.py               # HTTP 入口
│   └── flasky_socketio.py      # Socket.IO 入口
├── deploy/                      # 本地/远程部署配置模板
├── docs/                        # 文档与示例配置
├── start.sh                     # 非 Docker 一键启动脚本
└── deploy.sh                    # Docker 部署统一入口
```

### 架构与数据流（简图）

```mermaid
flowchart LR
  A[Vue3 Frontend] -->|HTTP /api| B[Flask HTTP :4289]
  A -->|WebSocket /socket.io| C[Flask SocketIO :4290]

  B --> D[(MySQL)]
  B --> E[(Redis 可选)]
  C --> E

  B --> F[Mail Adapter 可选]
  B --> G[Qiniu Storage 可选]
  B --> H[OAuth Providers 可选]

  subgraph Backend Clean Layers
    I[Domain] --> J[Services]
    J --> K[Infrastructure Adapters]
  end

  B --> I
  C --> I
```

---

## 📦 部署指南

### 方案 A：项目内置脚本部署（推荐）

统一入口：

```bash
./deploy.sh <target> [action]
```

- `target=local`：本地容器运行，使用 `backend/docker-compose.dev.yaml`
- `target=remote`：远程服务器部署，使用 `backend/docker-compose.prod.yaml`

Compose service name（后端 compose 内服务名）：
- `backend`
- `mysql`
- `myredis`

常用命令：

```bash
# 本地首次
./deploy.sh local init

# 本地更新后端
./deploy.sh local update

# 远程首次
cp deploy/remote.env.example deploy/remote.env
# 填写 REMOTE_HOST / REMOTE_USER / REMOTE_BACKEND_DIR
./deploy.sh remote init

# 远程更新
./deploy.sh remote update
```

详细说明见 [docs/deploy.md](docs/deploy.md)。

### 方案 B：可选 Nginx 反向代理（生产常见）

README 只放最小可用配置，完整示例见 [docs/nginx.conf.example](docs/nginx.conf.example)。

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://localhost:4289;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://localhost:4290;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
        proxy_buffering off;
    }
}
```

---

## 🗄️ 数据库初始化与迁移

### 快速路径（推荐）

```bash
cd backend
flask deploy
```

`flask deploy` 会执行：
- 迁移到最新版本（`upgrade`）
- 在历史迁移链不完整且核心表缺失时兜底 `create_all + stamp head`
- 初始化角色权限与自关注关系

### 手动迁移（开发常用）

```bash
cd backend
export FLASK_APP=flasky.py

# 生成迁移脚本
flask db migrate -m "your migration message"

# 应用迁移
flask db upgrade

# 回滚一步（可选）
flask db downgrade -1
```

### 种子数据

- 默认“角色权限/自关注”在 `flask deploy` 中自动初始化
- 业务演示数据可通过管理员接口生成：`GET /api/v1/users/generate_posts`

---

## 🔐 安全与生产注意事项

- 不要提交真实密钥（`.env`、`deploy/*.env`、云服务 AK/SK）
- 生产环境必须替换 `SECRET_KEY`、`JWT_SECRET_KEY`
- CORS 请按实际域名收敛，不要长期全开
- Socket.IO 走 Nginx 时必须带 `Upgrade/Connection` 头并放宽读写超时
- Redis 降级可保证可用性，但会影响限流精度、缓存命中与异步吞吐
- 上线前建议开启日志轮转与错误告警

---

## ❓ 常见问题

### 1. ❌ `start.sh` 启动后后端连不上 MySQL

**排查步骤：**

1. 检查 MySQL 是否可连接（本机/远程）
2. 检查 `backend/.env` 中 `DEV_DATABASE_URL` 是否正确
3. 确认账号有对应数据库权限

**示例：**
```bash
mysql -h 127.0.0.1 -P 3306 -u your_user -p
```

### 2. ⚠️ Redis 没有安装，项目还能跑吗？

可以。Redis 在本项目是可选能力，会进入降级模式。  
影响主要是：缓存/限流/部分实时与异步能力受限。

### 3. ❌ 七牛云上传返回 401 / `bad token`

请优先检查：
- `QINIU_ACCESS_KEY` / `QINIU_SECRET_KEY` 是否正确
- `QINIU_BUCKET_NAME` / `QINIU_DOMAIN` 是否与控制台一致
- `.env` 中变量是否包含多余空格

### 4. ❌ OAuth 登录回调失败（`redirect_uri_mismatch`）

请确认两端一致：
- OAuth 平台配置的回调地址
- 服务端实际回调地址（`/api/auth/oauth/callback/<provider>`）

生产环境务必使用实际域名与 HTTPS。

### 5. ❌ WebSocket 在 Nginx 后 502

请确认：
- Nginx 已配置 `/socket.io/` 代理和 `Upgrade/Connection` 头
- 后端 Socket.IO 服务监听在 `4290`
- 防火墙/安全组放行 80/443（或对应端口）

### 6. 🔍 如何快速确认 `.env` 已生效？

```bash
cd backend
python -c "from app.infrastructure.config.runtime_env import load_env; load_env(); import os; print('FLASK_CONFIG=', os.getenv('FLASK_CONFIG')); print('DEV_DATABASE_URL set=', bool(os.getenv('DEV_DATABASE_URL')))"
```

若输出 `DEV_DATABASE_URL set= True`，说明已从 `.env` 加载到进程环境。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/AmazingFeature`）
3. 提交更改（`git commit -m 'Add some AmazingFeature'`）
4. 推送到分支（`git push origin feature/AmazingFeature`）
5. 开启 Pull Request

### 本地开发命令

```bash
# 后端
cd backend
pip install -r requirements/dev.txt
python flasky.py

# 后端测试
pytest tests_api

# 前端
cd ../frontend
npm install
npm run dev
npm run build

# 仓库统一检查
cd ..
pre-commit run --all-files
```

---

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- 📧 项目维护者: your-email@example.com
- 🐛 Bug 反馈: [提交 Issue](https://github.com/nizhensh-i/The-Reverie-Loft/issues)

---

<div align="center">

**如果这个项目对你有帮助，请给个 Star 支持一下。**

Made with ❤️ by [nizhensh-i](https://github.com/nizhensh-i)

</div>
