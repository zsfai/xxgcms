#!/usr/bin/env bash
# 在离线 Linux 服务器上运行：加载本地镜像并一键启动
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGES_DIR="${ROOT}/images"
COMPOSE_FILE="${ROOT}/docker-compose.offline.yml"
# shellcheck source=access-urls.sh
source "${ROOT}/access-urls.sh"
# shellcheck source=install-progress.sh
source "${ROOT}/install-progress.sh"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-website)
      echo "提示: 当前离线包已默认包含 website，无需 --with-website" >&2
      shift
      ;;
    -h|--help)
      echo "用法: $0"
      echo "  加载镜像并启动: mysql + admin-backend + admin-frontend + website + nginx"
      exit 0
      ;;
    *) echo "未知参数: $1" >&2; exit 1 ;;
  esac
done

echo "=========================================="
echo " xxg-cms 离线一键安装"
echo "=========================================="

if ! command -v docker >/dev/null 2>&1; then
  echo "错误: 未安装 Docker。请先安装 Docker Engine。" >&2
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

if [[ ! -d "${IMAGES_DIR}" ]]; then
  echo "错误: 未找到 images/ 目录，请确认离线包完整。" >&2
  exit 1
fi

EXPECTED_TARS=(
  xxgcms-mysql.tar
  xxgcms-admin-backend.tar
  xxgcms-admin-frontend.tar
  xxgcms-website.tar
  xxgcms-nginx.tar
)
for tar_name in "${EXPECTED_TARS[@]}"; do
  if [[ ! -f "${IMAGES_DIR}/${tar_name}" ]]; then
    echo "错误: 离线包缺少 ${tar_name}" >&2
    exit 1
  fi
done
ACTUAL_COUNT="$(find "${IMAGES_DIR}" -maxdepth 1 -name '*.tar' | wc -l | tr -d ' ')"
if [[ "${ACTUAL_COUNT}" != "5" ]]; then
  echo "错误: images/ 含 ${ACTUAL_COUNT} 个 tar，期望恰好 5 个" >&2
  ls -1 "${IMAGES_DIR}"/*.tar >&2
  exit 1
fi

validate_docker_tar() {
  local tar_path="$1"
  local tar_name
  tar_name="$(basename "${tar_path}")"
  if [[ ! -s "${tar_path}" ]]; then
    echo "错误: ${tar_name} 为空或不存在，离线包可能不完整。" >&2
    return 1
  fi
  if ! tar -tf "${tar_path}" manifest.json >/dev/null 2>&1; then
    echo "错误: ${tar_name} 不是有效的 Docker 镜像包（无法读取 manifest.json）。" >&2
    echo "  路径: ${tar_path}" >&2
    echo "  大小: $(du -h "${tar_path}" | cut -f1)" >&2
    echo "  类型: $(file -b "${tar_path}" 2>/dev/null || echo '未知')" >&2
    echo "  常见原因: 传输中断、磁盘满、打包失败。请重新制作离线包或单独替换该 tar。" >&2
    return 1
  fi
}

echo "[1/4] 校验并加载 Docker 镜像 ..."
LOAD_ORDER=(
  xxgcms-mysql.tar
  xxgcms-admin-backend.tar
  xxgcms-admin-frontend.tar
  xxgcms-website.tar
  xxgcms-nginx.tar
)
for tar_name in "${LOAD_ORDER[@]}"; do
  tar_file="${IMAGES_DIR}/${tar_name}"
  validate_docker_tar "${tar_file}"
  echo "  -> docker load -i ${tar_file}"
  if ! docker load -i "${tar_file}"; then
    echo "错误: 加载 ${tar_name} 失败（docker load 退出非 0）。" >&2
    exit 1
  fi
done

echo "[2/4] 检查镜像 ..."
REQUIRED_IMAGES=(
  xxgcms/mysql:latest
  xxgcms/admin-backend:latest
  xxgcms/admin-frontend:latest
  xxgcms/website:latest
  xxgcms/nginx:latest
)
for img in "${REQUIRED_IMAGES[@]}"; do
  if ! docker image inspect "${img}" >/dev/null 2>&1; then
    echo "错误: 镜像 ${img} 未加载成功" >&2
    exit 1
  fi
  echo "  OK ${img}"
done

echo "[3/4] 准备环境配置 ..."
cd "${ROOT}"
NEW_ENV=0
if [[ ! -f .env ]]; then
  cp .env.docker.example .env
  NEW_ENV=1
  echo "  已从 .env.docker.example 创建 .env"
else
  echo "  使用已有 .env"
fi

if [[ "${NEW_ENV}" == "1" ]] || grep -q '__AUTO__' .env 2>/dev/null || grep -qE '=.*[^$]\$[^$]' .env 2>/dev/null; then
  BOOTSTRAP=""
  for candidate in "${ROOT}/bootstrap-docker-env.sh" "${ROOT}/docker/scripts/bootstrap-docker-env.sh"; do
    if [[ -f "${candidate}" ]]; then
      BOOTSTRAP="${candidate}"
      break
    fi
  done
  if [[ -n "${BOOTSTRAP}" ]]; then
    chmod +x "${BOOTSTRAP}" 2>/dev/null || true
    bash "${BOOTSTRAP}" "${ROOT}/.env"
  else
    echo "  警告: 未找到 bootstrap-docker-env.sh，请确认 .env 中数据库密码已设置" >&2
  fi
fi

if grep -q '^XXGCMS_ENABLE_WEBSITE=' .env; then
  sed -i 's/^XXGCMS_ENABLE_WEBSITE=.*/XXGCMS_ENABLE_WEBSITE=1/' .env
