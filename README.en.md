<div align="center">

# The-Reverie-Loft

### A Modern, Feature-Rich Social Platform

**An open-source social system built with Vue3 + Flask**

A full-stack social platform template with real-time communication and graceful dependency degradation, designed for clean engineering and practical deployment.

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI](https://github.com/nizhensh-i/The-Reverie-Loft/actions/workflows/python-tests.yml/badge.svg)](https://github.com/nizhensh-i/The-Reverie-Loft/actions/workflows/python-tests.yml)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-4FC08D.svg)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1.svg)](https://www.mysql.com/)
[![Redis](https://img.shields.io/badge/Redis-7.x-DC382D.svg)](https://redis.io/)

[English](README.en.md) | [中文](README.md)

[Overview](#-project-overview) • [Quick Start](#-quick-start) • [Configuration](#-third-party-service-configuration-guide) • [Deployment](#-deployment-guide) • [FAQ](#-faq)

</div>

---

## ⭐ Highlights

- Layered backend with Clean Architecture and clear dependency injection
- Complete real-time communication: split HTTP API and Socket.IO services
- Graceful degradation: app still runs without Redis / Mail / Storage / OAuth
- One-command dev start: `start.sh` for quick local bootstrapping
- Production deployment path: Docker Compose + Nginx reverse proxy

## 🚩 Quick Overview

- Full-stack social platform template based on Vue 3 + Flask (feed/interaction/realtime chat)
- Clean backend layering + dependency injection; split HTTP and Socket.IO services
- Optional dependencies (Redis/Mail/Storage/OAuth) degrade automatically when missing
- Startup flow: MySQL -> `./init.sh` (idempotent) -> `./start.sh`
- Default ports: `5172` (frontend) / `4289` (API) / `4290` (Socket.IO)

## 📚 API Entry Points

- Reference routes: `backend/app/api`, `backend/app/auth`

## 🎬 Demo

- Online preview: 191718.com
- Note: no prebuilt demo account. You can register your own account or browse as a guest.

## 🖼️ Preview

<img src="docs/preview_1.jpg" alt="Loft Preview 1" style="max-width: 800px; width: 100%;" />

---

<img src="docs/preview_2.jpg" alt="Loft Preview 2" style="max-width: 800px; width: 100%;" />

---

## 📖 Project Overview

The-Reverie-Loft is an open-source full-stack social platform built on a modern tech stack. The backend already applies clean layered architecture (domain / services / infrastructure) and graceful infrastructure capability degradation.

### ✨ Core Features

- 👤 **User system**: registration, login, profile management
- 📱 **Social login**: GitHub, Google, QQ, Weibo OAuth
- 💬 **Real-time chat**: instant messaging powered by WebSocket
- 📝 **Content publishing**: post text and images
- 👍 **Interactions**: likes, comments, follows
- 🔐 **Access control**: JWT-based authentication
- 📊 **Analytics**: operation logs and user behavior stats
- 🎨 **Responsive design**: works on desktop and mobile

### 🛠️ Tech Stack

| Layer | Tech | Notes |
|------|------|------|
| **Frontend** | Vue 3 + Vite | Modern build tooling and reactive framework |
| | Element Plus | UI component library |
| | Vue Router | Client-side routing |
| | Pinia | State management |
| **Backend** | Flask 3.x | Python web framework |
| | SQLAlchemy | ORM database access |
| | Flask-JWT-Extended | JWT auth |
| | Flask-SocketIO | WebSocket real-time communication |
| | dependency-injector | Dependency injection container |
| **Database** | MySQL 8.x | Relational storage (core requirement) |
| | Redis 7.x | Cache/rate-limit/message capability (optional with degradation) |
| **Deployment** | Shell scripts + Docker Compose | `deploy.sh` orchestrates local/remote deployment |
| | Nginx | Optional reverse proxy and HTTPS termination |

### 🧠 Capability Degradation Design

Loft implements capability detection and degradation strategies at the infrastructure layer:

- Redis unavailable: cache/rate limit/realtime messaging/async tasks enter degraded mode (for example Celery falls back to in-memory eager execution)
- Mail not configured: mail service degrades, verification emails are unavailable, core flows still run
- Qiniu not configured: upload and signed access degrade; registered users fall back to frontend default avatars and persist avatar names
- OAuth not configured: social login entries are disabled without impacting username/password auth

---

## 🚀 Quick Start

> Script-based startup (`start.sh`) is the default recommendation with minimal external dependencies. Docker is optional.

### Prerequisites (non-Docker primary path)

- Python >= 3.12
- Node.js 18+ (recommended), package manager: `npm`
- MySQL 8.x

### Step 0: Prepare MySQL Database

```sql
CREATE DATABASE flasky CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

> If you use another database name, keep `DEV_DATABASE_URL` in `backend/.env` consistent.

### ⚡ Start in 3 Steps (Recommended)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/nizhensh-i/The-Reverie-Loft && cd The-Reverie-Loft
```

#### Step 2: One-Command Environment Initialization (Recommended)

```bash
./init.sh
```

`init.sh` will:
- create a Python virtual environment and install dependencies
- generate `backend/.env` (with random secrets)
- run database migration via `flask deploy`
- install frontend dependencies and generate `frontend/.env.development`

> Notes: `backend/.env` is for development settings, while production uses `backend/.env.prod`.
> If `DEV_DATABASE_URL` is empty, `init.sh` automatically writes `sqlite:///dev.db` as a fallback so first-time setup can finish.
> Switch to MySQL as soon as possible: sqlite is only for quick local trial, not for concurrency validation, performance evaluation, or production.

**Minimum required config (core, manual mode)**

```bash
# backend/.env minimal example
SECRET_KEY=replace-with-random-string
JWT_SECRET_KEY=replace-with-random-string
DEV_DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/flasky?charset=utf8mb4
```

Optional: generate random secrets with:

```bash
openssl rand -hex 32
```

#### Step 3: Start Services

```bash
./start.sh
```

Default development endpoints after startup:
- Frontend: `http://localhost:5172`
- Backend HTTP: `http://localhost:4289`
- Backend Socket.IO: `http://localhost:4290`

Custom ports (via env vars):
- Frontend: `VITE_PORT` (`frontend/.env.development`)
- Backend HTTP: `FLASK_RUN_PORT` (`backend/.env`)
- Backend Socket.IO: `SOCKETIO_RUN_PORT` (`backend/.env`, default `4290`)

---

## 🔧 Third-Party Service Configuration Guide

The project uses an "enable when available, degrade when missing" capability model. Configure in this priority:

### 1) Core Required (strongly recommended not to skip)

| **Config** | Location | Notes |
|------|------|------|
| **`SECRET_KEY` / `JWT_SECRET_KEY`** | `backend/.env` | Flask/JWT base security secrets |
| **`DEV_DATABASE_URL` (dev) or `DATABASE_URL` (prod)** | `backend/.env` / `backend/.env.prod` | MySQL connection |

### 2) Optional with Degradation (app still starts, feature limits apply)

| Capability | **Key Config** | Impact if Missing |
|------|------|------|
| Redis | **`DEV_REDIS_URL` / `REDIS_URL` / `REDIS_HOST`** | Cache, rate limit, realtime messaging, async tasks enter degraded mode |
| Mail | **`MAIL_USERNAME` / `MAIL_PASSWORD`** | Email verification codes are printed to `backend/logg/celery.log`; notifications unavailable (system still runs) |
| Qiniu object storage | **`QINIU_ACCESS_KEY` / `QINIU_SECRET_KEY` / `QINIU_BUCKET_NAME` / `QINIU_DOMAIN`** | Image upload and signed access unavailable; registration avatar falls back to frontend static default avatar (avatar name is persisted) |
| OAuth login | **Platform `*_CLIENT_ID` / `*_CLIENT_SECRET`** | Corresponding social login entries unavailable |

### 3) Example Config

```bash
# MySQL (development)
DEV_DATABASE_URL=mysql+pymysql://user:password@127.0.0.1:3306/flasky?charset=utf8mb4

# Redis (optional)
DEV_REDIS_URL=redis://:1234@127.0.0.1:6379/0

# Qiniu (optional)
QINIU_DOMAIN=https://your-bucket-domain.example.com
```

> Security note: never commit real secrets. Example values are for demonstration only.

---

## 🧱 Project Structure

See [backend/README.md](backend/README.md) for backend layering and dependency injection details.

```text
The-Reverie-Loft/
├── frontend/                    # Vue3 + Vite frontend
│   ├── src/
│   │   ├── api/                # request wrappers and API definitions
│   │   ├── stores/             # Pinia stores
│   │   ├── views/              # page views
│   │   └── router/             # routing
│   └── .env.development.example
│   └── .env.production.example
├── backend/                     # Flask backend
│   ├── app/
│   │   ├── domain/             # domain models/strategies/port protocols
│   │   ├── services/           # application services (use-case orchestration)
│   │   ├── infrastructure/     # DB/Redis/OAuth/Storage/Adapter implementations
│   │   ├── api/                # /api/v1 routes
│   │   ├── auth/               # /auth routes
│   │   └── container.py        # DI container wiring
│   ├── migrations/             # Alembic migration scripts
│   ├── flasky.py               # HTTP entry
│   └── flasky_socketio.py      # Socket.IO entry
│   └── .env.example
│   └── .env.prod.example
├── deploy/                      # local/remote deployment templates
├── docs/                        # docs and sample configs
├── start.sh                     # one-command non-Docker startup script
└── deploy.sh                    # unified Docker deployment entry
```

### Architecture and Data Flow (Simple Diagram)

```mermaid
flowchart LR
  A[Vue3 Frontend] -->|HTTP /api| B[Flask HTTP :4289]
  A -->|WebSocket /socket.io| C[Flask SocketIO :4290]

  B --> D[(MySQL)]
  B --> E[(Redis Optional)]
  C --> E

  B --> F[Mail Adapter Optional]
  B --> G[Qiniu Storage Optional]
  B --> H[OAuth Providers Optional]

  subgraph Backend Clean Layers
    I[Domain] --> J[Services]
    J --> K[Infrastructure Adapters]
  end

  B --> I
  C --> I
```

---

## 📦 Deployment Guide

### Option A: Built-in Deployment Script (Recommended)

Unified entry:

```bash
./deploy.sh <target> [action]
```

- `target=local`: run containers locally with `backend/docker-compose.dev.yaml`
- `target=remote`: deploy to remote server with `backend/docker-compose.prod.yaml`

Production template: `backend/.env.prod.example` (copy to `backend/.env.prod`)

Compose service names (in backend compose):
- `backend`
- `mysql`
- `myredis`

Common commands:

```bash
# first local setup
./deploy.sh local init

# update local backend
./deploy.sh local update

# first remote setup
cp deploy/remote.env.example deploy/remote.env
# fill REMOTE_HOST / REMOTE_USER / REMOTE_BACKEND_DIR
./deploy.sh remote init

# remote update
./deploy.sh remote update
```

See [docs/deploy.md](docs/deploy.md) for details.

### Option B: Optional Nginx Reverse Proxy (Common in Production)

README includes only a minimal working config. For a full sample, see [docs/nginx.conf.example](docs/nginx.conf.example).

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

## 🗄️ Database Initialization and Migration

### Fast Path (Recommended)

```bash
cd backend
flask deploy
```

`flask deploy` will:
- migrate to latest revision (`upgrade`)
- fallback to `create_all + stamp head` when migration history is incomplete and core tables are missing
- initialize roles/permissions and self-follow relationships

If you initially used sqlite fallback (`sqlite:///dev.db`), run migration again after switching to MySQL:

```bash
cd backend
flask deploy
```

### Manual Migration (Common in Development)

```bash
cd backend
export FLASK_APP=flasky.py

# generate migration script
flask db migrate -m "your migration message"

# apply migration
flask db upgrade

# rollback one step (optional)
flask db downgrade -1
```

### Seed Data

- Default roles/permissions/self-follow are initialized automatically in `flask deploy`
- Demo business data can be generated via admin endpoint: `GET /api/v1/users/generate_posts`

---

## 🔐 Security and Production Notes

- Do not commit real secrets (`.env`, `deploy/*.env`, cloud AK/SK)
- Replace `SECRET_KEY` and `JWT_SECRET_KEY` in production
- Restrict CORS to real domains; do not keep it fully open
- When Socket.IO runs behind Nginx, include `Upgrade/Connection` headers and increase read/write timeouts
- Redis degradation keeps service available, but affects rate-limit accuracy, cache hit rate, and async throughput
- Enable log rotation and error alerting before going live

---

## 🗺️ Roadmap

- [x] Core social features (post/comment/like/follow)
- [x] OAuth login
- [x] WebSocket real-time chat
- [ ] Notification center enhancements (rules/push)
- [ ] Mobile PWA experience
- [ ] Better operations/admin dashboard

---

## ❓ FAQ

### 1. ❌ Backend cannot connect to MySQL after `start.sh`

**Checklist:**

1. Verify MySQL connectivity (local or remote)
2. Verify `DEV_DATABASE_URL` in `backend/.env`
3. Confirm user permissions for the target database

**Example:**

```bash
mysql -h 127.0.0.1 -P 3306 -u your_user -p
```

### 2. ⚠️ Redis is not installed, can the project still run?

Yes. Redis is optional in this project and will enter degraded mode.  
Main impact: cache/rate-limit/some realtime and async capabilities are limited.

### 3. ❌ Qiniu upload returns 401 / `bad token`

Check first:
- `QINIU_ACCESS_KEY` / `QINIU_SECRET_KEY`
- `QINIU_BUCKET_NAME` / `QINIU_DOMAIN` matches Qiniu console settings
- no extra spaces in `.env` variables

### 4. ❌ OAuth callback fails (`redirect_uri_mismatch`)

Ensure both sides are consistent:
- callback URL configured in OAuth provider
- actual backend callback URL (`/api/auth/oauth/callback/<provider>`)

In production, always use the real domain and HTTPS.

### 5. ❌ WebSocket returns 502 behind Nginx

Confirm:
- Nginx has `/socket.io/` proxy config and `Upgrade/Connection` headers
- backend Socket.IO service listens on `4290`
- firewall/security groups allow 80/443 (or your configured ports)

### 6. 🔍 How to quickly verify `.env` is loaded?

```bash
cd backend
python -c "from app.infrastructure.config.runtime_env import load_env; load_env(); import os; print('FLASK_CONFIG=', os.getenv('FLASK_CONFIG')); print('DEV_DATABASE_URL set=', bool(os.getenv('DEV_DATABASE_URL')))"
```

If output shows `DEV_DATABASE_URL set= True`, `.env` has been loaded into process environment.

---

## 🤝 Contributing

Issues and Pull Requests are welcome.

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Local Development Commands

```bash
# backend
cd backend
pip install -r requirements/dev.txt
python flasky.py

# backend tests
pytest tests_api

# frontend
cd ../frontend
npm install
npm run dev
npm run build

# repo-wide checks
cd ..
pre-commit run --all-files
```

---

## 📄 License

This project is licensed under MIT - see [LICENSE](LICENSE) for details.

---

## 📞 Contact

- 📧 Maintainer: zmc_li@foxmail.com
- 🐛 Bug reports: [Open an Issue](https://github.com/nizhensh-i/The-Reverie-Loft/issues)

---

<div align="center">

**If this project helps you, a Star would be appreciated.**

Made with ❤️ by [nizhensh-i](https://github.com/nizhensh-i)

</div>
