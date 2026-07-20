#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build both WeChat HTML and the complete JSON payload."""
from __future__ import annotations

import argparse
import json
import sys
sys.dont_write_bytecode = True
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from md_to_wechat import compile_all


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output-dir", default="out")
    parser.add_argument("--profile", default="strict_draftbox", choices=["strict_draftbox", "rich_article"])
    parser.add_argument("--theme", default="auto", choices=["auto", "editorial", "business", "minimal", "course"])
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = input_path.read_text(encoding="utf-8")
    plan, rhythm, visual, tree, content_html, validation, visual_report, payload, fidelity, marker_report = compile_all(raw, args.profile, args.theme)
    result = {
        "article_plan": plan,
        "text_rhythm_plan": rhythm,
        "visual_plan": visual,
        "component_tree": tree,
        "content_html": content_html,
        "draftbox_payload": payload,
        "validation_report": validation,
        "visual_report": visual_report,
        "content_fidelity_report": fidelity,
        "semantic_marker_report": marker_report,
        "section_visual_coverage": payload.get("section_visual_coverage", {}),
    }
    stem = input_path.stem
    html_path = output_dir / f"{stem}.wechat.html"
    json_path = output_dir / f"{stem}.wechat.json"
    html_path.write_text(content_html, encoding="utf-8")
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failed = bool(validation.get("P0")) or fidelity.get("status") != "pass" or visual_report.get("visual_score", 0) < 88
    print(f"HTML: {html_path}")
    print(f"JSON: {json_path}")
    print(f"fidelity: {fidelity.get('status')}")
    print(f"visual_score: {visual_report.get('visual_score')}")
    print(f"validation_P0: {len(validation.get('P0', []))}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
