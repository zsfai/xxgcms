#!/usr/bin/env bash
# 小西瓜CMS 后端统一运维入口
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
export XXGCMS_ROOT="$ROOT"
source "$SCRIPT_DIR/lib.sh"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
DEFAULT_ADDR="${HOST}:${PORT}"

cmd="${1:-help}"
shift || true

case "$cmd" in
  help|-h|--help)
    xxgcms_usage
    ;;

  install)
    xxgcms_install_deps
    echo "[xxgcms] 依赖安装完成"
    ;;

  setup)
    xxgcms_ensure_venv
    xxgcms_run_manage setup
    xxgcms_print_credentials
    ;;

  init-env)
    xxgcms_ensure_venv
    xxgcms_run_manage init_env
    ;;

  init-db)
    xxgcms_ensure_venv
    xxgcms_run_manage init_db "$@"
    xxgcms_print_credentials
    ;;

  start|run|dev)
    xxgcms_ensure_venv
    addr="${1:-$DEFAULT_ADDR}"
    if ! xxgcms_has_env; then
      echo "[xxgcms] 未发现 .env，自动执行 setup ..."
      xxgcms_run_manage setup
      xxgcms_print_credentials
    fi
    echo "[xxgcms] 启动开发服务 http://${addr}"
    xxgcms_run_manage runserver "$addr"
    ;;

  prod-start|prod)
    xxgcms_ensure_venv
    addr="${1:-$DEFAULT_ADDR}"
    if ! xxgcms_has_env; then
      echo "[xxgcms] 未发现 .env，自动执行 setup ..."
      DJANGO_SETTINGS_MODULE=apps.settings.prod xxgcms_run_manage setup
      xxgcms_print_credentials
    fi
    echo "[xxgcms] 以生产配置启动 http://${addr}"
    DJANGO_SETTINGS_MODULE=apps.settings.prod xxgcms_run_manage runserver "$addr"
    ;;

  user)
    xxgcms_ensure_venv
    if [ $# -lt 2 ]; then
      echo "用法: ./scripts/xxgcms.sh user <用户名> <密码>"
      exit 1
    fi
    xxgcms_run_manage create_xxgcms_user "$1" "$2"
    ;;

  sync-db)
    xxgcms_ensure_venv
    xxgcms_run_manage sync_db "$@"
    ;;

  upgrade-mysql8|mysql8)
    xxgcms_ensure_venv
    xxgcms_run_manage upgrade_mysql8 "$@"
    ;;

  check)
    xxgcms_ensure_venv
    xxgcms_run_manage check
    ;;

  credentials|creds)
    xxgcms_print_credentials
    ;;

  *)
    echo "[xxgcms] 未知命令: $cmd"
    echo ""
    xxgcms_usage
    exit 1
    ;;
esac