else
  echo 'XXGCMS_ENABLE_WEBSITE=1' >> .env
fi

# Docker 离线部署：MySQL 在独立容器，主机名必须为 mysql
if grep -q '^XXGCMS_DB_HOST=' .env; then
  sed -i 's/^XXGCMS_DB_HOST=.*/XXGCMS_DB_HOST=mysql/' .env
else
  echo 'XXGCMS_DB_HOST=mysql' >> .env
fi

echo "[4/4] 启动服务 ..."
USE_UP_CORE=0

if has_compose; then
  compose_cmd -f "${COMPOSE_FILE}" up -d
else
  if [[ ! -x "${ROOT}/up-core.sh" ]]; then
    echo "错误: 未找到 docker compose，且缺少 up-core.sh" >&2
    echo "  请安装: sudo apt install -y docker-compose-plugin" >&2
    exit 1
  fi
  echo "未找到 docker compose，使用 docker run 模式启动 ..."
  "${ROOT}/up-core.sh"
  USE_UP_CORE=1
fi

RUNNING=0
if [[ "${USE_UP_CORE}" == "1" ]]; then
  docker ps --format '{{.Names}}' | grep -qx 'xxgcms-admin-backend' && RUNNING=1
elif has_compose && compose_cmd -f "${COMPOSE_FILE}" ps 2>/dev/null | grep -q backend; then
  RUNNING=1
fi

if [[ "${RUNNING}" == "1" ]]; then
  if wait_for_backend_ready_with_progress 300 "${USE_UP_CORE}" "${COMPOSE_FILE}"; then
    echo "  数据库结构已在容器启动时同步完成"
  else
    echo "  警告: backend 尚未完全就绪，请稍后查看日志:" >&2
    if [[ "${USE_UP_CORE}" == "1" ]]; then
      echo "    docker logs xxgcms-admin-backend" >&2
    else
      echo "    docker compose -f docker-compose.offline.yml logs backend" >&2
    fi
  fi
  echo ""
  echo "=========================================="
  echo " 安装完成"
  echo ""
  print_access_urls "${ROOT}/.env"
  echo ""
  echo " 查看管理员账号（请先保存凭据到安全位置）:"
  if [[ "${USE_UP_CORE}" == "1" ]]; then
    echo "   docker exec xxgcms-admin-backend python manage.py show_credentials"
  else
    echo "   docker compose -f docker-compose.offline.yml exec backend python manage.py show_credentials"
  fi
  echo ""
  echo " 【重要】凭据含后台/MySQL 密码，仅显示一次请立即备份，切勿提交 Git。"
  echo "=========================================="
else
  echo "警告: 部分服务可能尚未就绪，请执行:"
  if [[ "${USE_UP_CORE}" == "1" ]]; then
    echo "  docker ps"
    echo "  docker logs xxgcms-admin-backend"
  else
    echo "  docker compose -f docker-compose.offline.yml ps"
    echo "  docker compose -f docker-compose.offline.yml logs backend"
  fi
fi
