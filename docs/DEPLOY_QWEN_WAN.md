# 本地部署 Qwen-Image 与 Wan2.2

本项目的两个生成模型：

1. **Qwen-Image-2.1-Turbo**：文生图（T2I），生成视频的首帧；
2. **Wan2.2-I2V-A14B**：图生视频（I2V），读取首帧和视频提示词。

> 原始设想写的是 Wan2.2-T2V；但 T2V 不接收图片，无法实现“图片交给视频模型”。
> 所以本项目用 I2V。两者同属 Wan2.2 A14B 系列。

## 1. ComfyUI 版本

需要 ComfyUI **v0.43.0 或更新**，因为工作流用到：

- `TextEncodeQwenImage21`
- `QwenImage21Cache`
- `WanImageToVideo`
- `SaveVideo`
- 前端 subgraph

旧版（如 v0.34）节点不存在，工作流会缺节点。

## 2. Qwen-Image-2.1-Turbo 部署

来源：[Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1)

| 文件 | 大小 | 放置位置 |
|---|---:|---|
| `qwen_image_2.1_turbo_int8_convrot.safetensors` | 6.76 GiB | `ComfyUI/models/diffusion_models/` |
| `qwen3vl_8b_int8_convrot.safetensors` | 8.71 GiB | `ComfyUI/models/text_encoders/` |
| `qwen_image_2.1_vae_bf16.safetensors` | 0.63 GiB | `ComfyUI/models/vae/` |

下载：

```powershell
$q = "https://hf-mirror.com/Comfy-Org/Qwen-Image-2.1/resolve/main"
curl.exe -L -C - -o "ComfyUI\models\diffusion_models\qwen_image_2.1_turbo_int8_convrot.safetensors" "$q/diffusion_models/qwen_image_2.1_turbo_int8_convrot.safetensors"
curl.exe -L -C - -o "ComfyUI\models\text_encoders\qwen3vl_8b_int8_convrot.safetensors" "$q/text_encoders/qwen3vl_8b_int8_convrot.safetensors"
curl.exe -L -C - -o "ComfyUI\models\vae\qwen_image_2.1_vae_bf16.safetensors" "$q/vae/qwen_image_2.1_vae_bf16.safetensors"
```

节点配置：

- `UNETLoader`：`qwen_image_2.1_turbo_int8_convrot.safetensors`
- `CLIPLoader`：`qwen3vl_8b_int8_convrot.safetensors`，type=`qwen_image`
- `VAELoader`：`qwen_image_2.1_vae_bf16.safetensors`

不要把 `qwen3.5_9b_qwen_image_2.1_pe_t2i` 当成文本编码器：它是可选的
prompt enhancer。本项目用 MiMo 做提示词扩写，已经把它从官方子图中移除。

### 验证

1. 启动 ComfyUI；
2. 加载官方模板 `image_qwen_image_2_1_turbo_t2i.json`；
3. 输入 SFW 提示词，Queue，能出图即部署成功。

## 3. Wan2.2-I2V-A14B 部署

来源：[Comfy-Org/Wan_2.2_ComfyUI_Repackaged](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)

| 文件 | 大小 | 放置位置 |
|---|---:|---|
| `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` | 13.31 GiB | `models/diffusion_models/` |
| `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` | 13.31 GiB | `models/diffusion_models/` |
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | 6.27 GiB | `models/text_encoders/` |
| `wan_2.1_vae.safetensors` | 0.24 GiB | `models/vae/` |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` | 1.14 GiB | `models/loras/` |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | 1.14 GiB | `models/loras/` |

下载：

```powershell
$w = "https://hf-mirror.com/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main"
curl.exe -L -C - -o "ComfyUI\models\diffusion_models\wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors" "$w/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"
curl.exe -L -C - -o "ComfyUI\models\diffusion_models\wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors" "$w/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"
curl.exe -L -C - -o "ComfyUI\models\text_encoders\umt5_xxl_fp8_e4m3fn_scaled.safetensors" "$w/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors"
curl.exe -L -C - -o "ComfyUI\models\vae\wan_2.1_vae.safetensors" "$w/split_files/vae/wan_2.1_vae.safetensors"
curl.exe -L -C - -o "ComfyUI\models\loras\wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors" "$w/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors"
curl.exe -L -C - -o "ComfyUI\models\loras\wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors" "$w/split_files/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors"
```

### 验证

1. 启动 ComfyUI；
2. 加载官方模板 `video_wan2_2_14B_i2v.json`；
3. 用一张本地图 + SFW 视频提示词，生成短视频；
4. 能输出 VIDEO 即部署成功。

## 4. 下载经验

- 大模型优先 **ModelScope 单连接**，有时比多线程更快；HF 镜像作为备用；
- GitHub release 直连慢时用 `ghproxy.net`，并发过高会被限流；
- Windows curl 如遇证书吊销错误，加 `--ssl-no-revoke`；
- 本机没有 7z 时可用 Windows 自带 `tar`（bsdtar 支持 7z）或 `py7zr`；
- 模型总大小约 54GB，下载前确认磁盘空间。

## 5. 许可

- Qwen-Image 2.1：见 Comfy-Org 模型卡。
- Wan2.2：Alibaba Wan 2.2 / Apache-2.0（以发布方声明为准）。
- 不要把权重提交进 Git 仓库。
