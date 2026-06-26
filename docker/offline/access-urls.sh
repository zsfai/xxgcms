#!/usr/bin/env bash
# 安装完成后打印可访问 URL（使用本机 IP，避免误导性的 localhost）

detect_host_ip() {
  local ip=""

  if command -v ip >/dev/null 2>&1; then
    ip="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i == "src") { print $(i + 1); exit }}' || true)"
  fi

  if [[ -z "${ip}" || "${ip}" == "127.0.0.1" ]]; then
    ip="$(hostname -I 2>/dev/null | awk '{for (i = 1; i <= NF; i++) if ($i != "127.0.0.1") { print $i; exit }}' || true)"
  fi

  if [[ -z "${ip}" ]]; then
    ip="<本机IP>"
  fi

  printf '%s' "${ip}"
}

read_site_host_from_env() {
  local env_file="$1"
  local site_name=""

  if [[ -n "${env_file}" && -f "${env_file}" ]]; then
    site_name="$(grep -E '^XXGCMS_CMS_SITE_NAME=' "${env_file}" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"'"'"'"'"' " || true)"
  fi

  case "${site_name}" in
    ''|localhost|127.0.0.1|localhost:*|127.0.0.1:*)
      printf '%s' ""
      ;;
    *)
      printf '%s' "${site_name%%:*}"
      ;;
  esac
}

print_access_urls() {
  local env_file="${1:-}"
  local host_ip domain

  host_ip="$(detect_host_ip)"
  domain="$(read_site_host_from_env "${env_file}")"

  echo " 访问地址（请用服务器 IP 或已在后台配置的域名；localhost 仅本机可用）:"
  echo "   站点前台: http://${host_ip}/"
  echo "   管理后台: http://${host_ip}/back-x/"
  echo "   API:      http://${host_ip}/api/"

  if [[ -n "${domain}" && "${domain}" != "${host_ip}" ]]; then
    echo "   环境站点名: ${domain}（DNS 指向本机后可用 http://${domain}/ 访问）"
  fi

  if [[ "${host_ip}" == "<本机IP>" ]]; then
    echo "   提示: 执行「hostname -I」或「ip -4 addr」查看本机 IP"
  elif [[ -z "${domain}" ]]; then
    echo "   提示: 在后台「站点管理」配置域名并启用 HTTPS 后，可用 https://域名/ 访问"
  fi
}
