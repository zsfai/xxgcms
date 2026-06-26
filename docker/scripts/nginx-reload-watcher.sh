#!/bin/sh
# 监视 reload.stamp，校验通过后热加载 Nginx
STAMP="/data/config/nginx/reload.stamp"
LAST=""
ERROR_LOG="/data/config/nginx/last-error.log"
RELOAD_LOG="/data/config/nginx/last-reload.log"

mkdir -p /data/config/nginx/sites

while true; do
  if [ -f "$STAMP" ]; then
    CUR=$(cat "$STAMP" 2>/dev/null || true)
    if [ "$CUR" != "$LAST" ]; then
      if nginx -t 2>"$ERROR_LOG"; then
        nginx -s reload 2>>"$ERROR_LOG" || true
        echo "reload ok $(date 2>/dev/null || echo '')" >> "$RELOAD_LOG"
      fi
      LAST="$CUR"
    fi
  fi
  sleep 2
done
