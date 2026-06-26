#!/usr/bin/env bash
# 仅从服务器下载已构建好的离线包（不重新构建）
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/deploy.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "请先创建 deploy.env" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${ENV_FILE}"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/ssh-common.sh"

SSH_PORT="${SSH_PORT:-22}"
LOCAL_DOWNLOAD_DIR="${LOCAL_DOWNLOAD_DIR:-.}"

mkdir -p "${ROOT}/${LOCAL_DOWNLOAD_DIR}"
REMOTE_BUNDLE="$(run_ssh "ls -t ${REMOTE_DIR}/xxgcms-*.tar.gz 2>/dev/null | grep -v 'xxgcms-src-' | head -1")"
if [[ -z "${REMOTE_BUNDLE}" ]]; then
  echo "错误: 远程未找到离线安装包 (xxgcms-*.tar.gz)" >&2
  exit 1
fi
run_scp_from_remote "${REMOTE_BUNDLE}" "${ROOT}/${LOCAL_DOWNLOAD_DIR}"

ls -lh "${ROOT}/${LOCAL_DOWNLOAD_DIR}/$(basename "${REMOTE_BUNDLE}")"
