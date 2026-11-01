param(
    [string]$ComfyRoot = "D:\AI\ComfyUI\ComfyUI_windows_portable",
    [string]$MiMoGguf = "D:\models\MiMo-9B-GGUF\MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf"
)

$ErrorActionPreference = "Stop"
$Models = Join-Path $ComfyRoot "ComfyUI\models"
if (-not (Test-Path $Models)) { throw "ComfyUI models directory not found: $Models" }

function Get-Model {
    param([string]$Url, [string]$RelativePath)
    $out = Join-Path $Models $RelativePath
    $parent = Split-Path $out -Parent
    New-Item -ItemType Directory -Force $parent | Out-Null
    if (Test-Path $out) {
        Write-Host "skip existing: $RelativePath"
        return
    }
    Write-Host "download: $RelativePath"
    & curl.exe -L --retry 5 --retry-delay 5 -C - -o $out $Url
    if ($LASTEXITCODE -ne 0) { throw "download failed: $Url" }
}

$qwenRepo = "https://hf-mirror.com/Comfy-Org/Qwen-Image-2.1/resolve/main"
$wanRepo = "https://hf-mirror.com/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main"

Get-Model "$qwenRepo/diffusion_models/qwen_image_2.1_turbo_int8_convrot.safetensors" "diffusion_models\qwen_image_2.1_turbo_int8_convrot.safetensors"
Get-Model "$qwenRepo/text_encoders/qwen3vl_8b_int8_convrot.safetensors" "text_encoders\qwen3vl_8b_int8_convrot.safetensors"
Get-Model "$qwenRepo/vae/qwen_image_2.1_vae_bf16.safetensors" "vae\qwen_image_2.1_vae_bf16.safetensors"

Get-Model "$wanRepo/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors" "diffusion_models\wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"
Get-Model "$wanRepo/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors" "diffusion_models\wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"
Get-Model "$wanRepo/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors" "text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors"
Get-Model "$wanRepo/split_files/vae/wan_2.1_vae.safetensors" "vae\wan_2.1_vae.safetensors"
Get-Model "$wanRepo/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors" "loras\wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"
Get-Model "$wanRepo/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors" "loras\wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"

$llmDir = Join-Path $Models "LLM"
New-Item -ItemType Directory -Force $llmDir | Out-Null
$mimoDst = Join-Path $llmDir "MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf"
if (Test-Path $MiMoGguf) {
    if (-not (Test-Path $mimoDst)) {
        Write-Host "hardlink MiMo GGUF into models/LLM"
        New-Item -ItemType HardLink -Path $mimoDst -Target $MiMoGguf | Out-Null
    }
} else {
    Write-Host "MiMo GGUF not found at $MiMoGguf; place it at $mimoDst manually"
}

Write-Host "Model download complete."
