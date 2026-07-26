#!/usr/bin/env bash
# 本地开发：一键启动 admin-backend / admin-frontend / website
# 用法（仓库根目录）:
#   ./scripts/dev-start.sh
#   ./start-dev.sh
# Ctrl+C 停止全部服务。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT/.dev-logs"
mkdir -p "$LOG_DIR"

BACKEND_ADDR="${BACKEND_ADDR:-0.0.0.0:8000}"
WEBSITE_ADDR="${WEBSITE_ADDR:-0.0.0.0:8088}"
PIDS=()

cleanup() {
  local pid
  echo ""
  echo "[dev-start] 正在停止服务 ..."
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      kill -- -"$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
  done
  echo "[dev-start] 已全部停止"
}
trap cleanup EXIT INT TERM

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[dev-start] 缺少命令: $1" >&2
    exit 1
  fi
}

start_bg() {
  local name="$1"
  local log="$LOG_DIR/${name}.log"
  shift
  echo "[dev-start] 启动 ${name} ..."
  "$@" >"$log" 2>&1 &
  local pid=$!
  PIDS+=("$pid")
  echo "[dev-start]   ${name} pid=${pid}  log=${log}"
}

if [ ! -f "$ROOT/admin-backend/scripts/xxgcms.sh" ]; then
  echo "[dev-start] 未找到 admin-backend/scripts/xxgcms.sh" >&2
  exit 1
fi
chmod +x "$ROOT/admin-backend/scripts/xxgcms.sh" "$ROOT/admin-backend/scripts/start.sh" 2>/dev/null || true
start_bg backend "$ROOT/admin-backend/scripts/xxgcms.sh" start "$BACKEND_ADDR"

if [ -f "$ROOT/website/scripts/website.sh" ]; then
  chmod +x "$ROOT/website/scripts/website.sh" "$ROOT/website/scripts/start.sh" 2>/dev/null || true
  start_bg website "$ROOT/website/scripts/website.sh" start "$WEBSITE_ADDR"
else
  echo "[dev-start] 跳过 website（脚本不存在）"
fi

need_cmd npm
if [ ! -d "$ROOT/admin-frontend/node_modules" ]; then
  echo "[dev-start] admin-frontend 未安装依赖，执行 npm install ..."
  (cd "$ROOT/admin-frontend" && npm install)
fi
echo "[dev-start] 启动 frontend ..."
(
  cd "$ROOT/admin-frontend"
  npm run dev
) >"$LOG_DIR/frontend.log" 2>&1 &
_fp=$!
PIDS+=("$_fp")
echo "[dev-start]   frontend pid=${_fp}  log=$LOG_DIR/frontend.log"

echo ""
echo "=========================================="
echo " 本地开发服务已启动"
echo "------------------------------------------"
echo " 管理后台前端  http://localhost:8080"
echo " 管理后台 API  http://localhost:8000"
echo " 站点前台      http://localhost:8088"
echo " 日志目录      ${LOG_DIR}"
echo "------------------------------------------"
echo " 按 Ctrl+C 停止全部服务"
echo "=========================================="
echo ""

while true; do
  for pid in "${PIDS[@]}"; do
    if ! kill -0 "$pid" 2>/dev/null; then
      echo "[dev-start] 进程 ${pid} 已退出，查看 .dev-logs/ 日志"
      exit 1
    fi
  done
  sleep 2
done
