#!/usr/bin/env bash
# 入口脚本：从项目根目录执行远程离线包制作
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/offline-pack/upload-and-build.sh" "$@"
