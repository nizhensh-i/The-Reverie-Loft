# Deploy Commands

## One Rule

- `./deploy.sh local ...` 只使用 `docker-compose.dev.yaml`（development）
- `./deploy.sh remote ...` 只使用 `docker-compose.prod.yaml`（docker/production）

## Usage

```bash
./deploy.sh <target> [action]
```

## Targets

- `local`: 本地容器运行（development）
- `remote`: 远程服务器部署（production）
- `help`: 显示帮助

## Actions

- `init`: 首次部署，启动 `backend + mysql + myredis`
- `update`: 仅更新 backend（`remote` 默认）
- `restart`: 重启 backend
- `status`: 查看状态
- `logs`: 查看 backend 日志（最近 200 行）
- `down`: 仅停止 backend，不停止 mysql/myredis

## Env Responsibilities

- `backend/.env`: 本地开发与 local 容器（development）
- `backend/.env.prod`: remote 容器（production）
- `backend/.env-redis`: redis 参数
- `backend/.env-mysql`: mysql 参数

## Common Commands

```bash
# 本地首次（development compose）
./deploy.sh local

# 本地更新后端
./deploy.sh local update

# 远程首次（production compose）
cp deploy/remote.env.example deploy/remote.env
# 填写 REMOTE_HOST / REMOTE_USER / REMOTE_BACKEND_DIR
./deploy.sh remote init

# 远程更新后端
./deploy.sh remote update
```
