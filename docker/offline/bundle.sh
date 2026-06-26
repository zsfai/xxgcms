#!/usr/bin/env bash
# 在有网络的机器上运行：构建并导出全部 Docker 镜像，生成离线安装包
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUNDLE_NAME="xxgcms"
BUNDLE_DIR="${ROOT}/${BUNDLE_NAME}"
IMAGES_DIR="${BUNDLE_DIR}/images"
PKG_JSON="${ROOT}/admin-frontend/package.json"
BUILD_DATE="$(date +%Y%m%d)"

read_app_version() {
  if command -v node >/dev/null 2>&1; then
    node -p "require('${PKG_JSON}').version"
    return
  fi
  sed -n 's/.*"version"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "${PKG_JSON}" | head -1
}

APP_VERSION="$(read_app_version)"
if [[ -z "${APP_VERSION}" ]]; then
  echo "错误: 无法从 admin-frontend/package.json 读取 version" >&2
  exit 1
fi

ARCHIVE_BASENAME="${BUNDLE_NAME}-${APP_VERSION}-${BUILD_DATE}"

echo "=========================================="
echo " xxg-cms 离线安装包制作"
echo " 版本: ${APP_VERSION} (admin-frontend/package.json)"
echo " 输出目录: ${BUNDLE_DIR}"
echo " 镜像: admin-backend + admin-frontend + website + nginx + mysql"
echo "=========================================="

cd "${ROOT}"

if ! command -v docker >/dev/null 2>&1; then
  echo "错误: 未找到 docker 命令" >&2
  exit 1
fi

check_disk_space() {
  local target_dir="$1"
  mkdir -p "${target_dir}"
  local avail_kb
  avail_kb="$(df -Pk "${target_dir}" | awk 'NR==2 {print $4}')"
  local avail_mb=$((avail_kb / 1024))
  echo "  磁盘可用: ${avail_mb} MB (${target_dir})"
  if [[ "${avail_mb}" -lt 1024 ]]; then
    echo "错误: 磁盘可用空间不足 1GB，无法安全导出镜像 tar（建议 ≥ 3GB）。" >&2
    echo "  请清理 Docker: docker system prune -a" >&2
    echo "  或将 REMOTE_DIR 改到空间更大的目录（建议纯英文路径，如 /home/abc/xxg-cms-build）。" >&2
    df -h "${target_dir}" >&2 || true
    exit 1
  fi
  if [[ "${avail_mb}" -lt 3072 ]]; then
    echo "  警告: 可用空间偏紧（< 3GB），导出可能失败，建议先执行 docker system prune -a" >&2
  fi
}

verify_docker_tar() {
  local path="$1"
  local name
  name="$(basename "${path}")"
  if [[ ! -s "${path}" ]]; then
    echo "错误: ${name} 导出为空" >&2
    return 1
  fi
  if tar -tf "${path}" manifest.json >/dev/null 2>&1; then
    echo "  OK ${name} ($(du -h "${path}" | cut -f1))"
    return 0
  fi
  if tar -tf "${path}" index.json >/dev/null 2>&1 && tar -tf "${path}" oci-layout >/dev/null 2>&1; then
    echo "  OK ${name} (OCI, $(du -h "${path}" | cut -f1))"
    return 0
  fi
  echo "错误: ${name} 不是有效 Docker 镜像 tar。" >&2
  echo "  大小: $(du -h "${path}" | cut -f1)" >&2
  echo "  类型: $(file -b "${path}" 2>/dev/null || echo '未知')" >&2
  echo "  常见原因: 磁盘满导致 docker save 中断；请 df -h 检查并清理后重试。" >&2
  rm -f "${path}"
  return 1
}

save_image_tar() {
  local image="$1"
  local out_path="$2"
  local tmp_path="${out_path}.tmp"
  local name
  name="$(basename "${out_path}")"

  echo "  -> save ${image} -> ${name}"
  if ! docker image inspect "${image}" >/dev/null 2>&1; then
    echo "错误: 镜像不存在: ${image}" >&2
    exit 1
  fi

  rm -f "${tmp_path}" "${out_path}"
  if ! docker save "${image}" -o "${tmp_path}"; then
    echo "错误: docker save ${image} 失败" >&2
    rm -f "${tmp_path}"
    exit 1
  fi

  if ! verify_docker_tar "${tmp_path}"; then
    echo "错误: ${name} 导出校验失败（镜像 ${image}）" >&2
    docker system df >&2 || true
    exit 1
  fi

  mv "${tmp_path}" "${out_path}"
}

docker_build() {
  local dockerfile="$1"
  local tag="$2"
  echo "  -> ${tag}"
  local -a build_args=(
    --build-arg "USE_CN_MIRROR=${USE_CN_MIRROR:-1}"
  )
  if docker buildx version >/dev/null 2>&1; then
    DOCKER_BUILDKIT=1 docker build --progress=plain "${build_args[@]}" -f "${dockerfile}" -t "${tag}" .
  else
    echo "  (未安装 buildx，使用经典 docker build；如需 BuildKit: sudo apt install docker-buildx-plugin)"
    docker build "${build_args[@]}" -f "${dockerfile}" -t "${tag}" .
  fi
}

docker_pull_if_needed() {
  local img="$1"
  if docker image inspect "${img}" >/dev/null 2>&1; then
    echo "  已有 ${img}，跳过 pull"
  else
    echo "  pull ${img} ..."
    docker pull "${img}"
  fi
}

