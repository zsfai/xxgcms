#!/usr/bin/env bash
# 一键制作 xxg-cms 离线安装包（全栈五镜像）
# 须在已安装 Docker 的 Linux/macOS 机器上运行
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT}"

if ! command -v docker >/dev/null 2>&1; then
  echo "错误: 未找到 docker。请先安装 Docker Engine / Docker Desktop。" >&2
  echo "  https://docs.docker.com/get-docker/" >&2
  exit 1
fi

if [[ ! -f .env ]]; then
  cp .env.docker.example .env
  echo "已从 .env.docker.example 创建 .env"
fi

exec "${ROOT}/docker/offline/bundle.sh"
