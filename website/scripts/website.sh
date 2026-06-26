#!/usr/bin/env bash
# 小西瓜CMS 前台统一运维入口
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export WEBSITE_ROOT="$ROOT"
source "$SCRIPT_DIR/lib.sh"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8088}"
DEFAULT_ADDR="${HOST}:${PORT}"

cmd="${1:-help}"
shift || true

case "$cmd" in
  help|-h|--help)
    website_usage
    ;;

  install)
    website_install_deps
    echo "[website] 依赖安装完成"
    ;;

  init-env)
    website_bootstrap_env
    echo "[website] .env 已就绪"
    ;;

  start|run|dev)
    website_ensure_venv
    addr="${1:-$DEFAULT_ADDR}"
    if ! website_has_env; then
      echo "[website] 未发现 .env，自动生成 ..."
      website_bootstrap_env
    fi
    echo "[website] 启动开发服务 http://${addr}"
    website_run_manage runserver "$addr"
    ;;

  prod-start|prod)
    website_ensure_venv
    addr="${1:-$DEFAULT_ADDR}"
    if ! website_has_env; then
      echo "[website] 未发现 .env，自动生成 ..."
      website_bootstrap_env
    fi
    echo "[website] 以生产配置启动 http://${addr}"
    DJANGO_SETTINGS_MODULE=apps.settings.prod website_run_manage runserver "$addr"
    ;;

  check)
    website_ensure_venv
    website_run_manage check
    ;;

  *)
    echo "[website] 未知命令: $cmd"
    echo ""
    website_usage
    exit 1
    ;;
esac