echo "[1/6] 拉取基础镜像（本地已有则跳过）..."
docker_pull_if_needed mysql:8.0
docker_pull_if_needed python:3.12-slim
docker_pull_if_needed node:20-alpine
docker_pull_if_needed nginx:1.27-alpine

echo "[2/6] 构建 xxgcms 私有镜像（5 个，与其他 Docker 栈隔离）..."
docker_build docker/Dockerfile.mysql xxgcms/mysql:latest
docker_build docker/Dockerfile.backend xxgcms/admin-backend:latest
docker_build docker/Dockerfile.admin-frontend xxgcms/admin-frontend:latest
docker_build docker/Dockerfile.website xxgcms/website:latest
docker_build docker/Dockerfile.nginx xxgcms/nginx:latest

echo "[3/6] 导出镜像为 tar ..."
rm -rf "${BUNDLE_DIR}"
mkdir -p "${IMAGES_DIR}"
check_disk_space "${IMAGES_DIR}"
echo "  Docker 存储占用:"
docker system df 2>/dev/null || true

save_image_tar xxgcms/mysql:latest "${IMAGES_DIR}/xxgcms-mysql.tar"
save_image_tar xxgcms/admin-backend:latest "${IMAGES_DIR}/xxgcms-admin-backend.tar"
save_image_tar xxgcms/admin-frontend:latest "${IMAGES_DIR}/xxgcms-admin-frontend.tar"
save_image_tar xxgcms/website:latest "${IMAGES_DIR}/xxgcms-website.tar"
save_image_tar xxgcms/nginx:latest "${IMAGES_DIR}/xxgcms-nginx.tar"

echo "  全部 tar 校验通过"

echo "[3.5/6] 校验镜像包（应恰好 5 个 xxgcms 私有镜像）..."
EXPECTED_TARS=(
  xxgcms-mysql.tar
  xxgcms-admin-backend.tar
  xxgcms-admin-frontend.tar
  xxgcms-website.tar
  xxgcms-nginx.tar
)
for tar_name in "${EXPECTED_TARS[@]}"; do
  if [[ ! -f "${IMAGES_DIR}/${tar_name}" ]]; then
    echo "错误: 缺少 ${tar_name}" >&2
    exit 1
  fi
done
ACTUAL_COUNT="$(find "${IMAGES_DIR}" -maxdepth 1 -name '*.tar' | wc -l | tr -d ' ')"
if [[ "${ACTUAL_COUNT}" != "5" ]]; then
  echo "错误: images/ 下 tar 数量为 ${ACTUAL_COUNT}，期望 5（勿多勿少）" >&2
  ls -1 "${IMAGES_DIR}"/*.tar >&2
  exit 1
fi
echo "  OK 5/5: ${EXPECTED_TARS[*]}"

echo "[4/6] 复制离线部署文件 ..."
cp "${ROOT}/docker-compose.offline.yml" "${BUNDLE_DIR}/"
cp "${ROOT}/.env.docker.example" "${BUNDLE_DIR}/"
cp "${ROOT}/docker/offline/install.sh" "${BUNDLE_DIR}/install.sh"
cp "${ROOT}/docker/offline/uninstall.sh" "${BUNDLE_DIR}/uninstall.sh"
cp "${ROOT}/docker/scripts/bootstrap-docker-env.py" "${BUNDLE_DIR}/bootstrap-docker-env.py"
cp "${ROOT}/docker/scripts/bootstrap-docker-env.sh" "${BUNDLE_DIR}/bootstrap-docker-env.sh"
cp "${ROOT}/docker/offline/up-core.sh" "${BUNDLE_DIR}/up-core.sh"
cp "${ROOT}/docker/offline/access-urls.sh" "${BUNDLE_DIR}/access-urls.sh"
cp "${ROOT}/docker/offline/install-progress.sh" "${BUNDLE_DIR}/install-progress.sh"
cp "${ROOT}/docker/offline/README-OFFLINE.md" "${BUNDLE_DIR}/README.md"
chmod +x "${BUNDLE_DIR}/install.sh" "${BUNDLE_DIR}/uninstall.sh" "${BUNDLE_DIR}/bootstrap-docker-env.sh" "${BUNDLE_DIR}/up-core.sh"

echo "[5/6] 生成版本信息 ..."
cat > "${BUNDLE_DIR}/VERSION" <<EOF
app_version=${APP_VERSION}
bundle_version=${ARCHIVE_BASENAME}
build_date=${BUILD_DATE}
mysql_image=xxgcms/mysql:latest
admin_backend_image=xxgcms/admin-backend:latest
admin_frontend_image=xxgcms/admin-frontend:latest
website_image=xxgcms/website:latest
nginx_image=xxgcms/nginx:latest
created_at=$(date -Iseconds 2>/dev/null || date)
EOF

echo "[6/6] 打包压缩 ..."
ARCHIVE="${ROOT}/${ARCHIVE_BASENAME}.tar.gz"
tar -czf "${ARCHIVE}" -C "${ROOT}" "${BUNDLE_NAME}"

TOTAL_SIZE="$(du -sh "${ARCHIVE}" | cut -f1)"
echo ""
echo "=========================================="
echo " 离线包制作完成"
echo " 版本: ${APP_VERSION}"
echo " 目录: ${BUNDLE_DIR}"
echo " 压缩包: ${ARCHIVE} (${TOTAL_SIZE})"
echo ""
echo " 离线服务器安装:"
echo "   tar xzf ${ARCHIVE_BASENAME}.tar.gz"
echo "   cd ${BUNDLE_NAME} && sudo ./install.sh"
echo "=========================================="
