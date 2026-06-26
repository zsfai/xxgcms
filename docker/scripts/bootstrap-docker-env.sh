#!/usr/bin/env bash
# 在 docker compose up 之前为 .env 生成随机密码/密钥
set -euo pipefail

ENV_FILE="${1:-.env}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "错误: 未找到 ${ENV_FILE}" >&2
  exit 1
fi

if command -v python3 >/dev/null 2>&1; then
  python3 "${SCRIPT_DIR}/bootstrap-docker-env.py" "${ENV_FILE}"
elif command -v python >/dev/null 2>&1; then
  python "${SCRIPT_DIR}/bootstrap-docker-env.py" "${ENV_FILE}"
else
  echo "错误: 需要 python3 以生成随机数据库密码" >&2
  exit 1
fi
