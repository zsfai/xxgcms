#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${CONFIG_DIR:-/data/config}"
INIT_MARKER="${CONFIG_DIR}/.initialized"
MAX_TRIES="${CONFIG_WAIT_TRIES:-90}"
SLEEP_SEC="${CONFIG_WAIT_SLEEP:-2}"

export HOST="${XXGCMS_DB_HOST:-mysql}"
export PORT="${XXGCMS_DB_PORT:-3306}"
export USER="${XXGCMS_DB_USER:-xxgcms}"
export PASSWORD="${XXGCMS_DB_PASSWORD:-}"
export MYSQL_WAIT_SLEEP="${MYSQL_WAIT_SLEEP:-1}"
export MYSQL_WAIT_TRIES="${MYSQL_WAIT_TRIES:-45}"

/docker/scripts/wait-for-mysql.sh

echo "[website] Waiting for backend initialization ..."
for ((i = 1; i <= MAX_TRIES; i++)); do
  if [[ -f "${INIT_MARKER}" ]]; then
    break
  fi
  if [[ "${i}" -eq "${MAX_TRIES}" ]]; then
    echo "[website] Backend config not ready after ${MAX_TRIES} attempts." >&2
    exit 1
  fi
  sleep "${SLEEP_SEC}"
done

/docker/scripts/sync-env-from-config.sh website

mkdir -p /var/log/xxgcms
cd /app
export DJANGO_SETTINGS_MODULE=apps.settings.prod

echo "[website] Starting uWSGI ..."
if ! command -v uwsgi >/dev/null 2>&1; then
  echo "[website] ERROR: uwsgi not found. Rebuild website image after adding uwsgi to requirements.txt." >&2
  exit 1
fi
exec uwsgi --ini /docker/uwsgi/website.ini
