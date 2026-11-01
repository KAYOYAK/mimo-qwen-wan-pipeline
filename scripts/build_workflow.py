#!/usr/bin/env python3
"""Build the single-file workflow from the official ComfyUI subgraph templates.

The official templates are UI workflows that wrap the Qwen-Image and Wan2.2
graphs in subgraph definitions. We keep those definitions unchanged and add:

  LLM Session Chat (Simple) -> Prompt JSON Split -> Qwen subgraph
      -> Unload All Models -> Wan I2V subgraph -> SaveImage / SaveVideo

The generated workflow uses local nodes only. It does not use Comfy Cloud or
any remote API.
"""

from __future__ import annotations

import argparse
import copy
import json
import uuid
from pathlib import Path

QWEN_TYPE = "c291ceec-b98f-4751-9d0b-7bc288f27b30"
WAN_TYPE = "84e2cf3f-de93-40ef-ab22-b9375296917b"
MODEL_NAME = "MiMo-V2.6-Distill-Qwen-9B-Q5_K_M.gguf"

USER_TEXT = """You are the prompt planner for a local text-to-image-to-video pipeline.
Return ONLY a JSON object, no markdown, with exactly these keys:
{"image_prompt": "...", "video_prompt": "...", "negative_prompt": "..."}

- image_prompt: a detailed English prompt for Qwen-Image 2.1 Turbo. Describe the subject, composition, lighting, style, and camera angle.
- video_prompt: an English prompt for Wan2.2 I2V. Describe the motion and camera movement, starting from the generated image.
- negative_prompt: short English list of things to avoid.
- Keep everything safe-for-work and suitable for a public demo.

User idea:
"""


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def find_node(nodes: list[dict], node_type: str) -> dict:
    for node in nodes:
        if node.get("type") == node_type:
            return node
    raise KeyError(f"node type not found: {node_type}")


def blank(node: dict, node_id: int, pos: list[float]) -> dict:
    out = copy.deepcopy(node)
    out["id"] = node_id
    out["pos"] = pos
    out["order"] = 0
    out["mode"] = 0
    out["flags"] = {}
    for port in out.get("inputs", []):
        port["link"] = None
    for port in out.get("outputs", []):
        port["links"] = []
    return out


def add_link(wf: dict, link_id: int, origin: dict, origin_slot: int,
             target: dict, target_slot: int, link_type: str) -> None:
    wf["links"].append([link_id, origin["id"], origin_slot, target["id"], target_slot, link_type])
    target["inputs"][target_slot]["link"] = link_id
    origin["outputs"][origin_slot].setdefault("links", []).append(link_id)


def strip_qwen_prompt_enhancer(subgraph: dict) -> None:
    """Remove the optional Qwen prompt-enhancer branch.

    MiMo replaces it. The official subgraph evaluates both switch branches, so
    leaving the enhancer in would load an extra 9B text model even when the
    switch is off.
    """
    removed_nodes = {471, 472, 473, 474, 475}
    subgraph["nodes"] = [n for n in subgraph["nodes"] if n.get("id") not in removed_nodes]
    removed_links = set()
    kept_links = []
    for link in subgraph.get("links", []):
        if link.get("origin_id") in removed_nodes or link.get("target_id") in removed_nodes:
            removed_links.add(link.get("id"))
        else:
            kept_links.append(link)
    subgraph["links"] = kept_links

    text_encode = next(n for n in subgraph["nodes"] if n.get("id") == 452)
    # Subgraph input prompt is (-10, slot 0); TextEncodeQwenImage21 prompt is slot 3.
    new_link_id = 900
    subgraph["links"].append({
        "id": new_link_id,
        "origin_id": -10,
        "origin_slot": 0,
        "target_id": 452,
        "target_slot": 3,
        "type": "STRING",
    })
    text_encode["inputs"][3]["link"] = new_link_id
    for node in subgraph["nodes"]:
        for inp in node.get("inputs", []):
            if inp.get("link") in removed_links:
                inp["link"] = None
        for out in node.get("outputs", []):
            if isinstance(out.get("links"), list):
                out["links"] = [lid for lid in out["links"] if lid not in removed_links]


