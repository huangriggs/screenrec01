param([switch]$Tts)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$local = Join-Path $root '.local-tools'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $local 'python'
$env:UV_CACHE_DIR = Join-Path $local 'uv-cache'
$env:UV_NO_PROGRESS = '1'
New-Item -ItemType Directory -Force -Path $local | Out-Null
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64' -and $env:PROCESSOR_ARCHITEW6432 -ne 'AMD64') {
    throw '自動安裝目前僅提供 Windows x64；其他架構請依官方文件另行準備 Python 3.10 以上。'
}
function Check-Exit($Action) {
    if ($LASTEXITCODE -ne 0) { throw "$Action 失敗，結束碼 $LASTEXITCODE" }
}
$uvExe = Join-Path $local 'uv\uv.exe'
if (-not (Test-Path -LiteralPath $uvExe)) {
    $uvZip = Join-Path $local 'uv-0.13.7.zip'
    if (-not (Test-Path -LiteralPath $uvZip)) {
        $url = 'https://github.com/astral-sh/uv/releases/download/0.13.7/uv-x86_64-pc-windows-msvc.zip'
        Write-Host "Downloading $url"
        Invoke-WebRequest -Uri $url -OutFile $uvZip -UseBasicParsing
    }
    $hash = (Get-FileHash -LiteralPath $uvZip -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($hash -ne '0cdc5b38fe5a8168ed6a25814f5ba43c21d313dd3187314fccb37b7cec46e021') {
        throw 'uv 壓縮檔 SHA256 驗證失敗；請檢查網路及下載檔。'
    }
    $extract = Join-Path $local 'uv-extracted'
    Expand-Archive -LiteralPath $uvZip -DestinationPath $extract -Force
    $found = @(Get-ChildItem -LiteralPath $extract -Filter uv.exe -Recurse -File)
    if ($found.Count -ne 1) { throw 'uv 壓縮檔內容異常。' }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $uvExe) | Out-Null
    Copy-Item -LiteralPath $found[0].FullName -Destination $uvExe
}
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & $uvExe venv --python 3.12 --python-preference only-managed (Join-Path $root '.venv')
    Check-Exit '建立 Python 環境'
}
& $uvExe pip install --python $python -r (Join-Path $root 'requirements.txt')
Check-Exit '安裝環境套件'
& $python -X utf8 (Join-Path $PSScriptRoot '課前檢查.py')
Check-Exit '課前檢查'
$name = '示範-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,6) + '.mp4'
$output = Join-Path (Join-Path $root '示例\輸出') $name
$arguments = @('-X', 'utf8', (Join-Path $PSScriptRoot '產生示範.py'), '--config', (Join-Path $root '示例\認識因數.json'), '--output', $output)
if ($Tts) { $arguments += '--tts' }
& $python @arguments
Check-Exit '製作影片'
Write-Host "OUTPUT: $output"
