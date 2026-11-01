param(
    [string]$ComfyRoot = "D:\AI\ComfyUI\ComfyUI_windows_portable"
)

$ErrorActionPreference = "Stop"
$ComfyDir = Join-Path $ComfyRoot "ComfyUI"
$CustomDir = Join-Path $ComfyDir "custom_nodes"
$Python = Join-Path $ComfyRoot "python_embeded\python.exe"
if (-not (Test-Path $Python)) {
    $Python = Join-Path $ComfyRoot "python_embeded\python.exe"
}
if (-not (Test-Path $Python)) {
    throw "ComfyUI embedded Python not found under $ComfyRoot"
}
New-Item -ItemType Directory -Force $CustomDir | Out-Null

$repos = @(
    @{ Url = "https://github.com/kantan-kanto/ComfyUI-LLM-Session.git"; Name = "ComfyUI-LLM-Session" },
    @{ Url = "https://github.com/SeanScripts/ComfyUI-Unload-Model.git"; Name = "ComfyUI-Unload-Model" }
)
foreach ($repo in $repos) {
    $dest = Join-Path $CustomDir $repo.Name
    if (-not (Test-Path $dest)) {
        git clone --depth 1 $repo.Url $dest
    }
}

# Install the node package shipped in this repository.
$nodeSrc = Join-Path $PSScriptRoot "..\custom_nodes\comfyui-mimo-pipeline"
$nodeDst = Join-Path $CustomDir "comfyui-mimo-pipeline"
if (Test-Path $nodeDst) { Remove-Item $nodeDst -Recurse -Force }
Copy-Item $nodeSrc $nodeDst -Recurse

& $Python -m pip install --upgrade pip
& $Python -m pip install -r (Join-Path $CustomDir "ComfyUI-LLM-Session\requirements.txt")

Write-Host "Custom nodes installed under $CustomDir"
Write-Host "For CUDA acceleration of llama-cpp-python, use a JamePeng prebuilt wheel matching $Python."
