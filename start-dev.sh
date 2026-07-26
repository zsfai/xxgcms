#!/usr/bin/env bash
# 仓库根目录快捷入口
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$ROOT/scripts/dev-start.sh" "$@"
