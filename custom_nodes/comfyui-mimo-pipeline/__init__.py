"""MiMo -> Qwen-Image -> Wan2.2 local pipeline helper nodes.

`PromptJSONSplit` turns the LLM's JSON response into three plain strings so the
downstream official Qwen/Wan subgraphs only need ordinary STRING inputs.
"""

from __future__ import annotations

import json
import re

DEFAULT_NEGATIVE = (
    "low quality, blurry, watermark, text overlay, distorted anatomy, "
    "duplicate limbs, flickering, oversaturated"
)


class PromptJSONSplit:
    """Parse a JSON prompt plan emitted by a local LLM."""

    CATEGORY = "MiMo Pipeline"
    FUNCTION = "split"
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("image_prompt", "video_prompt", "negative_prompt")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"text": ("STRING", {"multiline": True, "default": ""})},
            "optional": {"trigger": ("*",)},
        }

    @staticmethod
    def _extract_json(text: str):
        text = (text or "").strip()
        if not text:
            return None
        fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S | re.I)
        if fence:
            text = fence.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            return None
        try:
            value = json.loads(text[start : end + 1])
        except (TypeError, ValueError):
            return None
        return value if isinstance(value, dict) else None

    def split(self, text: str, trigger=None):
        data = self._extract_json(text) or {}
        image_prompt = str(data.get("image_prompt") or "").strip()
        video_prompt = str(data.get("video_prompt") or "").strip()
        negative_prompt = str(data.get("negative_prompt") or "").strip()

        # A malformed JSON response should still produce a usable workflow.
        fallback = (text or "").strip()
        if not image_prompt:
            image_prompt = fallback
        if not video_prompt:
            video_prompt = image_prompt
        if not negative_prompt:
            negative_prompt = DEFAULT_NEGATIVE
        return (image_prompt, video_prompt, negative_prompt)


NODE_CLASS_MAPPINGS = {"PromptJSONSplit": PromptJSONSplit}
NODE_DISPLAY_NAME_MAPPINGS = {"PromptJSONSplit": "Prompt JSON Split (MiMo)"}
