#!/usr/bin/env bash
set -euo pipefail

# 用法:
#   bash set_proxy.sh http://user:pass@proxy.example.com:8080 "localhost,127.0.0.1,::1"
#
# 第1个参数: PROXY_URL
# 第2个参数: NO_PROXY (可选)

PROXY_URL="${1:-}"
NO_PROXY_VALUE="${2:-localhost,127.0.0.1,::1}"

if [[ -z "${PROXY_URL}" ]]; then
  echo "用法: bash set_proxy.sh <PROXY_URL> [NO_PROXY]"
  echo '例子: bash set_proxy.sh "http://user:pass@proxy.xxx.co.jp:8080" "localhost,127.0.0.1,::1,.example.com"'
  exit 1
fi

BASHRC="${HOME}/.bashrc"
DOCKER_CLIENT_CONFIG_DIR="${HOME}/.docker"
DOCKER_CLIENT_CONFIG_FILE="${DOCKER_CLIENT_CONFIG_DIR}/config.json"

echo "==> PROXY_URL=${PROXY_URL}"
echo "==> NO_PROXY=${NO_PROXY_VALUE}"

backup_file() {
  local file="$1"
  if [[ -f "$file" ]]; then
    cp "$file" "${file}.bak.$(date +%Y%m%d%H%M%S)"
  fi
}

ensure_line_in_file() {
  local file="$1"
  local key="$2"
  local line="$3"

  touch "$file"

  if grep -qE "^[[:space:]]*export[[:space:]]+${key}=" "$file"; then
    sed -i "s|^[[:space:]]*export[[:space:]]\+${key}=.*|${line}|g" "$file"
  else
    echo "$line" >> "$file"
  fi
}

detect_os() {
  if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_ID="${ID:-}"
    OS_LIKE="${ID_LIKE:-}"
  else
    echo "无法识别系统：/etc/os-release 不存在"
    exit 1
  fi

  if [[ "${OS_ID}" == "ubuntu" ]]; then
    echo "ubuntu"
    return
  fi

  if [[ "${OS_ID}" == "ol" || "${OS_ID}" == "oracle" || "${OS_LIKE}" == *"rhel"* ]]; then
    # 这里不绝对等于 Oracle Linux，但常见 Oracle Linux 会匹配到
    if grep -qi "oracle" /etc/os-release; then
      echo "oraclelinux"
      return
    fi
  fi

  echo "unknown"
}

update_bashrc() {
  echo "==> 更新 ~/.bashrc"
  backup_file "${BASHRC}"

  ensure_line_in_file "${BASHRC}" "http_proxy"  "export http_proxy=\"${PROXY_URL}\""
  ensure_line_in_file "${BASHRC}" "https_proxy" "export https_proxy=\"${PROXY_URL}\""
  ensure_line_in_file "${BASHRC}" "HTTP_PROXY"  "export HTTP_PROXY=\"${PROXY_URL}\""
  ensure_line_in_file "${BASHRC}" "HTTPS_PROXY" "export HTTPS_PROXY=\"${PROXY_URL}\""
  ensure_line_in_file "${BASHRC}" "no_proxy"    "export no_proxy=\"${NO_PROXY_VALUE}\""
  ensure_line_in_file "${BASHRC}" "NO_PROXY"    "export NO_PROXY=\"${NO_PROXY_VALUE}\""
}

update_docker_client() {
  echo "==> 更新 Docker client: ${DOCKER_CLIENT_CONFIG_FILE}"
  mkdir -p "${DOCKER_CLIENT_CONFIG_DIR}"
  backup_file "${DOCKER_CLIENT_CONFIG_FILE}"

  cat > "${DOCKER_CLIENT_CONFIG_FILE}" <<EOF
{
  "proxies": {
    "default": {
      "httpProxy": "${PROXY_URL}",
      "httpsProxy": "${PROXY_URL}",
      "noProxy": "${NO_PROXY_VALUE}"
    }
  }
}
EOF
}

update_docker_daemon() {
  echo "==> 更新 Docker daemon systemd proxy"
  local dir="/etc/systemd/system/docker.service.d"
  local file="${dir}/http-proxy.conf"

  sudo mkdir -p "${dir}"
  if sudo test -f "${file}"; then
    sudo cp "${file}" "${file}.bak.$(date +%Y%m%d%H%M%S)"
  fi

  sudo tee "${file}" > /dev/null <<EOF
[Service]
Environment="HTTP_PROXY=${PROXY_URL}"
Environment="HTTPS_PROXY=${PROXY_URL}"
Environment="NO_PROXY=${NO_PROXY_VALUE}"
EOF

  sudo systemctl daemon-reload
  sudo systemctl restart docker
}

update_apt_proxy() {
  echo "==> 更新 apt proxy"
  local file="/etc/apt/apt.conf.d/95proxies"

  if sudo test -f "${file}"; then
    sudo cp "${file}" "${file}.bak.$(date +%Y%m%d%H%M%S)"
  fi

  sudo tee "${file}" > /dev/null <<EOF
Acquire::http::Proxy "${PROXY_URL}";
Acquire::https::Proxy "${PROXY_URL}";
EOF
}

update_dnf_proxy() {
  echo "==> 更新 dnf proxy"
  local file="/etc/dnf/dnf.conf"

  if sudo test -f "${file}"; then
    sudo cp "${file}" "${file}.bak.$(date +%Y%m%d%H%M%S)"
  fi

  if sudo grep -qE '^[[:space:]]*proxy=' "${file}"; then
    sudo sed -i "s|^[[:space:]]*proxy=.*|proxy=${PROXY_URL}|g" "${file}"
  else
    echo "" | sudo tee -a "${file}" > /dev/null
    echo "proxy=${PROXY_URL}" | sudo tee -a "${file}" > /dev/null
  fi
}

main() {
  OS_TYPE="$(detect_os)"
  echo "==> 检测到系统: ${OS_TYPE}"

  update_bashrc
  update_docker_client
  update_docker_daemon

  case "${OS_TYPE}" in
    ubuntu)
      update_apt_proxy
      ;;
    oraclelinux)
      update_dnf_proxy
      ;;
    *)
      echo "==> 未识别为 Ubuntu / Oracle Linux，跳过 apt/dnf proxy 配置"
      ;;
  esac

  echo
  echo "完成。"
  echo "bash 环境变量执行下面命令生效："
  echo "  source ~/.bashrc"
  echo
  echo "检查 Docker daemon proxy："
  echo "  systemctl show --property=Environment docker"
  echo
  echo "检查 Docker client proxy："
  echo "  cat ~/.docker/config.json"
}

main