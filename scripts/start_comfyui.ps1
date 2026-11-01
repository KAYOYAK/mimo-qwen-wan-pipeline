param(
    [string]$ComfyRoot = "D:\AI\ComfyUI\ComfyUI_windows_portable",
    [int]$Port = 8188
)

$ErrorActionPreference = "Stop"
$Python = Join-Path $ComfyRoot "python_embeded\python.exe"
$Main = Join-Path $ComfyRoot "ComfyUI\main.py"
if (-not (Test-Path $Python)) { throw "Python not found: $Python" }
if (-not (Test-Path $Main)) { throw "ComfyUI main.py not found: $Main" }

Set-Location (Join-Path $ComfyRoot "ComfyUI")
& $Python -s main.py --listen 127.0.0.1 --port $Port
