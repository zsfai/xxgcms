#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${CONFIG_DIR:-/data/config}"
MEDIA_DIR="${XXGCMS_MEDIA_DIR:-/data/media}"
INIT_MARKER="${CONFIG_DIR}/.initialized"

mkdir -p "${MEDIA_DIR}" /var/log/xxgcms "${CONFIG_DIR}" "${CONFIG_DIR}/nginx/sites" "${CONFIG_DIR}/certs"
cd /app

export DJANGO_SETTINGS_MODULE=apps.settings.prod
export HOST="${XXGCMS_DB_HOST:-mysql}"
export PORT="${XXGCMS_DB_PORT:-3306}"
export USER="${XXGCMS_DB_USER:-xxgcms}"
export PASSWORD="${XXGCMS_DB_PASSWORD:-}"
export MYSQL_WAIT_SLEEP="${MYSQL_WAIT_SLEEP:-1}"
export MYSQL_WAIT_TRIES="${MYSQL_WAIT_TRIES:-45}"

/docker/scripts/wait-for-mysql.sh

if [[ -f "${INIT_MARKER}" ]]; then
  echo "[backend] Restoring config from ${CONFIG_DIR} ..."
  /docker/scripts/sync-env-from-config.sh backend
else
  echo "[backend] First run — initializing environment and database ..."
  /docker/scripts/prepare-env-from-compose.sh backend
  python manage.py setup
fi

/docker/scripts/ensure-docker-db-host.sh

echo "[backend] Ensuring site root_path under MEDIA_ROOT ..."
python manage.py fix_site_paths

echo "[backend] Syncing database schema (xxgcms) ..."
python manage.py sync_db --xxgcms

echo "[backend] Refreshing deployment credentials ..."
python manage.py refresh_credentials
if [[ -f /app/.credentials ]]; then
  cp /app/.credentials "${CONFIG_DIR}/.credentials"
else
  echo "[backend] WARN: .credentials 未生成，请检查 .env 是否已配置" >&2
fi

if [[ ! -f "${INIT_MARKER}" ]]; then
  /docker/scripts/persist-env-to-config.sh
  echo ""
  echo "=========================================="
  echo " 【重要】请立即复制并妥善保存下方凭据！"
  echo " 含管理后台、MySQL 等密码；容器重建后无法找回。"
  echo "=========================================="
  echo "[backend] Setup complete. Deployment credentials:"
  if [[ -f /app/.credentials ]]; then
    cat /app/.credentials
  fi
  echo ""
  echo "=========================================="
  echo " 请务必将上述凭据保存到安全位置后再继续。"
  echo "=========================================="
fi

echo "[backend] Starting uWSGI ..."
exec uwsgi --ini /docker/uwsgi/backend.ini
