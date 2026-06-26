#!/usr/bin/env bash
# 在 Ubuntu 构建服务器上执行：解压源码并制作离线安装包
set -euo pipefail

REMOTE_DIR="${REMOTE_DIR:-${HOME}/xxg-cms-build}"
TODAY="$(date +%Y%m%d)"

log() {
  echo "[remote-build $(date '+%H:%M:%S')] $*"
}

mkdir -p "${REMOTE_DIR}"
cd "${REMOTE_DIR}"

SRC="xxgcms-src-${TODAY}.tar.gz"
if [[ ! -f "${SRC}" ]]; then
  SRC="$(ls -t xxgcms-src-*.tar.gz 2>/dev/null | head -1 || true)"
fi
if [[ -z "${SRC}" || ! -f "${SRC}" ]]; then
  echo "错误: ${REMOTE_DIR} 下未找到 xxgcms-src-*.tar.gz" >&2
  exit 1
fi

log "使用源码包: ${SRC} ($(du -sh "${SRC}" | cut -f1))"
log "解压到 ${REMOTE_DIR}/src ..."
rm -rf src
mkdir -p src
tar -xzf "${SRC}" -C src

cd src
chmod +x make-offline-bundle.sh docker/offline/*.sh 2>/dev/null || true

if [[ -f /etc/docker/daemon.json ]] && ! grep -q 'registry-mirrors' /etc/docker/daemon.json 2>/dev/null; then
  log "提示: docker pull 较慢时可执行 sudo ./docker/offline/setup-docker-mirror-cn.sh"
fi

log "开始制作离线包（已启用 apt/pip/npm 国内源，请稍候）..."
log "磁盘: $(df -h "${REMOTE_DIR}" | awk 'NR==2 {print $4 " 可用 / " $2 " 总计 (" $NF ")"}')"
./make-offline-bundle.sh

log "复制离线包到 ${REMOTE_DIR} ..."
BUNDLE="$(ls -t xxgcms-*.tar.gz 2>/dev/null | grep -v '^xxgcms-src-' | head -1 || true)"
if [[ -z "${BUNDLE}" || ! -f "${BUNDLE}" ]]; then
  echo "错误: 未找到 xxgcms-{version}-{date}.tar.gz" >&2
  exit 1
fi
cp "${BUNDLE}" "${REMOTE_DIR}/"
log "全部完成: ${REMOTE_DIR}/${BUNDLE##*/} ($(du -sh "${REMOTE_DIR}/${BUNDLE##*/}" | cut -f1))"
