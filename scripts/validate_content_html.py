#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate WeChat-safe HTML and semantic marker density."""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ALLOWED = {"section", "p", "span", "strong", "br", "img", "blockquote", "table", "tbody", "tr", "td"}
STYLE_OPTIONAL = {"br", "tbody", "tr"}
ALLOWED_ATTRS = {"style", "src", "alt", "width", "height", "colspan", "rowspan"}
THEME_ACCENTS = {"#1746A2", "#123B5D", "#4B5563", "#A35A00"}
SEMANTIC_ACCENTS = {"#2F855A", "#B7791F", "#C53030", "#6B46C1"}
ACCENTS = THEME_ACCENTS | SEMANTIC_ACCENTS
KNOWN_COLORS = ACCENTS | {
    "#111827", "#1F2937", "#2A2E34", "#26313A", "#2B2F33", "#332C26", "#333333", "#555555",
    "#5A6068", "#666666", "#7B8792", "#7C8796", "#8A9099", "#8B9097", "#8C8176", "#A5A5A5",
    "#FFFFFF", "#F7F8FA", "#F4F7F9", "#F7F7F7", "#FAF7F2", "#ECEEF1", "#E5EAEE", "#E8E8E8",
    "#EEE4D7", "#D8D8D8", "#999999", "#888888", "#EAF0FA", "#E8F0F5", "#EEF0F2", "#F7ECDD",
    "#FFFDF8", "#FCFBF7", "#FCFCFA", "#FFF9F0", "#F0E7D8", "#D8DCE2", "#EAF6EF", "#FFF4D6",
    "#FDECEC", "#F2ECFB", "#FFF7C7", "#F1F2F4", "#BFD1EE", "#D9C8F0", "#A0A6AF", "#356B8C",
    "#D89A2B",
}


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.tags: list[str] = []
        self.attrs: list[tuple[str, list[tuple[str, str]]]] = []
        self.data: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag.lower())
        self.attrs.append((tag.lower(), [(key.lower(), value or "") for key, value in attrs]))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        self.data.append(data)

    def handle_entityref(self, name: str) -> None:
        self.data.append("&" + name + ";")

    def handle_charref(self, name: str) -> None:
        self.data.append("&#" + name + ";")


def plain(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)


def clen(value: str) -> int:
    return len(re.sub(r"\s+", "", plain(value)))


def font_size(style: str) -> int | None:
    match = re.search(r"font-size\s*:\s*(\d+)px", style or "", re.I)
    return int(match.group(1)) if match else None


def balanced_pairs(text: str) -> bool:
    pairs = [("“", "”"), ("‘", "’"), ("《", "》"), ("（", "）"), ("【", "】")]
    return all(text.count(left) == text.count(right) for left, right in pairs)


def semantic_types(inner: str) -> set[str]:
    types: set[str] = set()
    if "text-decoration:line-through" in inner:
        types.add("strike")
    if "border-bottom:2px solid" in inner:
        types.add("underline")
    if re.search(r"<span[^>]+background:", inner, re.I):
        types.add("highlight")
    return types


