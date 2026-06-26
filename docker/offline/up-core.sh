#!/usr/bin/env bash
# 仅用 docker 命令启动全栈（无需 docker compose）
# 用法: ./up-core.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT}"
# shellcheck source=access-urls.sh
source "${ROOT}/access-urls.sh"

if [[ ! -f .env ]]; then
  cp .env.docker.example .env
  echo "已从 .env.docker.example 创建 .env"
fi

if [[ -f docker/scripts/bootstrap-docker-env.sh ]]; then
  bash docker/scripts/bootstrap-docker-env.sh .env
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

export XXGCMS_ENABLE_WEBSITE=1

# Docker 离线部署：MySQL 服务名为 mysql
if grep -q '^XXGCMS_DB_HOST=' .env; then
  sed -i 's/^XXGCMS_DB_HOST=.*/XXGCMS_DB_HOST=mysql/' .env
else
  echo 'XXGCMS_DB_HOST=mysql' >> .env
fi
export XXGCMS_DB_HOST=mysql

NET="xxgcms-net"
MYSQL_VOL="xxgcms_mysql_data"
MEDIA_VOL="xxgcms_media_data"
CONFIG_VOL="xxgcms_config_data"

echo "[up-core] 创建网络与数据卷 ..."
docker network create "${NET}" 2>/dev/null || true
docker volume create "${MYSQL_VOL}" 2>/dev/null || true
docker volume create "${MEDIA_VOL}" 2>/dev/null || true
docker volume create "${CONFIG_VOL}" 2>/dev/null || true

echo "[up-core] 停止旧容器（若存在）..."
docker rm -f xxgcms-mysql xxgcms-admin-backend xxgcms-admin-frontend xxgcms-website xxgcms-nginx 2>/dev/null || true
docker rm -f xxgcms-backend 2>/dev/null || true

echo "[up-core] 启动 MySQL ..."
docker run -d --name xxgcms-mysql \
  --network "${NET}" --network-alias mysql \
  --restart unless-stopped \
  -e "MYSQL_ROOT_PASSWORD=${XXGCMS_MYSQL_ROOT_PASSWORD}" \
  -e "MYSQL_DATABASE=${XXGCMS_DB_NAME:-xxgcms}" \
  -e "MYSQL_USER=${XXGCMS_DB_USER:-xxgcms}" \
  -e "MYSQL_PASSWORD=${XXGCMS_DB_PASSWORD}" \
  -e "XXGCMS_CMS_DB_NAME=${XXGCMS_CMS_DB_NAME:-xxgai}" \
  -v "${MYSQL_VOL}:/var/lib/mysql" \
  xxgcms/mysql:latest

echo "[up-core] 等待 MySQL 就绪 ..."
_up_start="${SECONDS}"
for i in $(seq 1 90); do
  if docker exec xxgcms-mysql mysqladmin ping -h 127.0.0.1 -uroot -p"${XXGCMS_MYSQL_ROOT_PASSWORD}" --silent 2>/dev/null; then
    echo "[up-core] MySQL 已就绪（用时 $((SECONDS - _up_start))s）"
    break
  fi
  if [[ "${i}" -eq 90 ]]; then
    echo "错误: MySQL 启动超时" >&2
    docker logs xxgcms-mysql --tail 30
    exit 1
  fi
  if [[ "${i}" -eq 1 || $((i % 10)) -eq 0 ]]; then
    _mlogs="$(docker logs xxgcms-mysql 2>&1 | tail -3 | tr '\n' ' ' | cut -c1-72)"
    if echo "${_mlogs}" | grep -qiE 'Initializing|initdb'; then
      echo "[up-core] MySQL 首次初始化数据目录… (${i}/90, 已 ${SECONDS - _up_start}s)"
    else
      echo "[up-core] 等待 MySQL… (${i}/90, 已 ${SECONDS - _up_start}s)"
    fi
  fi
  sleep 1
done

echo "[up-core] 启动 admin-backend ..."
docker run -d --name xxgcms-admin-backend \
  --network "${NET}" --network-alias backend \
  --restart unless-stopped \
  --env-file .env \
  -e DJANGO_SETTINGS_MODULE=apps.settings.prod \
  -e XXGCMS_MEDIA_DIR=/data/media \
  -e XXGCMS_DB_HOST=mysql \
  -v "${MEDIA_VOL}:/data/media" \
  -v "${CONFIG_VOL}:/data/config" \
  xxgcms/admin-backend:latest

echo "[up-core] 启动 admin-frontend ..."
docker run -d --name xxgcms-admin-frontend \
  --network "${NET}" --network-alias admin-frontend \
  --restart unless-stopped \
  xxgcms/admin-frontend:latest

echo "[up-core] 启动 website ..."
docker run -d --name xxgcms-website \
  --network "${NET}" --network-alias website \
  --restart unless-stopped \
  --env-file .env \
  -e DJANGO_SETTINGS_MODULE=apps.settings.prod \
  -e XXGCMS_MEDIA_DIR=/data/media \
  -e XXGCMS_CMS_SITE_NAME="${XXGCMS_CMS_SITE_NAME:-localhost}" \
  -e XXGCMS_DEFAULT_THEME="${XXGCMS_DEFAULT_THEME:-www_xxg_ai}" \
  -v "${MEDIA_VOL}:/data/media" \
  -v "${CONFIG_VOL}:/data/config:ro" \
  xxgcms/website:latest

echo "[up-core] 启动 nginx ..."
docker run -d --name xxgcms-nginx \
  --network "${NET}" \
  --restart unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -e "XXGCMS_ENABLE_WEBSITE=1" \
  -v "${MEDIA_VOL}:/var/www/media:ro" \
  -v "${CONFIG_VOL}:/data/config" \
  xxgcms/nginx:latest

echo ""
echo "=========================================="
echo " 服务已启动（docker run 模式）"
print_access_urls "${ROOT}/.env"
echo ""
echo " 查看管理员凭据（请先保存到安全位置）:"
echo "   docker exec xxgcms-admin-backend python manage.py show_credentials"
echo ""
echo " 【重要】凭据含后台/MySQL 密码，请立即备份，切勿提交 Git。"
echo ""
echo " 查看日志:"
echo "   docker logs -f xxgcms-admin-backend"
echo "=========================================="
