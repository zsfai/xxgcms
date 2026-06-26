# 小西瓜CMS 前台 shell 公共函数库
# 由 scripts/website.sh 引用，勿直接执行

website_root() {
  cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd
}

website_admin_root() {
  local root="${WEBSITE_ROOT:-$(website_root)}"
  echo "$(cd "$root/../admin-backend" && pwd)"
}

website_detect_python() {
  local root="$1"
  local admin_root
  admin_root="$(website_admin_root)"

  if [ -x "$root/.venv/Scripts/python.exe" ]; then
    echo "$root/.venv/Scripts/python"
  elif [ -x "$root/.venv/bin/python" ]; then
    echo "$root/.venv/bin/python"
  elif [ -x "$admin_root/.venv/Scripts/python.exe" ]; then
    echo "$admin_root/.venv/Scripts/python"
  elif [ -x "$admin_root/.venv/bin/python" ]; then
    echo "$admin_root/.venv/bin/python"
  elif command -v python3 >/dev/null 2>&1; then
    command -v python3
  else
    command -v python
  fi
}

website_run_manage() {
  local root="${WEBSITE_ROOT:-$(website_root)}"
  local py="${WEBSITE_PYTHON:-$(website_detect_python "$root")}"
  export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-apps.settings.dev}"
  cd "$root" || exit 1
  "$py" manage.py "$@"
}

website_ensure_venv() {
  local root="${WEBSITE_ROOT:-$(website_root)}"
  local py="${WEBSITE_PYTHON:-$(website_detect_python "$root")}"
  if [ ! -x "$py" ] || [ "$py" = "python" ] || [ "$py" = "$(command -v python3 2>/dev/null)" ]; then
    if [ ! -d "$root/.venv" ]; then
      echo "[website] 创建虚拟环境 .venv ..."
      python3 -m venv "$root/.venv" 2>/dev/null || python -m venv "$root/.venv"
    fi
    py="$(website_detect_python "$root")"
  fi
  WEBSITE_PYTHON="$py"
  export WEBSITE_PYTHON
}

website_install_deps() {
  local root="${WEBSITE_ROOT:-$(website_root)}"
  website_ensure_venv
  local py="${WEBSITE_PYTHON:-$(website_detect_python "$root")}"
  echo "[website] 安装依赖 requirements.txt ..."
  "$py" -m pip install --upgrade pip
  "$py" -m pip install -r "$root/requirements.txt"
}

website_has_env() {
  local root="${WEBSITE_ROOT:-$(website_root)}"
  [ -f "$root/.env" ]
}

website_bootstrap_env() {
  website_ensure_venv
  echo "[website] 生成/同步 .env ..."
  website_run_manage check --skip-checks 2>/dev/null || website_run_manage check
}

website_usage() {
  cat <<'EOF'
小西瓜CMS 前台运维脚本

用法: ./scripts/website.sh <命令> [参数...]

命令:
  install          创建 .venv 并安装 pip 依赖
  init-env         从 .env.example 生成/补全 .env（并同步 admin-backend 数据库配置）
  start [地址]     启动开发服务（默认 0.0.0.0:8088，无 .env 时自动生成）
  prod-start [地址] 以生产配置启动（apps.settings.prod，默认 0.0.0.0:8088）
  check            Django 配置检查
  help             显示本帮助

环境变量:
  HOST             默认绑定地址（默认 0.0.0.0）
  PORT             默认端口（默认 8088）
  DJANGO_SETTINGS_MODULE  dev 命令默认 apps.settings.dev

说明:
  - 首次部署请先完成 admin-backend: ./scripts/xxgcms.sh setup
  - 若无本地 .venv，会尝试使用 ../admin-backend/.venv

示例:
  ./scripts/website.sh install
  ./scripts/website.sh start
  ./scripts/start.sh
  ./scripts/website.sh prod-start 0.0.0.0:8088
EOF
}
