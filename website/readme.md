# 网站前台

Python 3.12+ / Django 4.2 LTS / MySQL 8.0+

## 快速开始

先完成 `admin-backend` 的 `./scripts/xxgcms.sh setup`，再启动前台：

```bash
chmod +x scripts/website.sh scripts/start.sh
./scripts/website.sh install    # 首次：创建 venv + 安装依赖
./scripts/website.sh start        # 启动（默认 0.0.0.0:8088）
```

或最短路径：

```bash
./scripts/start.sh
```

### Shell 命令一览

| 命令 | 说明 |
|------|------|
| `./scripts/website.sh install` | 创建 `.venv` 并 `pip install` |
| `./scripts/website.sh init-env` | 生成/补全 `.env` |
| `./scripts/website.sh start [地址]` | 开发模式启动（默认 `0.0.0.0:8088`） |
| `./scripts/website.sh prod-start [地址]` | 生产配置启动 |
| `./scripts/website.sh check` | Django 检查 |

也可手动启动：

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

## 依赖说明

仅保留前台实际使用的库：

| 包 | 用途 |
|----|------|
| Django | Web 框架 |
| PyMySQL | 连接 MySQL |
| arrow | 页面日期时间格式化 |

## 配置

参见 `.env.example`。关键变量：

| 变量 | 说明 |
|------|------|
| `WEBSITE_SECRET_KEY` | Django 密钥（前台） |
| `XXGCMS_DB_*` | 与后台共用的系统库连接 |
| `WEBSITE_MEDIA_URL` | 媒体文件 URL 前缀 |
| `WEBSITE_ALLOWED_HOSTS` | 生产环境允许的域名（逗号分隔） |
| `WEBSITE_LOG_DIR` | 生产环境日志目录 |

生产环境使用 `apps.settings.prod`（`wsgi.py` 默认）。

## 站点与域名

系统库 `site.name` 需与访问时的 `HTTP_HOST` 一致（含端口，例如 `localhost:8088`），前台据此选择 CMS 数据库。若同时存在 `localhost` 与 `localhost:8088` 两个站点，带端口访问时会优先匹配带端口的站点名。
