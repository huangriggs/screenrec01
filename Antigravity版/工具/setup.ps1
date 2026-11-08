param([switch]$Tts)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$local = Join-Path $root '.local-tools'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $local 'python'
$env:UV_CACHE_DIR = Join-Path $local 'uv-cache'
$env:UV_NO_PROGRESS = '1'
New-Item -ItemType Directory -Force -Path $local | Out-Null
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64' -and $env:PROCESSOR_ARCHITEW6432 -ne 'AMD64') {
    throw '本程式提供 Windows x64 安裝檔。ARM64 或其他架構請由 Agent 另行處理。'
}

function Download-Verified($Url, $Destination, $Sha256) {
    if (Test-Path -LiteralPath $Destination) {
        $oldHash = (Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($oldHash -eq $Sha256) { return }
        throw "既有下載檔 SHA256 驗證失敗：$Destination。請檢查後移除該檔再試。"
    }
    $partial = "$Destination.part"
    if (Test-Path -LiteralPath $partial) {
        throw "發現未完成的下載檔 $partial；請檢查後移除再試。"
    }
    try {
        Write-Host "Downloading $Url"
        & curl.exe --fail --location --silent --show-error --retry 2 --connect-timeout 30 --output $partial $Url
        if ($LASTEXITCODE -ne 0) { throw "下載失敗，結束碼 $LASTEXITCODE" }
        $actual = (Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -ne $Sha256) { throw "下載檔 SHA256 驗證失敗：$partial。" }
        Move-Item -LiteralPath $partial -Destination $Destination
    } catch {
        throw "$_ 請檢查網路並視情況移除未完成的下載檔。"
    }
}
function Check-Exit($Action) {
    if ($LASTEXITCODE -ne 0) { throw "$Action 失敗，結束碼 $LASTEXITCODE" }
}

$uvExe = Join-Path $local 'uv\uv.exe'
if (-not (Test-Path -LiteralPath $uvExe)) {
    $uvZip = Join-Path $local 'uv-0.13.7.zip'
    Download-Verified 'https://github.com/astral-sh/uv/releases/download/0.13.7/uv-x86_64-pc-windows-msvc.zip' $uvZip '0cdc5b38fe5a8168ed6a25814f5ba43c21d313dd3187314fccb37b7cec46e021'
    $uvExtract = Join-Path $local 'uv-extracted'
    Expand-Archive -LiteralPath $uvZip -DestinationPath $uvExtract -Force
    $foundUv = @(Get-ChildItem -LiteralPath $uvExtract -Filter uv.exe -Recurse -File)
    if ($foundUv.Count -ne 1) { throw 'uv 壓縮檔內容異常。' }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $uvExe) | Out-Null
    Copy-Item -LiteralPath $foundUv[0].FullName -Destination $uvExe
}

$venvPython = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $uvExe venv --python 3.12 --python-preference only-managed (Join-Path $root '.venv')
    Check-Exit '建立 Python 虛擬環境'
}
& $uvExe pip install --python $venvPython 'Pillow==12.3.0' 'edge-tts==7.3.1' 'imageio-ffmpeg==0.6.0' 'mutagen==1.47.0'
Check-Exit '安裝影片與旁白依賴'
& $venvPython -X utf8 (Join-Path $PSScriptRoot '檢查設備.py')
Check-Exit '設備檢查'
$name = '實作-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,6)
$output = Join-Path (Join-Path $root '成果') $name
$arguments = @('-X', 'utf8', (Join-Path $PSScriptRoot '製作示範.py'), '--output', $output)
if ($Tts) { $arguments += '--tts' }
& $venvPython @arguments
Check-Exit '製作影片'
Write-Host "OUTPUT: $output"
