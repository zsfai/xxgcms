#!/usr/bin/env bash
# 一键卸载 xxg-cms Docker 部署（停止容器、删除镜像；可选清除数据卷）
# 用法:
#   ./uninstall.sh              交互确认，保留数据卷
#   ./uninstall.sh -y           跳过确认，保留数据卷
#   ./uninstall.sh -y --purge-data   同时删除 MySQL / 媒体 / 配置数据卷
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_OFFLINE="${ROOT}/docker-compose.offline.yml"
COMPOSE_DEFAULT="${ROOT}/docker-compose.yml"

YES=0
PURGE_DATA=0

usage() {
  cat <<'EOF'
用法: uninstall.sh [选项]

一键移除 xxg-cms 的 Docker 容器、网络与应用镜像。
默认保留数据卷（数据库、上传文件、配置），便于日后重装。

选项:
  -y, --yes              跳过确认提示
  --purge-data           同时删除数据卷（不可恢复）
  -h, --help             显示帮助

示例:
  ./uninstall.sh -y
  ./uninstall.sh -y --purge-data
  sudo ./uninstall.sh -y --purge-data
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -y|--yes) YES=1; shift ;;
    --purge-data) PURGE_DATA=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage >&2; exit 1 ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "错误: 未安装 Docker。" >&2
  exit 1
fi

has_compose() {
  docker compose version >/dev/null 2>&1 || command -v docker-compose >/dev/null 2>&1
}

compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    docker compose "$@"
  else
    docker-compose "$@"
  fi
}

CONTAINERS=(
  xxgcms-nginx
  xxgcms-admin-frontend
  xxgcms-website
  xxgcms-admin-backend
  xxgcms-backend
  xxgcms-mysql
)

NETWORK="xxgcms-net"

UP_CORE_VOLUMES=(
  xxgcms_mysql_data
  xxgcms_media_data
  xxgcms_config_data
)

XXGCMS_IMAGES=(
  xxgcms/nginx:latest
  xxgcms/website:latest
  xxgcms/admin-frontend:latest
  xxgcms/admin-backend:latest
  xxgcms/mysql:latest
)

echo "=========================================="
echo " xxg-cms Docker 一键卸载"
echo "=========================================="
echo ""
echo "将执行:"
echo "  · 停止并删除 xxg-cms 相关容器"
echo "  · 删除 Docker 网络 ${NETWORK}（若存在）"
echo "  · 删除 xxgcms 私有镜像: ${XXGCMS_IMAGES[*]}"
if [[ "${PURGE_DATA}" == "1" ]]; then
  echo "  · 删除数据卷（MySQL / 媒体 / 配置）—— 不可恢复"
else
  echo "  · 保留数据卷（加 --purge-data 可一并删除）"
fi
echo ""

if [[ "${YES}" != "1" ]]; then
  read -r -p "确认继续？[y/N] " ans
  case "${ans}" in
    y|Y|yes|YES) ;;
    *) echo "已取消。"; exit 0 ;;
  esac
fi

removed_containers=0
removed_volumes=0
removed_images=0

echo ""
echo "[1/4] 停止 compose 栈（若存在）..."
for compose_file in "${COMPOSE_OFFLINE}" "${COMPOSE_DEFAULT}"; do
  if [[ -f "${compose_file}" ]]; then
    project_dir="$(dirname "${compose_file}")"
    compose_name="$(basename "${compose_file}")"
    echo "  -> ${compose_file}"
    if [[ "${PURGE_DATA}" == "1" ]]; then
      (cd "${project_dir}" && compose_cmd -f "${compose_name}" down -v --remove-orphans 2>/dev/null) || true
    else
      (cd "${project_dir}" && compose_cmd -f "${compose_name}" down --remove-orphans 2>/dev/null) || true
    fi
  fi
done

echo "[2/4] 删除 docker run 模式容器 ..."
for name in "${CONTAINERS[@]}"; do
  if docker ps -a --format '{{.Names}}' | grep -qx "${name}"; then
    echo "  -> docker rm -f ${name}"
    docker rm -f "${name}" >/dev/null
    removed_containers=$((removed_containers + 1))
  fi
done

# 兜底：名称含 xxgcms 的容器
while IFS= read -r extra; do
  [[ -z "${extra}" ]] && continue
  echo "  -> docker rm -f ${extra}"
  docker rm -f "${extra}" >/dev/null
  removed_containers=$((removed_containers + 1))
done < <(docker ps -a --format '{{.Names}}' | grep -E 'xxgcms' || true)

echo "[3/4] 清理网络与数据卷 ..."
if docker network inspect "${NETWORK}" >/dev/null 2>&1; then
  echo "  -> docker network rm ${NETWORK}"
  docker network rm "${NETWORK}" >/dev/null 2>&1 || docker network rm "${NETWORK}" --force >/dev/null 2>&1 || true
fi

if [[ "${PURGE_DATA}" == "1" ]]; then
  for vol in "${UP_CORE_VOLUMES[@]}"; do
    if docker volume inspect "${vol}" >/dev/null 2>&1; then
      echo "  -> docker volume rm ${vol}"
      docker volume rm "${vol}" >/dev/null
      removed_volumes=$((removed_volumes + 1))
    fi
  done

  # compose 按目录名前缀的数据卷，如 xxgcms_mysql_data
  while IFS= read -r vol; do
    [[ -z "${vol}" ]] && continue
    if docker volume inspect "${vol}" >/dev/null 2>&1; then
      echo "  -> docker volume rm ${vol}"
      docker volume rm "${vol}" >/dev/null 2>&1 || true
      removed_volumes=$((removed_volumes + 1))
    fi
  done < <(docker volume ls --format '{{.Name}}' | grep -E '(^|_)mysql_data$|(^|_)media_data$|(^|_)config_data$' | grep -iE 'xxgcms|xxg' || true)
fi

echo "[4/4] 删除 xxgcms 私有镜像 ..."
for img in "${XXGCMS_IMAGES[@]}"; do
  if docker image inspect "${img}" >/dev/null 2>&1; then
    echo "  -> docker rmi ${img}"
    docker rmi -f "${img}" >/dev/null 2>&1 || true
    removed_images=$((removed_images + 1))
  fi
done

echo ""
echo "=========================================="
echo " 卸载完成"
echo ""
if [[ "${PURGE_DATA}" == "1" ]]; then
  echo " 数据卷已删除，数据库与上传文件不可恢复。"
else
  echo " 数据卷已保留。完全重装可执行:"
  echo "   sudo ./install.sh"
  echo ""
  echo " 若需彻底清空数据，请执行:"
  echo "   ./uninstall.sh -y --purge-data"
fi
echo ""
echo " 离线包目录（install.sh 所在目录）未自动删除，"
echo " 可手动 rm -rf 解压目录以释放磁盘。"
echo "=========================================="
