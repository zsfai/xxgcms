# xxg-cms — Agent Instructions

> 小西瓜 CMS monorepo。说明用中文，命令/路径/标识符保持英文原文。

## Project Overview

三件套 monorepo：

| Directory | Role | Detail |
|-----------|------|--------|
| `admin-backend/` | Admin REST API | Django 4.2 + PyMySQL，无 ORM |
| `admin-frontend/` | Admin SPA | React 18 + Vite 6 + shadcn/ui |
| `website/` | Public site | Django SSR，多站点模板 |

- **Runtime**: Python 3.12+, MySQL 8.0+, Node.js (frontend dev)
- **Production deploy**: Docker Compose — MySQL 8 + uWSGI + Nginx (`docker compose up -d --build`)
- **No automated test suite** — verify via Django check + manual integration
- **Bootstrap center**: `admin-backend setup` generates `.env`, initializes DB, creates admin, syncs `website/.env`

Sub-project docs (read before editing that area):

- [admin-backend/AGENTS.md](admin-backend/AGENTS.md)
- [admin-frontend/AGENTS.md](admin-frontend/AGENTS.md)
- [website/AGENTS.md](website/AGENTS.md)

## Data Layer

- **System DB** `xxgcms`: users, sites, AI config (`ai_*` tables)
- **Per-site CMS DB** (`db_x_*`): processed content — `article`, `cate`, `keyword`, etc.
- **Source DB** (`db_*`): read-only legacy imports; admin mostly writes to `db_x_*`

## Port Conventions

### Local Development

| Service | Port | Notes |
|---------|------|-------|
| `admin-frontend` | `8080` | Vite dev, proxies `/api` and `/media` → `:8000` |
| `admin-backend` | `8000` | Django runserver default |
| `website` | `8088` | Django runserver default |

### Docker Production (`docker compose`)

**三部分工程镜像（与 monorepo 目录一一对应）：**

| 工程目录 | 类型 | Compose 服务 | Image |
|----------|------|--------------|-------|
| `admin-backend/` | Python (Django + uWSGI) | `backend` | `xxgcms/admin-backend:latest` |
| `admin-frontend/` | 前端静态 (React build) | `admin-frontend` | `xxgcms/admin-frontend:latest` |
| `website/` | Python (Django + uWSGI) | `website` | `xxgcms/website:latest` |

**基础设施（非应用工程）：**

| Service | Image | Notes |
|---------|-------|-------|
| `mysql` | `xxgcms/mysql:latest` | Private MySQL 8.0 (not shared `mysql:8.0`) |
| `nginx` | `xxgcms/nginx:latest` | Private gateway — reverse proxy only |

Full stack: `docker compose up -d --build` (default `XXGCMS_ENABLE_WEBSITE=1`)

Offline bundle exports **exactly 5** image tars, all under `xxgcms/*`: 3 app images + `xxgcms/nginx` + `xxgcms/mysql`. Containers, network (`xxgcms-net`), and volumes use `xxgcms_*` names for isolation.

## Docker Deploy

```bash
cp .env.docker.example .env
docker compose up -d --build
docker compose exec backend cat /app/.credentials
```

Optional: set `XXGCMS_ENABLE_WEBSITE=0` in `.env` to disable `/` → website proxy (admin-only gateway mode).

Services: `mysql`, `backend`, `admin-frontend`, `website`, `nginx`. Volumes: `mysql_data`, `media_data`, `config_data`.

See [docker-compose.yml](docker-compose.yml), [docker/](docker/).

### Offline / Air-Gapped Deploy

On a **connected Linux machine**, build the bundle:

```bash
./docker/offline/bundle.sh
```

Transfer `xxgcms-YYYYMMDD.tar.gz` to offline server, then:

```bash
tar xzf xxgcms-*.tar.gz && cd xxgcms && sudo ./install.sh
```

Uses [docker-compose.offline.yml](docker-compose.offline.yml) with `pull_policy: never` — no network required.

## First-Time Setup (Local Dev)

```bash
cd admin-backend
chmod +x scripts/xxgcms.sh scripts/start.sh
./scripts/xxgcms.sh install
./scripts/xxgcms.sh setup
./scripts/xxgcms.sh start
```

```bash
cd admin-frontend
npm install
npm run dev
```

```bash
cd website
chmod +x scripts/website.sh scripts/start.sh
./scripts/website.sh start
```

Admin credentials: `./scripts/xxgcms.sh credentials` or `admin-backend/.credentials`.

## Cross-Cutting Conventions

### Multi-Site Context

- Frontend stores current site in `sessionStorage.domain` (site `name`)
- Site-scoped API calls inject `domain` via `xData()` in `admin-frontend/src/api/service.ts`
- Backend also accepts header `HTTP_DOMAIN`
- Website resolves site by `HTTP_HOST` (must match `site.name`, **including port**, e.g. `localhost:8088`)

### Authentication

- Header: `Auth-Key` (frontend sends lowercase `auth-key`)
- Token via `itsdangerous`, expires per `XXGCMS_TOKEN_EXPIRES`
- Protected endpoints: `@csrf_exempt` + `@perm(code=None)` — do not remove

### API Response Format

```json
{ "code": 0, "datas": [], "total_count": 0 }
{ "code": 10001, "message": "error text" }
{ "code": 403, "message": "token invalid" }
```

Frontend treats `code === 0` as success; `403` triggers re-login dialog.

### Commit Style

Use `feat:` / `fix:` prefix + Chinese description, e.g. `feat: 增加 AI 选题页面`.

## Security — DO NOT

- Commit `.env`, `.credentials`, `xxgcms_static_files/`, `admin-frontend/dist/`
- Hardcode API keys (`DEEPSEEK_API_KEY`, `DASHSCOPE_API_KEY`, etc.) — use `.env`
- Remove `@perm` from protected endpoints
- Expose secrets in logs or AGENTS.md examples

## Definition of Done

Before marking a task complete, verify:

- [ ] Schema changes → update `admin-backend/sql/` and note if `sync_db` is required
- [ ] New API → mapper + service + controller + `apps/api/urls.py` all present
- [ ] New frontend page → Page component + router + Sidebar (if needed) + `service.ts`
- [ ] Backend + frontend can start locally (or Docker stack if deployment-related)
- [ ] Docker changes → update `docker-compose.yml` / `docker/` and verify `docker compose up --build`
- [ ] No unrelated refactoring bundled in the same change

## Further Reading

| Doc | Purpose |
|-----|---------|
| [README.md](README.md) | Human quick-start |
| [admin-backend/readme.md](admin-backend/readme.md) | Backend shell commands, DB ops |
| [admin-frontend/readme.md](admin-frontend/readme.md) | Frontend stack, routes |
| [website/readme.md](website/readme.md) | Public site setup, domain rules |
| `docs/superpowers/specs/2026-06-20-ai-article-generation-design.md` | AI feature design (local) |