def build(qwen_path: str, wan_path: str) -> dict:
    qwen = load(qwen_path)
    wan = load(wan_path)
    strip_qwen_prompt_enhancer(qwen["definitions"]["subgraphs"][0])
    qwen_nodes = qwen["nodes"]
    wan_nodes = wan["nodes"]

    qwen_instance = blank(find_node(qwen_nodes, QWEN_TYPE), 1003, [420, -120])
    qwen_save = blank(find_node(qwen_nodes, "SaveImageAdvanced"), 1006, [1150, -120])
    wan_instance = blank(find_node(wan_nodes, WAN_TYPE), 1005, [1150, 420])
    wan_save = blank(find_node(wan_nodes, "SaveVideo"), 1007, [1600, 420])

    llm = {
        "id": 1000,
        "type": "LLMSessionChatSimpleNode",
        "pos": [20, -420],
        "size": [380, 380],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": [
            {"localized_name": "user_text", "name": "user_text", "type": "STRING", "widget": {"name": "user_text"}, "link": None},
            {"localized_name": "session_id", "name": "session_id", "type": "STRING", "widget": {"name": "session_id"}, "link": None},
            {"localized_name": "model", "name": "model", "type": "COMBO", "widget": {"name": "model"}, "link": None},
            {"localized_name": "mmproj", "name": "mmproj", "type": "COMBO", "widget": {"name": "mmproj"}, "link": None},
            {"localized_name": "history_dir", "name": "history_dir", "type": "STRING", "widget": {"name": "history_dir"}, "link": None},
            {"localized_name": "config_path", "name": "config_path", "shape": 7, "type": "STRING", "widget": {"name": "config_path"}, "link": None},
        ],
        "outputs": [{"localized_name": "assistant_text", "name": "assistant_text", "type": "STRING", "links": []}],
        "properties": {"Node name for S&R": "LLMSessionChatSimpleNode"},
        "widgets_values": [USER_TEXT, "mimo-pipeline", MODEL_NAME, "(Not required)", "", ""],
    }

    split = {
        "id": 1001,
        "type": "PromptJSONSplit",
        "pos": [440, -420],
        "size": [300, 160],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": [
            {"localized_name": "text", "name": "text", "type": "STRING", "widget": {"name": "text"}, "link": None},
            {"localized_name": "trigger", "name": "trigger", "shape": 7, "type": "*", "link": None},
        ],
        "outputs": [
            {"localized_name": "image_prompt", "name": "image_prompt", "type": "STRING", "links": []},
            {"localized_name": "video_prompt", "name": "video_prompt", "type": "STRING", "links": []},
            {"localized_name": "negative_prompt", "name": "negative_prompt", "type": "STRING", "links": []},
        ],
        "properties": {"Node name for S&R": "PromptJSONSplit"},
        "widgets_values": [""],
    }

    unload_llm = {
        "id": 1002,
        "type": "UnloadLLMModelNode",
        "pos": [760, -420],
        "size": [280, 58],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": [
            {"localized_name": "trigger", "name": "trigger", "shape": 7, "type": "*", "link": None},
            {"localized_name": "unload_now", "name": "unload_now", "type": "BOOLEAN", "widget": {"name": "unload_now"}, "link": None},
        ],
        "outputs": [{"localized_name": "trigger", "name": "trigger", "type": "*", "links": []}],
        "properties": {"Node name for S&R": "UnloadLLMModelNode"},
        "widgets_values": [True],
    }

    unload_all = {
        "id": 1004,
        "type": "UnloadAllModels",
        "pos": [900, 220],
        "size": [260, 58],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": [{"localized_name": "value", "name": "value", "type": "*", "link": None}],
        "outputs": [{"localized_name": "value", "name": "value", "type": "*", "links": []}],
        "properties": {"Node name for S&R": "UnloadAllModels"},
        "widgets_values": [],
    }

    nodes = [llm, split, unload_llm, qwen_instance, qwen_save, unload_all, wan_instance, wan_save]
    wf = {
        "id": str(uuid.uuid4()),
        "revision": 0,
        "last_node_id": max(n["id"] for n in nodes),
        "last_link_id": 9,
        "nodes": nodes,
        "links": [],
        "groups": [],
        "definitions": {
            "subgraphs": qwen["definitions"]["subgraphs"] + wan["definitions"]["subgraphs"]
        },
        "config": {},
        "extra": {},
        "version": 0.4,
    }

    add_link(wf, 1, llm, 0, split, 0, "STRING")
    add_link(wf, 2, llm, 0, unload_llm, 0, "*")
    add_link(wf, 3, unload_llm, 0, split, 1, "*")
    add_link(wf, 4, split, 0, qwen_instance, 0, "STRING")
    add_link(wf, 5, split, 1, wan_instance, 1, "STRING")
    add_link(wf, 6, qwen_instance, 0, qwen_save, 0, "IMAGE")
    add_link(wf, 7, qwen_instance, 0, unload_all, 0, "IMAGE")
    add_link(wf, 8, unload_all, 0, wan_instance, 0, "IMAGE")
    add_link(wf, 9, wan_instance, 0, wan_save, 0, "VIDEO")
    return wf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qwen-template", required=True)
    parser.add_argument("--wan-template", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = build(args.qwen_template, args.wan_template)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out} ({len(result['nodes'])} nodes, {len(result['links'])} links)")


if __name__ == "__main__":
    main()
