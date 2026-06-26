# 小西瓜CMS 后端

## 环境

- Python 3.12+
- MySQL 8.0+

## 快速开始（推荐：Shell 脚本）

```bash
chmod +x scripts/xxgcms.sh scripts/start.sh
./scripts/xxgcms.sh install    # 创建 venv + 安装依赖
./scripts/xxgcms.sh setup      # 一键初始化（.env + 数据库 + 管理员）
./scripts/xxgcms.sh start      # 启动服务（无 .env 时会自动 setup）
```

或最短路径：

```bash
./scripts/start.sh
```

管理员凭据：`./scripts/xxgcms.sh credentials` 或查看 `.credentials`。

### Shell 命令一览

| 命令 | 说明 |
|------|------|
| `./scripts/xxgcms.sh install` | 创建 `.venv` 并 `pip install` |
| `./scripts/xxgcms.sh setup` | 生成配置 + 初始化库 + 创建管理员 |
| `./scripts/xxgcms.sh init-env` | 仅生成/补全 `.env` |
| `./scripts/xxgcms.sh init-db` | 仅初始化数据库 |
| `./scripts/xxgcms.sh start [地址]` | 开发模式启动（默认 `0.0.0.0:8000`） |
| `./scripts/xxgcms.sh prod-start [地址]` | 生产配置启动 |
| `./scripts/xxgcms.sh user <名> <密码>` | 创建/重置用户 |
| `./scripts/xxgcms.sh sync-db` | 增量同步表结构 |
| `./scripts/xxgcms.sh upgrade-mysql8` | 5.7→8.0 库结构升级（零日期、字符集） |
| `./scripts/xxgcms.sh check` | Django 检查 |
| `./scripts/xxgcms.sh credentials` | 查看管理员凭据 |

其他 Python 工具脚本见 `scripts/` 目录（`create_user.py`、`backup_sql.py`、`task_manage.py`）。

### 分步命令

| 命令 | 说明 |
|------|------|
| `python manage.py init_env` | 仅生成/补全 `.env` 敏感配置（含同步 website） |
| `python manage.py init_db` | 初始化数据库并创建管理员 |
| `python manage.py setup` | 上述全部 + 创建管理员 |

### 数据库初始化参数

| 命令 | 说明 |
|------|------|
| `python manage.py init_db` | 初始化 `xxgcms` + CMS 库，并写入测试站点 |
| `python manage.py init_db --xxgcms` | 仅执行 `sql/xxgcms.sql` |
| `python manage.py init_db --cms` | 仅执行 `sql/cmsdb.sql` |
| `python manage.py init_db --cms-db mysite --site-name demo` | 指定 CMS 库名与站点标识 |

### 增量同步结构

```bash
python manage.py sync_db --dry-run
python manage.py sync_db
python manage.py sync_db --all-sites
```

### MySQL 8.0 升级（从 5.7 迁移）

安装 MySQL 8.0 并恢复数据后，执行结构兼容升级：

```bash
python manage.py upgrade_mysql8 --dry-run    # 预览
python manage.py upgrade_mysql8              # 系统库 + 默认 CMS 库
python manage.py upgrade_mysql8 --all-sites  # 全部站点 CMS 库
python manage.py upgrade_mysql8 --convert-tables  # 可选：转换全部表 collation
```

或：

```bash
./scripts/xxgcms.sh upgrade-mysql8 --dry-run
./scripts/xxgcms.sh upgrade-mysql8 --all-sites
```

MySQL 8.0 默认认证插件为 `caching_sha2_password`，PyMySQL 1.1+ 已支持。若仍使用 `mysql_native_password` 亦可。

## 配置

参见 `.env.example`。敏感项使用 `__AUTO__`，首次 `setup` 时自动随机生成。

| 变量 | 说明 |
|------|------|
| `XXGCMS_SECRET_KEY` | Django 密钥（后台） |
| `XXGCMS_AUTH_SALT` | Token 盐值 |
| `XXGCMS_DB_PASSWORD` | 系统库密码 |
| `XXGCMS_ADMIN_USER` / `XXGCMS_ADMIN_PASSWORD` | 初始管理员 |
| `DJANGO_SETTINGS_MODULE` | `apps.settings.dev` 或 `apps.settings.prod` |

## 架构

- **配置**：`apps/settings/{base,dev,prod}.py`
- **环境引导**：`apps/api/utils/env_bootstrap.py`
- **运维脚本**：`scripts/`

## 技术栈

- Django 4.2 LTS + PyMySQL + jieba
