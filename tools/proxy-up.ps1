# ================================
# Proxy 一键更新脚本
# ================================

param(
    [string]$ProxyHost = "proxy.xxx.co.jp",
    [int]$ProxyPort = 8080,
    [string]$Username,
    [string]$Password
)

# ==== 1. 生成 proxy URL ====
$proxy = "http://$Username`:$Password@$ProxyHost`:$ProxyPort"

Write-Host "Proxy = $proxy" -ForegroundColor Green

# ================================
# 2. Windows 环境变量
# ================================
Write-Host "`n[1] 更新 Windows 环境变量..." -ForegroundColor Cyan

# User 级别
[Environment]::SetEnvironmentVariable("HTTP_PROXY", $proxy, "User")
[Environment]::SetEnvironmentVariable("HTTPS_PROXY", $proxy, "User")

# System 级别（需要管理员权限）
try {
    [Environment]::SetEnvironmentVariable("HTTP_PROXY", $proxy, "Machine")
    [Environment]::SetEnvironmentVariable("HTTPS_PROXY", $proxy, "Machine")
    Write-Host "✔ System 环境变量已更新"
} catch {
    Write-Host "⚠ System 环境变量更新失败（可能需要管理员权限）"
}

# ================================
# 3. Git Proxy
# ================================
Write-Host "`n[2] 更新 Git Proxy..." -ForegroundColor Cyan

git config --global http.proxy $proxy
git config --global https.proxy $proxy

Write-Host "✔ Git proxy 已更新"

# ================================
# 4. Conda + pip
# ================================
Write-Host "`n[3] 更新 Conda + pip..." -ForegroundColor Cyan

# 找到 conda 环境路径
$condaPrefix = $env:CONDA_PREFIX

if (-not $condaPrefix) {
    Write-Host "⚠ 当前未激活 conda 环境，跳过 pip 配置"
} else {
    $pipConfigPath = "$condaPrefix\pip.ini"

    Write-Host "pip config path: $pipConfigPath"

    $content = @"
[global]
proxy = $proxy
"@

    $content | Out-File -Encoding ASCII -FilePath $pipConfigPath

    Write-Host "✔ pip proxy 已写入 conda 环境"
}

# ================================
# 5. 当前 session 环境变量（立即生效）
# ================================
Write-Host "`n[4] 更新当前 PowerShell Session..." -ForegroundColor Cyan

$env:HTTP_PROXY = $proxy
$env:HTTPS_PROXY = $proxy

Write-Host "✔ 当前 session 生效"

# ================================
# 完成
# ================================
Write-Host "`n🎉 Proxy 全部更新完成！" -ForegroundColor Green