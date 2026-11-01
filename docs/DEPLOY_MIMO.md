# 本地部署 MiMo-V2.6-9B（llama.cpp）

本项目的第一个模型是 MiMo，负责把一句话扩写成图片提示词和视频提示词。
它有两条使用路径：

1. **独立 llama.cpp 服务**：`llama-server` 跑在 `127.0.0.1:8080`，用于验证模型、命令行调试、其他客户端；
2. **ComfyUI 内节点**：`ComfyUI-LLM-Session` 在 ComfyUI 进程内通过 llama.cpp backend 加载同一个 GGUF，单工作流默认使用这一种。

两条路径都用同一份 GGUF，不会同时占显存。

## 1. 准备 llama.cpp

从 [llama.cpp releases](https://github.com/ggml-org/llama.cpp/releases) 下载 Windows CUDA 发行包（或自行编译）：

```text
D:\llama.cpp\llama-b11270-bin-win-cuda-13.4-x64\llama-server.exe
```

要求版本支持 `qwen35` 架构。MiMo 是混合 QKV/SSM 结构，旧版 llama.cpp
会报 `tensor not found` 或 `arch mismatch`。

## 2. 准备 GGUF

```text
D:\models\MiMo-9B-GGUF\
├── MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf      # 主模型
└── mmproj-MiMo-V2.6-Distill-Qwen-9B-f16.gguf  # 可选，纯文本流程不需要
```

## 3. 方式一：独立 llama-server

CPU 模式（推荐：给 12GB 显存机器留满 VRAM 给 ComfyUI）：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_llama_server.ps1 `
  -GpuLayers 0
```

等价命令：

```powershell
& "D:\llama.cpp\llama-b11270-bin-win-cuda-13.4-x64\llama-server.exe" `
  -m "D:\models\MiMo-9B-GGUF\MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf" `
  --alias mimo-v2.6-distill-qwen-9b `
  --host 127.0.0.1 --port 8080 `
  --n-gpu-layers 0 --ctx-size 32768 --threads 8 `
  --jinja --reasoning-budget 0
```

GPU 模式仅用于单独验证：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_llama_server.ps1 `
  -GpuLayers 99
```

> 跑 ComfyUI 工作流前，如果 MiMo 用了 GPU，必须先停掉 llama-server，
> 否则会和 Qwen/Wan 抢 12GB 显存。

验证：

```powershell
Invoke-RestMethod http://127.0.0.1:8080/health

$body = @{
  model = "mimo-v2.6-distill-qwen-9b"
  messages = @(@{ role = "user"; content = "用一句话介绍你自己。" })
  max_tokens = 64
} | ConvertTo-Json -Depth 6

Invoke-RestMethod http://127.0.0.1:8080/v1/chat/completions `
  -Method Post -ContentType "application/json" `
  -Body ([Text.Encoding]::UTF8.GetBytes($body))
```

## 4. 方式二：ComfyUI 内 LLM 节点

工作流默认使用 [ComfyUI-LLM-Session](https://github.com/kantan-kanto/ComfyUI-LLM-Session)：

- 节点：`LLM Session Chat (Simple)`
- 后端：`llama-cpp-python`
- 卸载：`Unload LLM Model`

### 4.1 安装匹配的 llama-cpp-python

MiMo 的 `qwen35` 架构需要较新的 llama.cpp backend。本项目在
Python 3.13 + CUDA 13.0 环境使用 JamePeng 的预编译 wheel：

```text
llama_cpp_python-0.4.5+cu130-cp313-cp313-win_amd64.whl
```

下载地址：

```text
https://github.com/JamePeng/llama-cpp-python/releases
```

选择与本机 Python/ CUDA 匹配的 wheel，然后：

```powershell
$py = "D:\AI\ComfyUI\standalone\standalone-env\python.exe"
& $py -m pip install "D:\path\to\llama_cpp_python-0.4.5+cu130-cp313-cp313-win_amd64.whl"
```

如果使用便携版：

```powershell
D:\AI\ComfyUI\ComfyUI_windows_portable\python_embeded\python.exe -m pip install ...
```

### 4.2 放入 GGUF

```text
ComfyUI/models/LLM/MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf
```

`scripts/download_models.ps1` 会用硬链接把本地 GGUF 放进去。

### 4.3 节点参数

- `model`：`MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf`
- `mmproj`：留空（本流程只用文本）
- `user_text`：包含 JSON 输出要求的提示词模板
- `session_id`：`mimo-pipeline`
- `history_dir` / `config_path`：可留空

## 5. 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `model arch and LoRA arch mismatch` | 不是 MiMo 的问题；LoRA 架构不匹配 | 本流程不使用 LoRA |
| `tensor not found` / qwen35 报错 | llama.cpp 太旧 | 升级到支持 qwen35 的版本 |
| `llama_cpp` import fail | wheel 与 Python/CUDA 版本不匹配 | 选对应 cp313/cu130 wheel |
| 工作流到图片阶段 OOM | MiMo 仍占用 GPU | 用 `-GpuLayers 0` 或先停 llama-server |
| 想换成独立服务 | 工作流默认在 ComfyUI 内加载 | 用 `scripts/start_llama_server.ps1` 做命令行验证 |
