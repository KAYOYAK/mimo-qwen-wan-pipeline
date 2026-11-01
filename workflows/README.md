# Workflows

`mimo_qwen_wan_i2v.json` is the single workflow to open in ComfyUI.

It contains two subgraph definitions:

- `Text to Image (Qwen Image 2.1)`
- `Image to Video (Wan2.2)`

Load it with **Workflow → Open** in ComfyUI. The LLM node's `user_text` is the
only prompt you normally edit.

If you change the model filenames, edit the subgraph node widgets or regenerate
with `scripts/build_workflow.py` and the official ComfyUI templates.
