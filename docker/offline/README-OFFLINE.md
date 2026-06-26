# xxg-cms 离线安装包说明

本目录包含运行环境镜像，可在**无互联网**的 Linux 服务器上安装。

## 工程与镜像对齐（勿多勿少）

| 工程目录 | 类型 | Docker 镜像 | tar 包 | 镜像内包含 |
|----------|------|-------------|--------|------------|
| `admin-backend/` | **纯 Python** (Django + uWSGI) | `xxgcms/admin-backend:latest` | `xxgcms-admin-backend.tar` | 仅 `admin-backend/` 代码与依赖 |
| `admin-frontend/` | **纯前端** (React 静态资源) | `xxgcms/admin-frontend:latest` | `xxgcms-admin-frontend.tar` | 仅 `npm run build` 后的 `/back-x/` 静态文件 |
| `website/` | **纯 Python** (Django + uWSGI) | `xxgcms/website:latest` | `xxgcms-website.tar` | 仅 `website/` 代码与依赖（含 `static/`） |
| — | 基础设施：网关 | `xxgcms/nginx:latest` | `xxgcms-nginx.tar` | 私有 Nginx 网关，**不与**系统 `nginx` 镜像共用 |
| — | 基础设施：数据库 | `xxgcms/mysql:latest` | `xxgcms-mysql.tar` | 私有 MySQL 8.0，**不与**公共 `mysql:8.0` 共用 |

离线包 `images/` 目录**恰好 5 个 tar**，均为 `xxgcms/*` 私有镜像，容器/网络/卷亦使用 `xxgcms-*` 命名，与机器上其他 Docker 栈隔离。

> 容器名: `xxgcms-mysql`、`xxgcms-nginx` 等；网络: `xxgcms-net`；数据卷: `xxgcms_mysql_data` 等。

> `admin-backend` 首次 setup 会用 `docker/templates/website.env.example` 生成 website 配置写入共享卷，**不把 website 应用打进 admin-backend 镜像**。

## 路由关系

```
:80 nginx (xxgcms/nginx)
  ├─ /back-x/  → admin-frontend (静态)
  ├─ /api/     → admin-backend  (uWSGI :8002)
  ├─ /static/  → nginx 静态目录（website/static）；缺失时回退 website uWSGI
  ├─ /media/   → 共享卷
  └─ /         → website        (uWSGI :8003)
```

## 安装

```bash
tar xzf xxgcms-YYYYMMDD.tar.gz
cd xxgcms
cp .env.docker.example .env
sudo ./install.sh
```

## 访问

| 地址 | 工程 |
|------|------|
| http://服务器IP/ | website |
| http://服务器IP/back-x/ | admin-frontend |
| http://服务器IP/api/ | admin-backend |
| http://服务器IP/media/ | 共享媒体卷 |

```bash
docker compose -f docker-compose.offline.yml exec backend python manage.py show_credentials
```

## 绑定域名与 HTTPS

1. 防火墙放行 **80、443**
2. DNS 将域名 A 记录指向服务器
3. 管理后台 → **站点管理** → 编辑站点 → **域名与证书**
4. 上传或粘贴 `fullchain.pem` + `privkey.pem`，保存后系统自动写入 Nginx 并热加载

升级旧版本后请先同步数据库结构：

```bash
docker compose -f docker-compose.offline.yml exec backend python manage.py sync_db --xxgcms
```

故障恢复（从数据库重建全部 Nginx 站点配置）：

```bash
docker compose -f docker-compose.offline.yml exec backend python manage.py sync_nginx
```

## 制作离线包（有网机器）

```bash
./make-offline-bundle.sh
```

**国内构建加速（已内置）：** Dockerfile 默认使用阿里云 apt、清华 pip、npmmirror npm。  
首次在 Ubuntu 构建机制作时，可额外执行一次 Docker Hub 加速：

```bash
sudo ./docker/offline/setup-docker-mirror-cn.sh
```

海外构建可关闭：`USE_CN_MIRROR=0 ./make-offline-bundle.sh`

## 服务器要求

- Linux x86_64，Docker 20.10+，Docker Compose v2（推荐）
- 磁盘 ≥ 4GB，**80 / 443** 端口可用
