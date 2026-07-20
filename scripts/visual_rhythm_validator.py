#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Score mobile reading rhythm without treating capsules as full cards."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def score(content_html: str) -> dict[str, object]:
    text = re.sub(r"<[^>]+>", "", content_html)
    issues: list[str] = []
    value = 100
    checks = [
        ("empty bullet paragraph", r"<p[^>]*>\s*(?:<span[^>]*>)?\s*[•·●○▪▫◆◇]\s*(?:</span>)?\s*</p>", 18),
        ("module label found", r"模块\s*[一二三四五六七八九十0-9]|第一部分|第二部分|小节\s*\d+|Section\s*\d+", 12),
        ("skill meta content found", r"先把短句合并成自然段|再把重点句单独拎出来|Skill 元内容", 15),
        ("default CTA without signal", r"如果这篇对你有启发，可以点个在看|可以带走的做法", 10),
        ("markdown image leak", r"!\[[^\]]*\]|!示意图", 10),
        ("markdown table pipe leak", r"^\s*\|[^\n]+\|\s*$", 10),
        ("detached section number", r"<p[^>]*>\s*0[1-9]\s*</p>\s*<p[^>]*font-size\s*:\s*20px", 12),
        ("body title block rendered", r"font-size\s*:\s*22px[^>]*font-weight\s*:\s*700", 14),
    ]
    for name, pattern, penalty in checks:
        target = content_html if "markdown" in name or "detached" in name or "title" in name or "bullet" in name else text
        if re.search(pattern, target, re.I | re.M):
            issues.append(name)
            value -= penalty

    headings = len(re.findall(r"font-size\s*:\s*(?:19|20|21)px[^>]+font-weight\s*:\s*700", content_html, re.I))
    paragraphs = len(re.findall(r"<p\b", content_html, re.I))
    actual_cards = len(re.findall(r"<(?:section|blockquote)[^>]*(?:background:[^;\"]+;)[^>]*border-radius:(?:8|10)px", content_html, re.I))
    if headings < 2 and len(text) > 300:
        issues.append("heading beauty missing")
        value -= 8
    if actual_cards > max(2, len(text) // 300):
        issues.append("too many cards")
        value -= 8

    gradient_count = len(re.findall(r"background:linear-gradient\(135deg", content_html, re.I))
    compare_count = len(re.findall(r"<table[^>]*>.*?(?:你以为|真实情况)", content_html, re.I | re.S))
    capsule_count = len(re.findall(r"border-radius:999px", content_html, re.I))
    semantic_marks = len(re.findall(r"text-decoration:line-through|border-bottom:2px solid|<span[^>]+background:|border-left:4px solid", content_html, re.I))
    if gradient_count > 1:
        issues.append("too many gradient emphasis bars")
        value -= 8
    if compare_count > 2:
        issues.append("too many double compare blocks")
        value -= 6
    if capsule_count > 14:
        issues.append("capsule label fatigue")
        value -= 5
    if semantic_marks > max(18, paragraphs + 6):
        issues.append("semantic marker fatigue")
        value -= 6
    if re.search(r"background\s*:\s*#[0-9A-Fa-f]{6}[^>]+(关注|报名|领取|扫码)", content_html, re.I):
        issues.append("CTA too strong")
        value -= 10

    value = max(0, min(100, value))
    layout_pass = value >= 88 and not any(issue in issues for issue in ("body title block rendered", "too many cards"))
    return {
        "visual_score": value,
        "layout_rhythm": "pass" if layout_pass else "fail",
        "heading_beauty": "pass" if "heading beauty missing" not in issues and "module label found" not in issues else "fail",
        "component_balance": "pass" if "too many cards" not in issues else "fail",
        "cta_style": "pass" if "CTA too strong" not in issues and "default CTA without signal" not in issues else "fail",
        "issues": issues,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_file")
    args = parser.parse_args()
    print(json.dumps(score(Path(args.html_file).read_text(encoding="utf-8")), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
