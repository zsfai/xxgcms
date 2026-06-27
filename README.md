# 小西瓜CMS（xxgcms）

> **在使用本项目前，请阅读 [法律声明、使用条款与免责协议](TERMS.md)**（简要摘要见 [DISCLAIMER.md](DISCLAIMER.md)）。

## Docker 一键部署（推荐）

需安装 [Docker](https://docs.docker.com/get-docker/) 与 Docker Compose。

### 全栈一键部署

```bash
cp .env.docker.example .env
docker compose up -d --build
```

| 镜像 | 工程 | 说明 |
|------|------|------|
| `xxgcms/admin-backend` | `admin-backend/` | Django 管理 API（uWSGI） |
| `xxgcms/admin-frontend` | `admin-frontend/` | React 管理后台静态资源 |
| `xxgcms/website` | `website/` | Django 站点前台（uWSGI） |
| `xxgcms/nginx` | — | 私有网关（:80 入口，与其他 nginx 镜像隔离） |
| `xxgcms/mysql` | — | 私有 MySQL 8.0（2C4G 调优，应用账号 `xxgcms` + 随机密码） |

| 地址 | 说明 |
|------|------|
| http://localhost/ | 站点前台 |
| http://localhost/back-x/ | 管理后台 |
| http://localhost/api/ | 后台 API |

查看管理员凭据：

```bash
docker compose exec backend cat /app/.credentials
```

常用命令：

```bash
docker compose logs -f backend    # 查看后台日志
docker compose down             # 停止（数据保留在卷中）
docker compose down -v          # 停止并清除数据库与配置（慎用）
```

技术栈：MySQL 8 + Python uWSGI (Django) + Nginx + React 静态构建。

## 离线部署（无互联网环境）

在有网络的 Linux 机器上**一次性打包**全部镜像（MySQL、Python、Nginx 等），拷贝到离线服务器即可安装。

### 远程制作（推荐：本地 Windows + Ubuntu 构建机）

无需在本地安装 Docker，一键打包上传并在 Ubuntu 上构建：

```bash
cp scripts/offline-pack/deploy.env.example scripts/offline-pack/deploy.env
# 编辑 deploy.env：服务器 IP、用户名；密码填 REMOTE_PASSWORD（或留空用 SSH 密钥）
chmod +x scripts/build-offline-remote.sh scripts/offline-pack/*.sh
./scripts/build-offline-remote.sh
```

详见 [scripts/offline-pack/README.md](scripts/offline-pack/README.md)。

### 本地直接制作（Linux 且有 Docker）

```bash
chmod +x make-offline-bundle.sh docker/offline/bundle.sh
./make-offline-bundle.sh
```

默认打包**全栈五镜像**（约 2GB+）：

| 文件 | 内容 |
|------|------|
| `images/xxgcms-mysql.tar` | 私有 MySQL 8.0 |
| `images/xxgcms-admin-backend.tar` | admin-backend 管理 API |
| `images/xxgcms-admin-frontend.tar` | admin-frontend React 管理后台 |
| `images/xxgcms-website.tar` | website 站点前台 |
| `images/xxgcms-nginx.tar` | Nginx 统一网关 |

```bash
sudo ./install.sh
```

详细说明见 [docker/offline/README-OFFLINE.md](docker/offline/README-OFFLINE.md)。

## 本地开发启动

在 `admin-backend` 目录：

```bash
chmod +x scripts/xxgcms.sh scripts/start.sh
./scripts/xxgcms.sh install    # 首次：venv + 依赖
./scripts/xxgcms.sh setup      # 首次：配置 + 数据库 + 管理员
./scripts/xxgcms.sh start      # 启动（无 .env 时会自动 setup）
```

最短启动：

```bash
./admin-backend/scripts/start.sh          # 后台 API
./website/scripts/start.sh                # 站点前台（默认 8088）
```

管理前端开发：

```bash
cd admin-frontend && npm install && npm run dev   # http://localhost:8080
```

查看管理员账号：`./scripts/xxgcms.sh credentials`

## setup 会自动完成

1. 生成 `admin-backend/.env` 与 `website/.env`（随机密钥、数据库密码等）
2. 初始化 MySQL 8.0 库（`xxgcms` + CMS 站点库）
3. 创建管理员账号，凭据写入 `admin-backend/.credentials`

## 子项目

| 目录 | 说明 |
|------|------|
| `admin-backend/` | 后台 API，详见 [admin-backend/readme.md](admin-backend/readme.md) |
| `admin-frontend/` | 后台前端 |
| `website/` | 站点前台 |

## 敏感配置说明

- 所有密钥、密码通过 `.env` 配置，**勿提交** `.env`、`.credentials`
- 敏感项标记为 `__AUTO__` 的字段会在首次 `setup` / `init_env` 时自动随机生成
- 前台与后台共用 `XXGCMS_DB_*` 数据库连接配置（由 setup 自动同步）
- Docker 部署使用根目录 `.env`（从 `.env.docker.example` 复制）

## 法律声明与免责

使用本软件即表示您同意 [法律声明、使用条款与免责协议](TERMS.md)（版本 1.0，生效日期 2026年6月27日）。简要说明见 [DISCLAIMER.md](DISCLAIMER.md)。
