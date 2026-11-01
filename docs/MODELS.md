# Models

All weights stay local. They are **not** committed to this repository.

## LLM

| File | Approx size | Where |
|---|---:|---|
| `MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf` | 6.0 GB | user-provided local GGUF, `ComfyUI/models/LLM/` |

MiMo is used only for prompt expansion and JSON planning. The mmproj file is not needed for this text-only pipeline.

## Image: Qwen-Image 2.1 Turbo

Source: [Comfy-Org/Qwen-Image-2.1](https://huggingface.co/Comfy-Org/Qwen-Image-2.1)

| File | Size |
|---|---:|
| `diffusion_models/qwen_image_2.1_turbo_int8_convrot.safetensors` | 6.76 GiB |
| `text_encoders/qwen3vl_8b_int8_convrot.safetensors` | 8.71 GiB |
| `vae/qwen_image_2.1_vae_bf16.safetensors` | 0.63 GiB |

Use the official `qwen3vl_8b` text encoder. The separate `qwen3.5_9b_qwen_image_2.1_pe` model is an optional prompt enhancer; this project uses MiMo instead and does not download it.

## Video: Wan2.2 I2V 14B

Source: [Comfy-Org/Wan_2.2_ComfyUI_Repackaged](https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged)

| File | Size |
|---|---:|
| `diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` | 13.31 GiB |
| `diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors` | 13.31 GiB |
| `text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` | 6.27 GiB |
| `vae/wan_2.1_vae.safetensors` | 0.24 GiB |
| `loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors` | 1.14 GiB |
| `loras/wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors` | 1.14 GiB |

I2V is intentional: the Qwen image is the start frame. The T2V variant does not accept an image.

## Licenses

- Qwen-Image 2.1: check the model card on the Comfy-Org repository.
- Wan2.2: Alibaba Wan 2.2 license / Apache-2.0 as declared by the publisher.
- MiMo: check the XiaomiMiMo model card.

Do not use generated media to impersonate real people or to create non-consensual or unlawful content.
