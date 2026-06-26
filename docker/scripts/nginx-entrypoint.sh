#!/usr/bin/env sh
set -eu

ENABLE_WEBSITE="${XXGCMS_ENABLE_WEBSITE:-0}"

mkdir -p /data/config/nginx/sites /data/config/certs

chmod +x /docker/scripts/nginx-reload-watcher.sh
/docker/scripts/nginx-reload-watcher.sh &

rm -f /etc/nginx/conf.d/default.conf

if [ "${ENABLE_WEBSITE}" = "1" ] || [ "${ENABLE_WEBSITE}" = "true" ] || [ "${ENABLE_WEBSITE}" = "yes" ]; then
  echo "[nginx] Website mode: default 80 + dynamic SSL sites"
  cp /etc/nginx/available/00-base.conf /etc/nginx/conf.d/00-base.conf
else
  echo "[nginx] Admin-only mode: /api/ + /back-x/"
  cp /etc/nginx/available/admin-base.conf /etc/nginx/conf.d/00-base.conf
fi

cp /etc/nginx/available/zz-sites-include.conf /etc/nginx/conf.d/zz-sites-include.conf

exec nginx -g 'daemon off;'
