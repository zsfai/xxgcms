#!/usr/bin/env bash
# Docker Compose / 离线部署：应用库应连接服务名 mysql，而非 127.0.0.1
set -euo pipefail

export XXGCMS_DB_HOST=mysql

if [[ -f /app/.env ]]; then
  if grep -q '^XXGCMS_DB_HOST=' /app/.env; then
    sed -i 's/^XXGCMS_DB_HOST=.*/XXGCMS_DB_HOST=mysql/' /app/.env
  else
    echo 'XXGCMS_DB_HOST=mysql' >> /app/.env
  fi
fi

export HOST="${XXGCMS_DB_HOST}"
export PORT="${XXGCMS_DB_PORT:-3306}"
export USER="${XXGCMS_DB_USER:-xxgcms}"
