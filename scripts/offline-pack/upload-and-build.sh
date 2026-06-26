#!/usr/bin/env bash
# 本地一键：打包源码 → 上传到 Ubuntu → 远程构建离线包 →（可选）下载回本地
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/deploy.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "请先创建配置文件:" >&2
  echo "  cp scripts/offline-pack/deploy.env.example scripts/offline-pack/deploy.env" >&2
  echo "  编辑 deploy.env 填写 REMOTE_USER / REMOTE_HOST / REMOTE_DIR" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${ENV_FILE}"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/ssh-common.sh"

REMOTE_USER="${REMOTE_USER:?请在 deploy.env 设置 REMOTE_USER}"
REMOTE_HOST="${REMOTE_HOST:?请在 deploy.env 设置 REMOTE_HOST}"
REMOTE_DIR="${REMOTE_DIR:-${HOME}/xxg-cms-build}"
SSH_PORT="${SSH_PORT:-22}"
DOWNLOAD_BUNDLE="${DOWNLOAD_BUNDLE:-0}"
LOCAL_DOWNLOAD_DIR="${LOCAL_DOWNLOAD_DIR:-.}"

echo "=========================================="
echo " 远程制作 xxg-cms 离线安装包"
echo " 服务器: ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}"
if [[ -n "${REMOTE_PASSWORD:-}" ]]; then
  echo " 认证: 密码（deploy.env 本地配置）"
else
  echo " 认证: SSH 密钥"
fi
echo "=========================================="

echo "[1/3] 打包源码 ..."
ARCHIVE="$("${SCRIPT_DIR}/pack.sh")"
ARCHIVE="${ARCHIVE##*$'\n'}"  # 防御：只取最后一行路径
if [[ ! -f "${ARCHIVE}" ]]; then
  echo "错误: 打包产物不存在: ${ARCHIVE}" >&2
  exit 1
fi
ARCHIVE="$(cd "$(dirname "${ARCHIVE}")" && pwd)/$(basename "${ARCHIVE}")"
ARCHIVE_NAME="$(basename "${ARCHIVE}")"
echo "  -> ${ARCHIVE} (${ARCHIVE_NAME})"

echo "[2/3] 上传到服务器 ..."
run_ssh "mkdir -p '${REMOTE_DIR}'"
run_scp_to_remote "${ARCHIVE}" "${REMOTE_DIR}/${ARCHIVE_NAME}"

echo "[3/3] 远程构建（实时输出如下，约 10-30 分钟）..."
echo "------------------------------------------"
if ! run_ssh_script \
  "REMOTE_DIR='${REMOTE_DIR}'" \
  "${SCRIPT_DIR}/remote-build.sh"; then
  echo "------------------------------------------" >&2
  echo "错误: 远程构建失败，请查看上方输出" >&2
  exit 1
fi
echo "------------------------------------------"

if [[ "${DOWNLOAD_BUNDLE}" == "1" ]]; then
  echo "[可选] 下载离线包到本地 ${LOCAL_DOWNLOAD_DIR} ..."
  mkdir -p "${ROOT}/${LOCAL_DOWNLOAD_DIR}"
  REMOTE_BUNDLE="$(run_ssh "ls -t ${REMOTE_DIR}/xxgcms-*.tar.gz 2>/dev/null | grep -v 'xxgcms-src-' | head -1")"
  if [[ -z "${REMOTE_BUNDLE}" ]]; then
    echo "错误: 远程未找到离线安装包" >&2
    exit 1
  fi
  run_scp_from_remote "${REMOTE_BUNDLE}" "${ROOT}/${LOCAL_DOWNLOAD_DIR}"
  echo ""
  echo "本地离线包:"
  ls -lh "${ROOT}/${LOCAL_DOWNLOAD_DIR}/$(basename "${REMOTE_BUNDLE}")"
fi

echo ""
echo "=========================================="
echo " 全部完成"
echo " 服务器离线包: ${REMOTE_DIR}/xxgcms-{version}-{date}.tar.gz"
if [[ "${DOWNLOAD_BUNDLE}" != "1" ]]; then
  echo " 测试完成后手动下载:"
  echo "   ./scripts/offline-pack/download-bundle.sh"
fi
echo "=========================================="