def validate(content_html: str, profile: str = "strict_draftbox") -> dict[str, object]:
    parser = Parser()
    parser.feed(content_html)
    text = "".join(parser.data)
    p0: list[str] = []
    p1: list[str] = []
    p2: list[str] = []

    for tag in parser.tags:
        if tag not in ALLOWED:
            p0.append(f"non allowed tag: <{tag}>")
        if tag in {"style", "script", "html", "head", "body", "div", "iframe", "svg", "video", "canvas", "form", "input", "button", "h1", "h2", "h3", "ul", "ol", "li"}:
            p0.append(f"forbidden tag: <{tag}>")

    for tag, attrs in parser.attrs:
        attr_dict = dict(attrs)
        if tag not in STYLE_OPTIONAL and "style" not in attr_dict:
            p0.append(f"no inline style: <{tag}>")
        for key, value in attrs:
            if key not in ALLOWED_ATTRS:
                p0.append(f"unknown attr: {key}")
            if key in {"class", "id"} or key.startswith("data-"):
                p0.append(f"forbidden attr: {key}")
            if key == "style" and not value.strip():
                p0.append(f"empty style attr: <{tag}>")
            if key.startswith("on"):
                p0.append(f"event attr: {key}")
            if re.search(r"javascript\s*:", value, re.I):
                p0.append("javascript: found")
            if key == "src" and ("base64" in value.lower() or value.lower().startswith("data:")):
                p0.append("base64 image")
            if key == "style":
                forbidden_styles = [
                    r"display\s*:\s*flex", r"display\s*:\s*grid", r"position\s*:\s*(absolute|fixed|sticky)",
                    r"animation\s*:", r"transition\s*:", r"@keyframes", r":hover", r"var\s*\(", r"url\s*\(\s*data:",
                ]
                for pattern in forbidden_styles:
                    if re.search(pattern, value, re.I):
                        p0.append("forbidden style " + pattern)

    for token in ("&ensp;", "&emsp;", "&nbsp;"):
        if token in content_html.lower():
            p0.append("space entity " + token)
    if re.search(r"^\s*#{1,6}\s|\*\*|```|^\s*\|[^\n]+\|\s*$", content_html, re.M):
        p0.append("Markdown source residue")
    if re.search(r"!\[[^\]]*\]|!示意图", content_html):
        p0.append("markdown image leak")
    if not balanced_pairs(text):
        p0.append("unbalanced paired punctuation")

    paragraphs = re.findall(r"<p\b([^>]*)>(.*?)</p>", content_html, re.S | re.I)
    body_lengths: list[int] = []
    inline_marked_paragraphs = 0
    for attrs, inner in paragraphs:
        content = plain(inner).strip()
        size = font_size(attrs)
        if size == 16 and "line-height:1.78" in attrs and "font-weight:700" not in attrs:
            body_lengths.append(clen(content))
        if re.match(r"^(图：|图片：|图片说明：|图注：|Caption：|caption:|资料图：|配图：)", content) and (not size or size > 13):
            p1.append("image caption not small text")
        if re.match(r"^(参考资料|资料来源|来源|免责声明|作者|版权|备注)[:：]", content) and (not size or size >= 14):
            p1.append("references not small text")
        if re.search(r"(关注我|扫码|领取资料|加微信|私信)", content) and (not size or size >= 14):
            p1.append("CTA too strong")
        marker_types = semantic_types(inner) if size == 16 and "line-height:1.78" in attrs else set()
        if marker_types:
            inline_marked_paragraphs += 1
        if len(marker_types) > 1:
            p1.append("multiple inline marker types in one paragraph")

    # Source paragraph length and rhythm are immutable. The pure-layout Skill
    # must not merge, split, shorten, or rewrite paragraphs to satisfy a score.
    if re.search(r"“[^”<]*</p>\s*<p[^>]*>[^“]*”", content_html):
        p1.append("quote split detected")
    if body_lengths and inline_marked_paragraphs > max(12, int(len(body_lengths) * 0.85)):
        p1.append("inline marker fatigue")

    gradient_count = len(re.findall(r"background:linear-gradient\(135deg", content_html, re.I))
    compare_count = len(re.findall(r"<table[^>]*>.*?(?:你以为|真实情况)", content_html, re.I | re.S))
    capsule_count = len(re.findall(r"border-radius:999px", content_html, re.I))
    color_block_count = len(re.findall(r"border-left:4px solid[^>]+border-radius:8px", content_html, re.I))
    if gradient_count > 1:
        p1.append("too many gradient emphasis bars")
    if compare_count > 2:
        p1.append("too many double compare blocks")
    if capsule_count > 4:
        p1.append("too many capsule labels")
    if color_block_count > max(2, clen(text) // 350):
        p1.append("too many color blocks")

    for table in re.findall(r"<table\b.*?</table>", content_html, re.S | re.I):
        rows = re.findall(r"<tr\b", table, re.I)
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", table, re.S | re.I)
        if len(rows) > 8 or (rows and len(cells) // max(1, len(rows)) > 3) or "<table" in table[6:].lower() or any(clen(cell) > 100 for cell in cells):
            p1.append("table too complex")

    all_colors: list[str] = []
    foreground_colors: list[str] = []
    for _, attrs in parser.attrs:
        style = dict(attrs).get("style", "")
        all_colors.extend(color.upper() for color in re.findall(r"#[0-9A-Fa-f]{6}\b", style))
        foreground_colors.extend(color.upper() for color in re.findall(r"(?<!background-)color\s*:\s*(#[0-9A-Fa-f]{6})", style, re.I))
        foreground_colors.extend(color.upper() for color in re.findall(r"border-(?:left|right|top|bottom)\s*:\s*\d+px\s+(?:solid|dashed|dotted)\s+(#[0-9A-Fa-f]{6})", style, re.I))
    unknown = set(all_colors) - KNOWN_COLORS
    used_accents = set(foreground_colors) & ACCENTS
    if unknown:
        p1.append("unknown accent colors")
    if len(used_accents) > 6:
        p1.append("too many semantic accent colors")

    return {"verdict": "fix_required" if p0 else "pass", "P0": sorted(set(p0)), "P1": sorted(set(p1)), "P2": sorted(set(p2))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("html_file")
    parser.add_argument("--profile", default="strict_draftbox")
    args = parser.parse_args()
    result = validate(Path(args.html_file).read_text(encoding="utf-8"), args.profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(1 if result["P0"] else 0)


if __name__ == "__main__":
    main()
