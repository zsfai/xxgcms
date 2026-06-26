#!/usr/bin/env bash
# 打包 Docker 构建所需源码（不含 node_modules、venv、离线包产物等）
# 仅最后一行 stdout 输出 tar 包绝对路径，供 upload-and-build.sh 捕获
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT}"

DATE="$(date +%Y%m%d)"
ARCHIVE="${ROOT}/xxgcms-src-${DATE}.tar.gz"

echo "[pack] 项目根目录: ${ROOT}" >&2
echo "[pack] 输出: ${ARCHIVE}" >&2

if [[ -f "${ARCHIVE}" ]]; then
  echo "[pack] 覆盖当日已有源码包" >&2
  rm -f "${ARCHIVE}"
fi

# 注意：Windows Git Bash 下 --exclude='./**/node_modules' 不生效，须用 --exclude='node_modules'
TAR_EXCLUDES=(
  --exclude='.git'
  --exclude='node_modules'
  --exclude='.venv'
  --exclude='__pycache__'
  --exclude='*.pyc'
  --exclude='dist'
  --exclude='xxgcms_static_files'
  --exclude='xxgcms'
  --exclude='.env'
  --exclude='.credentials'
  --exclude='docs/superpowers'
  --exclude='.cursor'
  --exclude='xxgcms-src-*.tar.gz'
  --exclude='xxgcms-*.tar.gz'
)

echo "[pack] 正在压缩（已排除 node_modules / dist / xxgcms_static_files 等）..." >&2
SECONDS=0
tar -czf "${ARCHIVE}" \
  "${TAR_EXCLUDES[@]}" \
  -C "${ROOT}" \
  admin-backend \
  admin-frontend \
  website \
  docker \
  docker-compose.yml \
  docker-compose.offline.yml \
  .env.docker.example \
  .dockerignore \
  make-offline-bundle.sh \
  scripts/offline-pack

SIZE="$(du -sh "${ARCHIVE}" | cut -f1)"
echo "[pack] 完成 (${SIZE}, ${SECONDS}s): ${ARCHIVE}" >&2
printf '%s\n' "${ARCHIVE}"
