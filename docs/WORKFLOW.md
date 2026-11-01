# Workflow architecture

`workflows/mimo_qwen_wan_i2v.json` is one ComfyUI UI workflow with two official
subgraphs and four small outer nodes.

## Outer graph

| Node | Type | Purpose |
|---|---|---|
| 1000 | `LLMSessionChatSimpleNode` | Runs MiMo GGUF locally inside ComfyUI. Outputs one JSON prompt plan. |
| 1001 | `PromptJSONSplit` | Splits the JSON into image/video/negative prompt strings. |
| 1002 | `UnloadLLMModelNode` | Releases the MiMo llama.cpp model before the image model loads. |
| 1003 | Qwen-Image 2.1 subgraph | Text-to-image, outputs `IMAGE`. |
| 1006 | `SaveImageAdvanced` | Saves the generated still. |
| 1004 | `UnloadAllModels` | Releases Qwen/T5/VAE models before Wan loads. |
| 1005 | Wan2.2 I2V subgraph | Image + video prompt, outputs `VIDEO`. |
| 1007 | `SaveVideo` | Saves the generated video. |

## Execution order

```text
1000 LLM
 ├─ 1002 Unload LLM (triggered by LLM output)
 └─ 1001 Prompt JSON Split (also waits for 1002's trigger)
       └─ 1003 Qwen image
             ├─ 1006 SaveImage
             └─ 1004 UnloadAllModels
                   └─ 1005 Wan I2V
                         └─ 1007 SaveVideo
```

`PromptJSONSplit` receives both `text` and a `trigger` from the unload node, so
the image model cannot start before the LLM unload has run. Likewise the Wan
subgraph's `start_image` comes from `UnloadAllModels`, not directly from the
Qwen subgraph.

## Qwen prompt enhancer removed

The official Qwen Image 2.1 template contains an optional 9B prompt-enhancer
branch. ComfyUI evaluates both switch branches, which would load the extra
9B model even with the switch off. `scripts/build_workflow.py` removes nodes
471-475 and connects the subgraph `prompt` input directly to
`TextEncodeQwenImage21`. MiMo is the only prompt planner.

## VRAM notes

- 12GB laptop GPUs are the target; the unload nodes are not optional.
- MiMo Q5 + Qwen Image + Wan 2.2 cannot be resident together.
- If the Wan stage OOMs, reduce:
  - width/height in the Wan subgraph (default 640x640),
  - frame count (`81` in `WanImageToVideo`),
  - sampling steps.
- If the Qwen stage OOMs, lower the Qwen resolution or use the `w4a8` text
  encoder variant instead of `int8_convrot`.
