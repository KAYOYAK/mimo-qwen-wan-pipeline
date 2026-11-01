param(
    [string]$LlamaCppDir = "D:\llama.cpp\llama-b11270-bin-win-cuda-13.4-x64",
    [string]$Model = "D:\models\MiMo-9B-GGUF\MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf",
    [string]$Mmproj = "D:\models\MiMo-9B-GGUF\mmproj-MiMo-V2.6-Distill-Qwen-9B-f16.gguf",
    [int]$Port = 8080,
    [int]$GpuLayers = 0,
    [int]$CtxSize = 32768
)

$ErrorActionPreference = "Stop"
$Server = Join-Path $LlamaCppDir "llama-server.exe"
if (-not (Test-Path $Server)) { throw "llama-server.exe not found: $Server" }
if (-not (Test-Path $Model)) { throw "GGUF not found: $Model" }

$Arguments = @(
    "-m", $Model,
    "--alias", "mimo-v2.6-distill-qwen-9b",
    "--host", "127.0.0.1",
    "--port", "$Port",
    "--threads", "8",
    "--threads-batch", "8",
    "--n-gpu-layers", "$GpuLayers",
    "--ctx-size", "$CtxSize",
    "--jinja",
    "--reasoning-budget", "0",
    "--temp", "0.6",
    "--top-p", "0.95",
    "--top-k", "20",
    "--min-p", "0",
    "--repeat-penalty", "1.0"
)

# CPU mode is the safe default: it leaves the full 12GB VRAM for ComfyUI.
# For a GPU-only benchmark, pass -GpuLayers 99, but stop this server before
# running the ComfyUI workflow.
if ($GpuLayers -ne 0) {
    $Arguments += @("--flash-attn", "on")
}

Write-Host "Starting MiMo with $GpuLayers GPU layers on http://127.0.0.1:$Port"
& $Server @Arguments
