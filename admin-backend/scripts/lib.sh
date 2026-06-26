# 小西瓜CMS 后端 shell 公共函数库
# 由 scripts/xxgcms.sh 引用，勿直接执行

xxgcms_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

xxgcms_detect_python() {
  local root="$1"
  if [ -x "$root/.venv/Scripts/python.exe" ]; then
    echo "$root/.venv/Scripts/python"
  elif [ -x "$root/.venv/bin/python" ]; then
    echo "$root/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  else
    command -v python
  fi
}

xxgcms_run_manage() {
  local root="${XXGCMS_ROOT:-$(xxgcms_root)}"
  local py="${XXGCMS_PYTHON:-$(xxgcms_detect_python "$root")}"
  export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-apps.settings.dev}"
  cd "$root" || exit 1
  "$py" manage.py "$@"
}

xxgcms_ensure_venv() {
  local root="${XXGCMS_ROOT:-$(xxgcms_root)}"
  local py="${XXGCMS_PYTHON:-$(xxgcms_detect_python "$root")}"
  if [ ! -x "$py" ] || [ "$py" = "python" ] || [ "$py" = "$(command -v python3 2>/dev/null)" ]; then
    if [ ! -d "$root/.venv" ]; then
      echo "[xxgcms] 创建虚拟环境 .venv ..."
      python3 -m venv "$root/.venv" 2>/dev/null || python -m venv "$root/.venv"
    fi
    py="$(xxgcms_detect_python "$root")"
  fi
  XXGCMS_PYTHON="$py"
  export XXGCMS_PYTHON
}

xxgcms_install_deps() {
  local root="${XXGCMS_ROOT:-$(xxgcms_root)}"
  xxgcms_ensure_venv
  local py="${XXGCMS_PYTHON:-$(xxgcms_detect_python "$root")}"
  echo "[xxgcms] 安装依赖 requirements.txt ..."
  "$py" -m pip install --upgrade pip
  "$py" -m pip install -r "$root/requirements.txt"
}

xxgcms_has_env() {
  local root="${XXGCMS_ROOT:-$(xxgcms_root)}"
  [ -f "$root/.env" ]
}

xxgcms_print_credentials() {
  local root="${XXGCMS_ROOT:-$(xxgcms_root)}"
  if [ -f "$root/.credentials" ]; then
    echo ""
    echo "=========================================="
    echo " 【重要】请立即复制并妥善保存下方凭据！"
    echo " 含管理后台、MySQL 等密码；丢失后只能重置。"
    echo "=========================================="
    echo ""
    echo "======== 部署凭据（.credentials）========"
    cat "$root/.credentials"
    echo "============================================"
    echo " 请务必将上述凭据保存到安全位置。"
  fi
}

xxgcms_usage() {
  cat <<'EOF'
小西瓜CMS 后端运维脚本

用法: ./scripts/xxgcms.sh <命令> [参数...]

命令:
  install          创建 .venv 并安装 pip 依赖
  setup            一键初始化（生成 .env + 数据库 + 管理员）
  init-env         仅生成/补全 .env 与 website/.env
  init-db          初始化数据库（可选参数见下方）
  start [地址]     启动开发服务（默认 0.0.0.0:8000，无 .env 时先 setup）
  prod-start [地址] 以生产配置启动（apps.settings.prod，默认 0.0.0.0:8000）
  user <名> <密码> 创建或重置后台用户
  sync-db          增量同步库结构（可选 --dry-run --all-sites 等）
  upgrade-mysql8   MySQL 5.7→8.0 结构升级（零日期、utf8mb4）
  check            Django 配置检查
  credentials      查看 .credentials 管理员凭据
  help             显示本帮助

init-db 可选参数（原样传给 manage.py）:
  --xxgcms         仅初始化系统库
  --cms            仅初始化 CMS 库
  --cms-db NAME    CMS 库名
  --site-name NAME 测试站点标识
  --skip-site      不写入测试站点

sync-db 可选参数:
  --dry-run        仅预览
  --xxgcms / --cms 仅同步指定库
  --all-sites      同步全部站点库
  --cms-db NAME    指定 CMS 库名

upgrade-mysql8 可选参数:
  --dry-run        仅预览
  --xxgcms / --cms 仅升级指定库
  --all-sites      升级全部站点 CMS 库
  --cms-db NAME    指定 CMS 库名
  --convert-tables 转换全部表为 utf8mb4_unicode_ci（大库慎用）

环境变量:
  HOST             默认绑定地址（默认 0.0.0.0）
  PORT             默认端口（默认 8000）
  DJANGO_SETTINGS_MODULE  dev 命令默认 apps.settings.dev

示例:
  ./scripts/xxgcms.sh install
  ./scripts/xxgcms.sh setup
  ./scripts/xxgcms.sh start
  ./scripts/start.sh
  ./scripts/xxgcms.sh init-db --cms-db mysite --site-name demo
  ./scripts/xxgcms.sh sync-db --dry-run
  ./scripts/xxgcms.sh user admin mypassword
EOF
}
