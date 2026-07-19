#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compile Markdown/plain Chinese articles into WeChat-safe inline HTML.

The compiler is content-first: it preserves source wording and order, then adds
sparse inline styles according to the role of each sentence. It never changes source wording and never uses a
marker merely to fill visual space.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sanitize_wechat_html import sanitize as sanitize_wechat_html
from editorial_marker_library import render_library_component, source_payloads_for_library_component, source_triggered_component, library_marker_category
from validate_content_html import validate as validate_content_html
from visual_rhythm_validator import score as visual_rhythm_score

FF = "-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei','Helvetica Neue',Arial,sans-serif"

# Mutable theme tokens. apply_theme() sets these before rendering.
ACCENT = "#1746A2"
TEXT = "#2A2E34"
GREY = "#8A9099"
PALE = "#F7F8FA"
BLUE_BG = "#EAF0FA"
WARM = "#FFFDF8"
LINE = "#ECEEF1"
GRADIENT_START = "#1746A2"
GRADIENT_END = "#6B46C1"

GREEN = "#2F855A"
GREEN_BG = "#EAF6EF"
ORANGE = "#B7791F"
ORANGE_BG = "#FFF4D6"
RED = "#C53030"
RED_BG = "#FDECEC"
PURPLE = "#6B46C1"
PURPLE_BG = "#F2ECFB"
YELLOW_BG = "#FFF7C7"
GREY_BG = "#F1F2F4"

CAPTION_PREFIXES = ("图：", "图片：", "图片说明：", "图注：", "Caption：", "caption:", "资料图：", "配图：")
CTA_SIGNALS = ("关注", "私信", "扫码", "领取", "报名", "课程", "咨询", "加微信", "回复关键词", "资料包", "链接", "下载", "项目地址", "GitHub")
FORBIDDEN_TEMPLATE = (
    "先抓住文章的核心判断", "再看每个部分如何展开", "最后把方法带回自己的场景",
    "你可以这样检查", "本文将从以下几个方面展开", "模块 1", "模块 2", "可以带走的做法",
)
KEY_SENTENCE_SIGNALS = ("真正", "本质", "关键", "结论", "换句话说", "最重要", "核心", "意味着", "反直觉", "不是", "而是", "必须", "不要", "不能", "请记住")
PAIR_MAP = {"“": "”", "‘": "’", "《": "》", "（": "）", "(": ")", "【": "】", "[": "]", "「": "」", "『": "』"}
CLOSE_SET = set(PAIR_MAP.values())
SENTENCE_END = set("。！？!?；;")
SPECIAL_PREFIXES = ("IMAGE::", "TABLE::", "BULLET_ITEM::", "CAPTION::")

THEME_FILE = ROOT_DIR / "templates" / "theme-profiles.json"


def esc(value: Any) -> str:
    return html.escape(str(value or "").strip(), quote=False)


def plain_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "")


def clen(value: str) -> int:
    return len(re.sub(r"\s+", "", plain_html(value or "")))


def norm_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ").replace("\u2002", " ").replace("\u2003", " ")).strip()


def load_themes() -> dict[str, dict[str, Any]]:
    return json.loads(THEME_FILE.read_text(encoding="utf-8"))


def auto_theme(article_type: str) -> str:
    if article_type == "course_promo_clean":
        return "course"
    if article_type in {"skill_launch", "business_analysis"}:
        return "business"
    if article_type in {"opinion_editorial", "case_story", "book_note_editorial"}:
        return "minimal"
    return "editorial"


def apply_theme(name: str) -> dict[str, Any]:
    global ACCENT, TEXT, GREY, PALE, BLUE_BG, WARM, LINE, GRADIENT_START, GRADIENT_END
    themes = load_themes()
    theme = themes.get(name) or themes["editorial"]
    ACCENT = theme["accent"]
    TEXT = theme["text"]
    GREY = theme["grey"]
    PALE = theme["pale"]
    BLUE_BG = theme["blue_bg"]
    WARM = theme["warm"]
    LINE = theme["line"]
    GRADIENT_START, GRADIENT_END = theme["gradient"]
    return theme


def strip_markdown_links_keep_text(text: str) -> str:
    return re.sub(r"\[([^\]]+)\]\((?:[^()]|\([^()]*\))*\)", r"\1", text)


def strip_raw_html_tags(text: str) -> str:
    text = re.sub(r"<\s*/?\s*(html|head|body|div|iframe|svg|video|canvas|form|input|button|span|section|p|h1|h2|h3|ul|ol|li|a)\b[^>]*>", " ", text, flags=re.I)
    return re.sub(r"<(?!img\b)[^>]+>", " ", text)


def is_table_sep(line: str) -> bool:
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c or "") for c in cells)


def normalize_lonely_bullet_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    pending = False
    bullet_only = re.compile(r"^\s*(?:[•·●○▪▫◆◇]|[-*+])\s*$")
    bullet_with_text = re.compile(r"^\s*(?:[•·●○▪▫◆◇]|[-*+])\s+(.+?)\s*$")
    for raw in lines:
        line = raw.rstrip()
        if bullet_only.match(line):
            pending = True
            continue
        match = bullet_with_text.match(line)
        if match:
            text = match.group(1).strip()
            if text:
                out.append("BULLET_ITEM::" + text)
            pending = False
            continue
        if pending:
            clean = line.strip()
            if clean:
                out.append("BULLET_ITEM::" + clean)
            pending = False
        else:
            out.append(line)
    return out


def split_inline_markdown_table_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for raw in lines:
        line = raw.rstrip()
        if line.strip().startswith("|") or line.count("|") < 3:
            out.append(line)
            continue
        match = re.search(r"(.+?[。！？!?；;])\s*(\|\s*[^|]+\s*\|.+\|\s*)$", line)
        if match:
            prefix, table = match.group(1).strip(), match.group(2).strip()
            if prefix:
                out.append(prefix)
            out.append(table)
        else:
            out.append(line)
    return out


def parse_markdown_tables(lines: list[str]) -> tuple[list[str], list[list[list[str]]]]:
    out: list[str] = []
    tables: list[list[list[str]]] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.strip().startswith("|") and line.strip().endswith("|"):
            table: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                if not is_table_sep(lines[i]):
                    cells = [norm_space(c) for c in lines[i].strip().strip("|").split("|")]
                    table.append(cells)
                i += 1
            if table:
                out.append(f"TABLE::{len(tables)}")
                tables.append(table)
            continue
        out.append(line)
        i += 1
    return out, tables


def promote_numbered_plain_headings(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        if re.fullmatch(r"0?[1-9]|1[0-9]|20", lines[i].strip()) and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if nxt and not nxt.startswith(("HEADING::", "TABLE::", "IMAGE::", "BULLET_ITEM::", "CAPTION::")) and clen(nxt) <= 24 and not re.search(r"[。！？!?；;]$", nxt):
                out.append(f"HEADING::2::{lines[i].strip()} {nxt}")
                i += 2
                continue
        out.append(lines[i])
        i += 1
    return out


def normalize_input(raw_text: str) -> tuple[str, list[list[list[str]]]]:
    text = raw_text.replace("&nbsp;", " ").replace("&ensp;", " ").replace("&emsp;", " ")
    text = re.sub(r"<\s*(script|style)\b[^>]*>.*?<\s*/\s*\1\s*>", " ", text, flags=re.I | re.S)
    raw_lines = normalize_lonely_bullet_lines(split_inline_markdown_table_lines(text.splitlines()))
    parsed, tables = parse_markdown_tables(raw_lines)
    lines: list[str] = []
    for raw in parsed:
        line = raw.strip()
        if not line:
            continue
        if line.startswith(("TABLE::", "BULLET_ITEM::")):
            lines.append(line)
            continue
        image = re.match(r"^!\[([^\]]*)\]\(([^\)]*)\)", line)
        if image:
            lines.append(f"IMAGE::{image.group(1) or '图片'}::{image.group(2)}")
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            heading_text = norm_space(strip_raw_html_tags(strip_markdown_links_keep_text(heading.group(2))))
            if heading_text:
                lines.append(heading_text if level == 1 and not lines else f"HEADING::{level}::{heading_text}")
            continue
        line = strip_markdown_links_keep_text(line)
        line = strip_raw_html_tags(line)
        numbered = re.match(r"^\s*(\d+)[.)、]\s+(.+)$", line)
        if numbered:
            lines.append("BULLET_ITEM::" + numbered.group(2).strip())
            continue
        line = re.sub(r"^[-*+]\s+", "", line)
        line = line.replace("**", "").replace("__", "").replace("`", "").replace("|", "，")
        line = norm_space(line)
        if not line:
            continue
        if line.startswith(CAPTION_PREFIXES):
            lines.append("CAPTION::" + line)
        else:
            lines.append(line)
    lines = promote_numbered_plain_headings(lines)
    return "\n".join(lines), tables


def split_sentences(text: str) -> list[str]:
    """Split only outside paired Chinese punctuation.

    A closing quote is kept with the sentence. This prevents the old failure where
    an opening quote remained in one paragraph and the closing quote drifted into
    the next component.
    """
    out: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(SPECIAL_PREFIXES):
            out.append(line)
            continue
        stack: list[str] = []
        buf: list[str] = []
        for idx, char in enumerate(line):
            buf.append(char)
            if char in PAIR_MAP:
                stack.append(PAIR_MAP[char])
            elif char in CLOSE_SET and stack and char == stack[-1]:
                stack.pop()
                if not stack and idx > 0 and line[idx - 1] in SENTENCE_END:
                    sentence = "".join(buf).strip(" >")
                    if sentence:
                        out.append(sentence)
                    buf = []
            elif char in SENTENCE_END and not stack:
                sentence = "".join(buf).strip(" >")
                if sentence:
                    out.append(sentence)
                buf = []
        tail = "".join(buf).strip(" >")
        if tail:
            out.append(tail)
    return out


def balanced_pairs(text: str) -> bool:
    stack: list[str] = []
    for char in text:
        if char in PAIR_MAP:
            stack.append(PAIR_MAP[char])
        elif char in CLOSE_SET:
            if not stack or char != stack[-1]:
                return False
            stack.pop()
    return not stack


def is_caption_line(line: str) -> bool:
    return line.startswith("CAPTION::") or line.startswith(CAPTION_PREFIXES)


def classify_sentence_role(sentence: str) -> str:
    s = sentence.strip()
    if s.startswith("IMAGE::"):
        return "image"
    if s.startswith("TABLE::"):
        return "table"
    if s.startswith("BULLET_ITEM::"):
        return "bullet_item"
    if is_caption_line(s):
        return "image_caption"
    if re.match(r"^(参考资料|资料来源|来源|出处|免责声明|作者|版权|备注|时间|地点)[:：]", s):
        return "reference"
    if clen(s) < 100 and re.match(r"^(?:如果你想|如果想|想要|欢迎|请|扫码|关注(?:我|公众号)|私信|加微信|回复关键词|点击|立即报名|报名请|咨询请|下载|领取)", s) and any(signal in s for signal in CTA_SIGNALS):
        return "cta"
    if re.match(r"^(编辑注|编者按|补充说明|边界说明|说明)[:：]", s):
        return "editorial_note"
    if re.search(r"(^“.*”$|^‘.*’$|书中写道|有人说|原话|引用)", s):
        return "quote"
    if re.search(r"你以为.*(?:其实|真正|真实|但|而)", s):
        return "contrast"
    if re.search(r"(危险|警惕|禁止|不要|不能|错误|代价|小心|风险)", s):
        return "warning"
    if re.search(r"(可以|建议|先做|先从|行动|开始|试试|步骤|推荐)", s):
        return "action"
    if re.search(r"\d+(?:\.\d+)?\s*(?:%|％|倍|年|天|小时|分钟|元|万|亿|人|次)", s):
        return "data"
    if re.search(r"(真正|本质|关键|结论|换句话说|最重要|不是.*而是|核心|意味着|反直觉)", s):
        return "conclusion"
    if re.match(r"^(但是|但|然而|所以|因此|换句话说|这意味着)", s):
        return "transition"
    if s.endswith(("？", "?")):
        return "question"
    return "normal"


def semantic_marker_role(text: str) -> str:
    role = classify_sentence_role(text)
    if re.search(r"你以为|过去常说|旧做法|常见误区|误区是|表面答案", text):
        return "old_belief"
    if role == "warning":
        return "risk"
    if re.search(r"注意(?!力)|提醒|临界|尤其要留意", text):
        return "attention"
    # Whole-sentence judgment outranks a local action keyword such as “可以”.
    if role in {"conclusion", "transition", "contrast"} or re.search(r"(?:但|而|其实|真正|本质|关键|不是.*而是)", text):
        return "insight"
    if role == "action":
        return "action"
    if role == "data":
        return "data"
    return "neutral"


def is_strong_key_sentence(text: str) -> bool:
    return 16 <= clen(text) <= 140 and (any(signal in text for signal in KEY_SENTENCE_SIGNALS) or bool(re.search(r"你以为.*其实|不是.*而是|从.*开始", text)))


def merge_short_sentences(sentences: list[str]) -> list[str]:
    groups: list[str] = []
    buf: list[str] = []
    length = 0

    def flush() -> None:
        nonlocal buf, length
        if buf:
            groups.append("".join(buf))
            buf = []
            length = 0

    isolated = {"quote", "image", "image_caption", "reference", "cta", "table", "bullet_item", "editorial_note", "contrast"}
    for sentence in sentences:
        role = classify_sentence_role(sentence)
        current_length = clen(sentence)
        if source_triggered_component(sentence):
            flush()
            groups.append(sentence)
            continue
        if role in isolated:
            flush()
            groups.append(sentence)
            continue
        if role in {"conclusion", "transition", "warning", "data", "action"} and 14 <= current_length <= 120:
            flush()
            groups.append(sentence)
            continue
        buf.append(sentence)
        length += current_length
        if length >= 115 or len(buf) >= 3:
            flush()
    flush()
    merged: list[str] = []
    for group in groups:
        if merged and not source_triggered_component(group) and not source_triggered_component(merged[-1]) and classify_sentence_role(group) == "normal" and classify_sentence_role(merged[-1]) == "normal" and clen(group) < 70 and clen(merged[-1]) < 145:
            merged[-1] += group
        else:
            merged.append(group)
    return merged


def detect_article_type(title: str, text: str) -> str:
    all_text = title + "\n" + text
    if re.search(r"(Skill|工具发布|项目地址|GitHub|下载方式|怎么使用)", all_text, re.I):
        return "skill_launch"
    if re.search(r"(步骤|教程|操作|指南|如何|怎么|使用方法)", all_text):
        return "tutorial_guide"
    if re.search(r"(读书|书中|《[^》]+》|笔记|摘录)", all_text):
        return "book_note_editorial"
    if re.search(r"(课程|训练营|报名|咨询|领取课程|招生|活动报名)", all_text):
        return "course_promo_clean"
    if re.search(r"(营收|利润|增长|商业模式|市场|客户|销售|公司|企业)", all_text):
        return "business_analysis"
    if re.search(r"(案例|故事|复盘|经历|转变|那天|后来)", all_text):
        return "case_story"
    if re.search(r"(观点|判断|趋势|我认为|真正的问题|评论|不是.*而是)", all_text):
        return "opinion_editorial"
    return "knowledge_explainer"


def title_words(value: str) -> set[str]:
    return set(re.findall(r"[\u4e00-\u9fa5A-Za-z0-9]{2,}", value or ""))


def make_digest(title: str, core: str) -> str:
    candidate = core.strip("。")
    if not candidate or candidate == title or len(title_words(candidate) & title_words(title)) > max(2, len(title_words(title)) * 0.7):
        return "把重点、节奏和阅读层级处理清楚，让文章在手机上更容易读完。"
    if clen(candidate) > 70:
        candidate = candidate[:70] + "。"
    return candidate if candidate.endswith(("。", "！", "？")) else candidate + "。"


def compact_heading(text: str, idx: int, article_type: str) -> str:
    clean = re.sub(r"(?:IMAGE|TABLE|BULLET_ITEM|CAPTION)::[^\n]+", "", text)
    clean = re.sub(r"^[“‘]|[”’]$", "", clean).strip()
    role = semantic_marker_role(clean)
    patterns = [
        r"(?:真正的问题|关键|本质|核心|结论)[是：，]?([^。！？；]{4,18})",
        r"不是([^。！？；]{3,12})，?而是([^。！？；]{3,16})",
        r"(?:建议|可以|先从|先做)([^。！？；]{4,18})",
        r"(?:风险|误区|错误)[是：，]?([^。！？；]{4,18})",
    ]
    for pattern in patterns:
        match = re.search(pattern, clean)
        if match:
            phrase = match.group(match.lastindex or 1).strip("，：:。")
            if 4 <= clen(phrase) <= 20:
                return phrase
    first_clause = re.split(r"[，。！？；：]", clean)[0].strip()
    if 5 <= clen(first_clause) <= 20:
        return first_clause
    role_fallback = {
        "old_belief": "先修正一个常见误区",
        "risk": "这里有一个风险边界",
        "action": "把方法落到具体动作",
        "data": "先看数据说明了什么",
        "insight": "真正值得记住的判断",
    }
    if role in role_fallback:
        return role_fallback[role]
    by_type = {
        "tutorial_guide": ["先确认使用场景", "把步骤拆到能执行", "最后检查结果"],
        "opinion_editorial": ["判断从哪里开始", "理由为什么成立", "边界同样重要"],
        "knowledge_explainer": ["先理解这个概念", "它为什么会发生", "放回真实场景"],
        "case_story": ["事情从这里开始", "变化发生在这里", "复盘留下什么"],
        "course_promo_clean": ["先看是否适合你", "课程解决什么", "信息轻一点说清"],
        "skill_launch": ["它解决什么问题", "核心能力如何工作", "谁更适合使用"],
        "book_note_editorial": ["书里先提醒什么", "一个值得记住的判断", "把观点放回现实"],
        "business_analysis": ["先看真正的经营问题", "数据背后的原因", "下一步怎么做"],
    }
    return by_type.get(article_type, by_type["knowledge_explainer"])[idx % 3]


def choose_heading_style(article_type: str, idx: int) -> str:
    mapping = {
        "knowledge_explainer": ["question", "leftline", "shortline"],
        "opinion_editorial": ["leftline", "shortline"],
        "tutorial_guide": ["number", "capsule"],
        "book_note_editorial": ["shortline", "leftline"],
        "course_promo_clean": ["capsule", "leftline"],
        "case_story": ["shortline", "question"],
        "skill_launch": ["capsule", "number"],
        "business_analysis": ["number", "leftline"],
    }
    choices = mapping.get(article_type, ["question", "leftline"])
    return choices[idx % len(choices)]


def choose_section_key_sentence(points: Iterable[str]) -> str:
    clean = [p for p in points if p and classify_sentence_role(p) not in {"image", "image_caption", "reference", "cta", "table", "bullet_item"}]
    for point in clean:
        if is_strong_key_sentence(point):
            return point
    for point in clean:
        if 24 <= clen(point) <= 120:
            return point
    return clean[0] if clean else ""


def section_label(text: str) -> tuple[str, str, str]:
    role = semantic_marker_role(text)
    mapping = {
        "old_belief": ("常见误区", "×", "risk"),
        "risk": ("风险提醒", "!", "risk"),
        "action": ("行动建议", "✓", "action"),
        "attention": ("注意事项", "!", "attention"),
        "data": ("数据说明", "#", "data"),
        "insight": ("核心判断", "▍", "insight"),
    }
    return mapping.get(role, ("", "", "neutral"))


def infer_content_visual_profile(title: str, article_type: str, text: str) -> dict[str, str]:
    all_text = title + "\n" + text
    if re.search(r"宇宙|星系|黑洞|量子|物理|天文|行星|恒星|太空|暗物质", all_text):
        return {"content_domain": "hard_science_space", "visual_style": "深色电影感宇宙科普风", "mood": "悬疑、宏大、克制、可信", "cover_scene": "深色宇宙尺度场景、主体居中、强空间纵深、电影光影", "inline_scene": "尺度对比、天体结构、空间场景或科学过程可视化"}
    if re.search(r"健康|运动|睡眠|饮食|身体|焦虑|心脏|生活方式|养生", all_text):
        return {"content_domain": "health_lifestyle", "visual_style": "温暖真实生活感", "mood": "轻松、可信、生活化、柔和", "cover_scene": "自然光生活场景、普通人正在做低门槛行动、画面温暖不焦虑", "inline_scene": "日常动作、家庭场景、身体状态隐喻、低门槛行动"}
    if re.search(r"AI|人工智能|大模型|芯片|算力|科技|商业|数据|利润|公司|产业|模型|服务器|工具|Skill", all_text, re.I):
        return {"content_domain": "ai_tech_business", "visual_style": "现代科技知识杂志风", "mood": "理性、专业、清爽、未来感", "cover_scene": "抽象科技系统、芯片、数据流、城市或屏幕界面，信息层次清楚", "inline_scene": "概念图、流程图、工作流、界面感插画或系统结构图"}
    if re.search(r"成长|独居|情绪|人生|普通人|自律|拖延|决策|生活|工作|关系|方法论", all_text):
        return {"content_domain": "personal_growth", "visual_style": "温暖克制个人成长风", "mood": "安静、共鸣、留白、真实", "cover_scene": "人物背影、桌面、城市窗边或生活隐喻，情绪克制", "inline_scene": "生活场景、情绪隐喻、桌面、房间或路上的普通人画面"}
    return {"content_domain": "knowledge_editorial", "visual_style": "清爽知识杂志风", "mood": "克制、清晰、专业、可读", "cover_scene": "简洁知识杂志封面、清晰主视觉、少量图形隐喻", "inline_scene": "概念解释图、轻插画或信息结构图"}


def build_smart_image_plan(plan: dict[str, Any]) -> dict[str, Any]:
    full_text = "\n".join(group for section in plan.get("sections", []) for group in section.get("paragraph_groups", []) if not group.startswith(SPECIAL_PREFIXES))
    profile = infer_content_visual_profile(plan.get("title", ""), plan.get("article_type", ""), full_text)
    title = re.sub(r"\s+", " ", plan.get("title", "")).strip()[:28]
    cover_prompt = (
        f"公众号横版封面，比例 2.35:1，同时兼容中心 1:1 裁切；主题：{title}；"
        f"视觉风格：{profile['visual_style']}；情绪：{profile['mood']}；画面：{profile['cover_scene']}；"
        "主体和标题安全区靠近画面中心，左右两侧只做氛围延展；只放一个主标题，不放副标题、标签、正文说明；"
        "中文字体清晰，无错字，无水印，无平台标识。"
    )
    cover = {"usage": "cover", "ratio": "2.35:1", "square_crop_safe": "center 1:1 safe", "prompt": cover_prompt, "placement": "公众号封面", "requires_upload_to_wechat": True, "visual_style": profile["visual_style"], "content_domain": profile["content_domain"], "generation_mode": "optional_prompt_first"}
    length = clen(full_text)
    count = 1 if length < 700 else (2 if length < 1500 else 3)
    inline: list[dict[str, Any]] = []
    sections = plan.get("sections", [])
    indexes = [i for i in (1, 2, 3) if i < len(sections)] or ([0] if sections else [])
    for idx in indexes[:count]:
        section = sections[idx]
        key = section.get("key_sentence") or next((x for x in section.get("paragraph_groups", []) if not x.startswith(SPECIAL_PREFIXES)), "")
        prompt = (
            f"公众号正文配图，比例 3:4；对应小节：{section.get('heading', '正文重点')}；核心画面：{key[:80]}；"
            f"视觉风格：{profile['visual_style']}；情绪：{profile['mood']}；画面方向：{profile['inline_scene']}；"
            "不放大段文字、二维码、水印或平台标识，画面清爽，作为文章中段视觉停顿。"
        )
        inline.append({"usage": "inline", "ratio": "3:4", "prompt": prompt, "placement": f"第 {idx + 1} 节之后", "requires_upload_to_wechat": True, "visual_style": profile["visual_style"], "content_domain": profile["content_domain"], "generation_mode": "optional_prompt_first"})
    policy = "仅可对自有图片或本流程生成图片进行背景补全、局部重构和模型伪水印清理；第三方版权水印、署名、Logo和平台标识不得自动移除，应改用授权无水印素材或重新生成。"
    return {"enabled": True, "mode": "prompt_plan_first", "watermark_reconstruction_policy": policy, "cover_image": cover, "inline_images": inline, "all_assets": [cover] + inline}


def build_article_plan(normalized: str, tables: list[list[list[str]]]) -> dict[str, Any]:
    lines = normalized.splitlines()
    title = lines[0] if lines else "公众号文章"
    body_lines = lines[1:] if len(lines) > 1 else []
    preamble: list[str] = []
    outlined: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    references: list[str] = []
    ctas: list[str] = []
    images: list[dict[str, str]] = []
    source_segments: list[str] = []

    for line in body_lines:
        if line.startswith("HEADING::"):
            parts = line.split("::", 2)
            current = {"heading": parts[2].strip(), "lines": []}
            outlined.append(current)
            continue
        role = classify_sentence_role(line)
        if role == "reference":
            references.append(line)
            source_segments.append(line)
            continue
        if role == "cta":
            ctas.append(line)
            source_segments.append(line)
            continue
        if role == "image":
            parts = line.split("::", 2)
            images.append({"alt": parts[1] if len(parts) > 1 else "图片", "src": parts[2] if len(parts) > 2 else ""})
        elif role not in {"table"}:
            clean_source = line.split("::", 1)[1] if line.startswith(("BULLET_ITEM::", "CAPTION::")) else line
            source_segments.append(clean_source)
        (current["lines"] if current else preamble).append(line)

    source_body = "\n".join(source_segments)
    article_type = detect_article_type(title, source_body)
    sections: list[dict[str, Any]] = []
    pre_groups = merge_short_sentences(split_sentences("\n".join(preamble)))

    if outlined:
        for idx, item in enumerate(outlined[:12]):
            groups = merge_short_sentences(split_sentences("\n".join(item["lines"])))
            if not groups:
                continue
            text_points = [g for g in groups if classify_sentence_role(g) not in {"image", "image_caption", "table", "bullet_item"}]
            label, icon, tone = section_label("".join(text_points[:2]))
            sections.append({
                "heading": item["heading"],
                "goal": "忠实保留原文结构并降低阅读阻力",
                "raw_points": text_points,
                "paragraph_groups": groups,
                "key_sentence": choose_section_key_sentence(text_points),
                "key_sentence_candidates": [x for x in text_points if classify_sentence_role(x) in {"conclusion", "transition", "warning", "contrast", "data", "action"}],
                "heading_style": choose_heading_style(article_type, idx),
                "road_sign_label": label,
                "road_sign_icon": icon,
                "semantic_tone": tone,
            })
    else:
        groups = pre_groups or [title]
        target = max(2, min(5, (len(groups) + 1) // 2 or 2))
        size = max(1, (len(groups) + target - 1) // target)
        chunks = [groups[i:i + size] for i in range(0, len(groups), size)]
        for idx, chunk in enumerate(chunks[:6]):
            if not chunk:
                continue
            text_points = [g for g in chunk if classify_sentence_role(g) not in {"image", "image_caption", "table", "bullet_item"}]
            heading = compact_heading("".join(text_points), idx, article_type)
            label, icon, tone = section_label("".join(text_points[:2]))
            sections.append({
                "heading": heading,
                "goal": "降低阅读阻力，形成连续阅读节奏",
                "raw_points": text_points,
                "paragraph_groups": chunk,
                "key_sentence": choose_section_key_sentence(text_points),
                "key_sentence_candidates": [x for x in text_points if classify_sentence_role(x) in {"conclusion", "transition", "warning", "contrast", "data", "action"}],
                "heading_style": choose_heading_style(article_type, idx),
                "road_sign_label": label,
                "road_sign_icon": icon,
                "semantic_tone": tone,
            })

    all_text_groups = [group for section in sections for group in section["paragraph_groups"] if classify_sentence_role(group) not in {"image", "image_caption", "table", "bullet_item"}]
    intro = pre_groups[0] if pre_groups else ""
    core = next((g for g in all_text_groups if is_strong_key_sentence(g)), all_text_groups[0] if all_text_groups else title)
    summary = ""
    if sections:
        last_groups = sections[-1].get("paragraph_groups", [])
        if last_groups:
            last_group = last_groups[-1]
            if classify_sentence_role(last_group) not in {"image", "image_caption", "table", "bullet_item"} and last_group.strip() != intro.strip():
                summary = last_group
    actions = [segment.split("::", 1)[1] for section in sections for segment in section["paragraph_groups"] if segment.startswith("BULLET_ITEM::")]
    plan: dict[str, Any] = {
        "title": title,
        "digest": make_digest(title, core),
        "audience": "公众号手机端读者",
        "core_message": core,
        "intro_message": intro,
        "summary_message": summary,
        "article_type": article_type,
        "visual_style": "semantic_editorial_magazine",
        "sections": sections,
        "quotes": [g for g in all_text_groups if classify_sentence_role(g) == "quote"][:4],
        "actions": actions,
        "references": references,
        "image_assets": [],
        "images": images,
        "ctas": ctas,
        "tables": tables,
        "source_outline": [x["heading"] for x in outlined],
        "source_text": source_body,
        "source_segments": source_segments,
        "has_source_preamble": bool(pre_groups),
        "lead_groups": pre_groups if outlined else [],
    }
    smart_image_plan = build_smart_image_plan(plan)
    existing_assets = [{"usage": "inline_existing", "ratio": "source", "prompt": image["alt"], "placement": "原文图片位置", "requires_upload_to_wechat": True, "generation_mode": "source_image"} for image in images]
    plan["smart_image_plan"] = smart_image_plan
    plan["cover_image_brief"] = smart_image_plan["cover_image"]
    plan["image_assets"] = smart_image_plan["all_assets"] + existing_assets
    return plan


def choose_semantic_roles(plan: dict[str, Any]) -> list[str]:
    counts = {role: 0 for role in ("risk", "attention", "action", "data", "insight")}
    for section in plan.get("sections", []):
        for group in section.get("paragraph_groups", []):
            role = semantic_marker_role(group)
            if role in counts:
                counts[role] += 1
    active: list[str] = ["data"] if counts["data"] else []
    # Risk has priority over decorative insight. Action comes next.
    for role in ("risk", "action", "attention", "insight"):
        if counts[role] and len([x for x in active if x != "data"]) < 2:
            active.append(role)
    return active


def marker_budget(plan: dict[str, Any]) -> dict[str, int]:
    length = clen(plan.get("source_text", ""))
    return {
        "gradient_emphasis_bar": 0,
        "semantic_color_block": 1 if length < 1200 else 2,
        "outlined_text_box": 1 if length < 1200 else 2,
        "left_quote": 1 if length < 1000 else 2,
        "double_compare": 0,
        "editorial_note": 0,
        "numbered_points": 0,
        "divider": max(0, min(3, len(plan.get("sections", [])) - 1)),
        "capsule_label": 0,
        "source_triggered": 2 if length < 1200 else 4,
    }

def build_text_rhythm_plan(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": "paragraph_group",
        "visual_style": plan["visual_style"],
        "article_type": plan["article_type"],
        "paragraphs": [{"text": group, "role": classify_sentence_role(group), "semantic_role": semantic_marker_role(group), "length": clen(group)} for section in plan["sections"] for group in section["paragraph_groups"]],
    }


def build_visual_plan(plan: dict[str, Any], theme_name: str) -> dict[str, Any]:
    active = choose_semantic_roles(plan)
    return {
        "visual_style": plan["visual_style"],
        "article_type": plan["article_type"],
        "theme": theme_name,
        "accent_color": ACCENT,
        "heading_styles": [section["heading_style"] for section in plan["sections"]],
        "semantic_marker_system": {
            "mode": "automatic_sparse",
            "active_roles": active,
            "max_inline_marker_types_per_paragraph": 1,
            "max_semantic_accent_colors_per_article": 3,
            "budget": marker_budget(plan),
            "palette": {"knowledge": ACCENT, "action": GREEN, "attention": ORANGE, "risk": RED, "insight": PURPLE, "old_belief": GREY},
            "grammar": {
                "underline": "light emphasis or key judgment",
                "strikethrough": "corrected old belief only",
                "color_block": "section-level conclusion",
                "inline_highlight": "keyword inside paragraph",
                "left_quote": "screenshot-worthy quote",
                "capsule_label": "reading road sign",
                "icon_marker": "recognition for steps, questions and warnings",
                "double_compare": "old belief versus reality",
                "gradient_emphasis_bar": "single strongest judgment",
                "editorial_note": "boundary or clarification",
                "data_emphasis": "numbers with semantic weight",
                "divider": "reading rhythm",
                "numbered_points": "ordered multi-point argument",
            },
        },
        "smart_image_plan": plan.get("smart_image_plan", {}),
        "cta_enabled": bool(plan.get("ctas")),
        "cta_text": plan.get("ctas", [""])[0] if plan.get("ctas") else "",
    }


def comp(component_type: str, role: str, content: Any, style: str = "token", children: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"type": component_type, "role": role, "content": content, "style_token": style, "children": children or []}


def extract_compare(text: str) -> dict[str, str] | None:
    patterns = [
        r"你以为(?:问题)?是[:：]?\s*(.+?)[。；;]\s*(?:真正的问题是|真实情况是|其实|但|而)[:：]?\s*(.+)$",
        r"你以为[:：]?\s*(.+?)[，,]\s*(?:真正|其实|现实|但|而)[:：]?\s*(.+)$",
        r"表面上(?:看)?[:：]?\s*(.+?)[。；;]\s*(?:实际上|真正|其实)[:：]?\s*(.+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            left = match.group(1).strip("，。；;：: ")
            right = match.group(2).strip("，。；;：: ")
            if left and right and clen(left) <= 70 and clen(right) <= 90:
                return {"left_label": "你以为", "left": left, "right_label": "真实情况", "right": right, "source": text}
    return None


def divider_variant(next_tone: str, index: int) -> str:
    if next_tone == "risk":
        return "dotted"
    if next_tone in {"insight", "data"}:
        return "gradient"
    if next_tone in {"action", "attention"}:
        return "labeled"
    return "short"


def should_gradient(text: str, used: dict[str, int], budget: dict[str, int]) -> bool:
    return used["gradient_emphasis_bar"] < budget["gradient_emphasis_bar"] and 18 <= clen(text) <= 110 and bool(re.search(r"不是.*而是|真正|本质|最重要|核心|关键|结论", text))


def should_color_block(text: str, used: dict[str, int], budget: dict[str, int]) -> bool:
    return used["semantic_color_block"] < budget["semantic_color_block"] and is_strong_key_sentence(text) and semantic_marker_role(text) in {"risk", "action", "attention", "insight", "data"}


def resolved_tone(role: str, active_roles: set[str]) -> str:
    if role in {"neutral", "old_belief"}:
        return role
    if role == "data":
        return "data"
    return role if role in active_roles else "data"


def should_outlined_text_box(text: str, used: dict[str, int], budget: dict[str, int]) -> bool:
    return (
        used.get("outlined_text_box", 0) < budget.get("outlined_text_box", 0)
        and 18 <= clen(text) <= 120
        and is_strong_key_sentence(text)
    )


def build_component_tree(plan: dict[str, Any], rhythm: dict[str, Any], visual: dict[str, Any], profile: str = "strict_draftbox") -> dict[str, Any]:
    children: list[dict[str, Any]] = []
    if profile != "strict_draftbox":
        children.append(comp("title_block", "title", {"title": plan["title"]}))
    budget = visual["semantic_marker_system"]["budget"]
    used = {key: 0 for key in budget}
    active_roles = set(visual["semantic_marker_system"].get("active_roles", []))

    for lead in plan.get("lead_groups", []):
        role = semantic_marker_role(lead)
        if role not in active_roles and role not in {"old_belief", "data"}:
            role = "neutral"
        children.append(comp("body_paragraph", "lead", {"text": lead, "marker_role": role}))

    for section_index, section in enumerate(plan["sections"]):
        if section_index > 0 and used["divider"] < budget["divider"]:
            children.append(comp("divider", "rhythm", {"variant": "short", "tone": "neutral", "label": ""}))
            used["divider"] += 1
        children.append(comp("section_title", "section_heading", {
            "index": section_index + 1,
            "text": section["heading"],
            "style": "large_number",
            "tone": "neutral"
        }))
        groups = section["paragraph_groups"]
        idx = 0
        while idx < len(groups):
            group = groups[idx]
            role = classify_sentence_role(group)
            if role == "image":
                parts = group.split("::", 2)
                children.append(comp("image_block", "image", {"alt": parts[1] if len(parts) > 1 else "", "src": parts[2] if len(parts) > 2 else ""}))
                idx += 1; continue
            if role == "image_caption":
                children.append(comp("image_caption", "caption", group.split("::", 1)[1] if "::" in group else group))
                idx += 1; continue
            if role == "table":
                table_idx = int(group.split("::")[1])
                table = plan.get("tables", [])[table_idx] if table_idx < len(plan.get("tables", [])) else []
                children.append(comp("simple_compare_table", "table", table))
                idx += 1; continue
            if role == "bullet_item":
                items: list[str] = []
                while idx < len(groups) and groups[idx].startswith("BULLET_ITEM::"):
                    items.append(groups[idx].split("::", 1)[1].strip())
                    idx += 1
                children.append(comp("checklist", "source_list", {"items": items}, "plain_list"))
                continue
            if role == "quote" and used["left_quote"] < budget["left_quote"]:
                children.append(comp("left_quote", "source_quote", {"text": group, "tone": "neutral"}))
                used["left_quote"] += 1
                idx += 1; continue
            marker_role = semantic_marker_role(group)
            source_exact = group in plan.get("source_text", "")
            triggered_type = source_triggered_component(group) if source_exact else ""
            if triggered_type and used.get("source_triggered", 0) < budget.get("source_triggered", 0):
                children.append(comp(triggered_type, "source_triggered_marker", {"text": group, "tone": resolved_tone(marker_role if marker_role != "neutral" else "data", active_roles)}))
                used["source_triggered"] = used.get("source_triggered", 0) + 1
                idx += 1
                continue
            if marker_role not in active_roles and marker_role not in {"old_belief", "data"}:
                marker_role = "neutral"
            if source_exact and should_color_block(group, used, budget) and marker_role != "neutral":
                children.append(comp("semantic_color_block", "source_key_sentence", {
                    "text": group,
                    "tone": resolved_tone(marker_role, active_roles),
                    "label": "",
                    "icon": "",
                }))
                used["semantic_color_block"] += 1
            elif source_exact and should_outlined_text_box(group, used, budget):
                children.append(comp("outlined_text_box", "source_text_box", {
                    "text": group,
                    "tone": resolved_tone(marker_role if marker_role != "neutral" else "data", active_roles),
                    "label": "",
                    "icon": "",
                }))
                used["outlined_text_box"] += 1
            else:
                children.append(comp("body_paragraph", "body", {"text": group, "marker_role": marker_role}))
            idx += 1

    if plan.get("references"):
        children.append(comp("references_block", "references", plan["references"]))
    if plan.get("ctas"):
        children.append(comp("soft_cta", "source_cta", plan["ctas"]))
    return {"profile": profile, "components": [comp("article_container", "container", {}, children=children)]}

def tone_colors(tone: str) -> tuple[str, str]:
    mapping = {
        "risk": (RED_BG, RED),
        "action": (GREEN_BG, GREEN),
        "attention": (ORANGE_BG, ORANGE),
        "insight": (PURPLE_BG, PURPLE),
        "data": (BLUE_BG, ACCENT),
        "old_belief": (GREY_BG, GREY),
    }
    return mapping.get(tone, (BLUE_BG, ACCENT))


def marker_style(role: str, marker: str) -> str:
    background, color = tone_colors(role)
    if marker == "underline":
        return f"font-weight:700;color:{color};border-bottom:2px solid {background};padding-bottom:1px"
    if marker == "highlight":
        return f"font-weight:700;color:{color};background:{background};padding:1px 3px;border-radius:3px"
    if marker == "strike":
        return f"color:{GREY};text-decoration:line-through;text-decoration-color:#A0A6AF;text-decoration-thickness:2px"
    if marker == "data":
        return f"font-weight:700;color:{color};background:{background};padding:1px 4px;border-radius:4px"
    return f"font-weight:700;color:{color}"


def replace_first_escaped(raw: str, phrase: str, style: str) -> str:
    escaped = esc(phrase)
    return raw.replace(escaped, f'<span style="{style}">{escaped}</span>', 1)


def emphasize_inline(text: str, forced_role: str | None = None) -> str:
    raw = esc(text)
    if clen(text) > 180:
        return raw
    role = forced_role or semantic_marker_role(text)
    if role == "old_belief":
        match = re.search(r"(你以为(?:问题)?是?[:：]?[^，。；;！!？?]{2,34}|过去常说[^，。；;！!？?]{2,30}|旧做法[^，。；;！!？?]{2,30}|常见误区[^，。；;！!？?]{2,30}|表面答案[^，。；;！!？?]{2,30})", text)
        if match:
            return replace_first_escaped(raw, match.group(1), marker_style(role, "strike"))
    if role == "risk":
        match = re.search(r"((?:不要|不能|警惕|小心|风险|错误|代价|禁止)[^，。；;！!？?]{1,30})", text)
        if match:
            return replace_first_escaped(raw, match.group(1), marker_style(role, "underline"))
    if role == "attention":
        match = re.search(r"((?:注意(?!力)|提醒|临界|尤其要留意)[^，。；;！!？?]{1,30})", text)
        if match:
            return replace_first_escaped(raw, match.group(1), marker_style(role, "highlight"))
    if role == "action":
        match = re.search(r"((?:可以|建议|先做|先从|试试|开始|推荐)[^，。；;！!？?]{2,34})", text)
        if match:
            return replace_first_escaped(raw, match.group(1), marker_style(role, "highlight"))
    if role == "data":
        matches = list(re.finditer(r"\d+(?:\.\d+)?\s*(?:%|％|倍|年|天|小时|分钟|元|万|亿|人|次)", text))[:2]
        if matches:
            # Apply from right to left on escaped text to keep offsets irrelevant.
            for match in reversed(matches):
                raw = replace_first_escaped(raw, match.group(0), marker_style(role, "data"))
            return raw
    if role == "insight":
        patterns = [r"不是[^，。；;！!？?]{2,30}而是[^，。；;！!？?]{2,36}", r"真正[^，。；;！!？?]{2,36}", r"本质[^，。；;！!？?]{2,36}", r"关键[^，。；;！!？?]{2,36}"]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match and 4 <= clen(match.group(0)) <= 52:
                return replace_first_escaped(raw, match.group(0), marker_style(role, "underline"))
    return raw


GENERATED_UI_LABELS = ("核心判断", "行动建议", "注意事项", "风险提醒", "数据说明", "常见误区", "最后总结", "先说结论", "阅读重点", "这一篇，你会看到", "问题清单", "编辑注｜", "重点")

BODY = ""


def body_style() -> str:
    return f"margin:0 0 16px 0;font-size:16px;line-height:1.78;color:{TEXT};font-family:{FF}"


def render_heading(content: dict[str, Any]) -> str:
    index = int(content.get("index", 0) or 0)
    text = esc(content["text"])
    number = f"{index:02d}" if index else ""
    number_html = f'<p style="font-size:34px;line-height:1;color:{ACCENT};font-weight:700;margin:0 0 8px 0;font-family:{FF};letter-spacing:-1px;opacity:0.82;">{number}</p>' if number else ""
    return f'<section style="margin:34px 0 17px 0;">{number_html}<p style="font-size:21px;line-height:1.45;color:{TEXT};font-weight:700;margin:0;font-family:{FF};">{text}</p><p style="width:34px;height:3px;background:{ACCENT};border-radius:2px;margin:11px 0 0 0;"></p></section>'


def render_table(table: list[list[str]]) -> str:
    if not table:
        return ""
    body = "".join("<tr style="">" + "".join(f'<td style="font-size:14px;line-height:1.6;color:{TEXT};border:1px solid {LINE};padding:8px;vertical-align:top;">{esc(cell)}</td>' for cell in row[:3]) + "</tr>" for row in table[:9])
    return f'<table style="border-collapse:collapse;width:100%;margin:20px 0;"><tbody style="vertical-align:top;">{body}</tbody></table>'

def render_divider(content: dict[str, Any]) -> str:
    variant = content.get("variant", "short")
    tone = content.get("tone", "neutral")
    label = esc(content.get("label", ""))
    background, color = tone_colors(tone)
    if variant == "gradient":
        return f'<section style="height:2px;background:linear-gradient(90deg,{PALE} 0%,{color} 50%,{PALE} 100%);margin:28px 0;"></section>'
    if variant == "dotted":
        return f'<section style="border-top:1px dotted {color};margin:28px 0;"></section>'
    if variant == "labeled" and label:
        return f'<section style="text-align:center;margin:28px 0;border-top:1px solid {LINE};"><span style="display:inline-block;background:#FFFFFF;color:{color};font-size:12px;line-height:1.4;padding:3px 10px;margin-top:-10px;border-radius:999px;font-family:{FF};">{label}</span></section>'
    return f'<section style="width:38px;height:2px;background:{color};border-radius:2px;margin:28px auto;"></section>'


def render_component(component: dict[str, Any]) -> str:
    component_type = component["type"]
    content = component["content"]
    if component_type == "article_container":
        return f'<section style="margin:0 10px;font-family:{FF};">' + "".join(render_component(child) for child in component["children"]) + "</section>"
    if component_type == "title_block":
        return f'<section style="margin:0 0 28px 0;"><p style="margin:0;font-size:22px;line-height:1.35;color:#111827;font-weight:700;font-family:{FF};">{esc(content["title"])}</p></section>'
    if component_type == "intro_conclusion_card":
        return f'<p style="{body_style()}">{esc(content)}</p>'
    if component_type == "article_nav":
        rows = "".join(f'<p style="font-size:15px;line-height:1.7;color:{TEXT};margin:0 0 8px 0;font-family:{FF};"><span style="font-weight:700;color:{ACCENT};">{idx + 1:02d}</span> {esc(item)}</p>' for idx, item in enumerate(content[:6]))
        return f'<section style="background:#FFFFFF;border:1px solid {LINE};border-radius:10px;padding:14px 16px;margin:20px 0;"><p style="font-size:13px;line-height:1.4;color:{GREY};margin:0 0 10px 0;font-family:{FF};">这一篇，你会看到</p>{rows}</section>'
    if component_type == "section_title":
        return render_heading(content)
    if component_type == "body_paragraph":
        return f'<p style="{body_style()}">{emphasize_inline(content.get("text", ""), content.get("marker_role"))}</p>'
    if component_type in {"semantic_color_block", "emphasis_sentence"}:
        tone = content.get("tone", "data")
        background, color = tone_colors(tone)
        return f'<section style="background:{background};border-left:4px solid {color};border-radius:8px;padding:14px 16px;margin:18px 0;"><p style="font-size:16px;line-height:1.75;color:{TEXT};font-weight:700;margin:0;font-family:{FF};">{esc(content.get("text", ""))}</p></section>'
    if component_type == "gradient_emphasis_bar":
        return f'<section style="background:linear-gradient(135deg,{GRADIENT_START} 0%,{GRADIENT_END} 100%);border-radius:10px;padding:16px 18px;margin:20px 0;"><p style="font-size:17px;line-height:1.72;color:#FFFFFF;font-weight:700;margin:0;font-family:{FF};">{esc(content.get("text", ""))}</p></section>'
    if component_type == "outlined_text_box":
        _, color = tone_colors(content.get("tone", "data"))
        return f'<section style="background:#FFFFFF;border:1px solid {color};border-top:4px solid {color};border-radius:5px;padding:15px 17px;margin:20px 0;"><p style="font-size:16px;line-height:1.75;color:{TEXT};font-weight:500;margin:0;font-family:{FF};">{esc(content.get("text", ""))}</p></section>'
    if component_type in {"left_quote", "core_quote_card"}:
        _, color = tone_colors(content.get("tone", "insight"))
        return f'<blockquote style="border-left:4px solid {color};background:{PALE};border-radius:0 8px 8px 0;padding:14px 16px;margin:20px 0;"><p style="font-size:16px;line-height:1.75;color:{TEXT};margin:0;font-family:{FF};">{esc(content.get("text", ""))}</p></blockquote>'
    if component_type == "editorial_note":
        background, color = tone_colors(content.get("tone", "attention"))
        return f'<section style="background:{background};border:1px dashed {color};border-radius:8px;padding:12px 14px;margin:18px 0;"><p style="font-size:13px;line-height:1.7;color:{TEXT};margin:0;font-family:{FF};">{esc(content.get("text", ""))}</p></section>'
    if component_type == "double_compare":
        left_bg, left_color = tone_colors(content.get("left_tone", "old_belief"))
        right_bg, right_color = tone_colors(content.get("right_tone", "data"))
        table_html = f'<table style="border-collapse:collapse;width:100%;margin:10px 0 0 0;"><tbody style="vertical-align:top;"><tr style="vertical-align:top;"><td style="width:50%;vertical-align:top;background:{left_bg};border:1px solid {LINE};padding:13px;"><p style="font-size:12px;line-height:1.4;color:{left_color};font-weight:700;margin:0 0 7px 0;font-family:{FF};">× {esc(content.get("left_label", "你以为"))}</p><p style="font-size:15px;line-height:1.65;color:{TEXT};margin:0;font-family:{FF};">{esc(content.get("left", ""))}</p></td><td style="width:50%;vertical-align:top;background:{right_bg};border:1px solid {LINE};padding:13px;"><p style="font-size:12px;line-height:1.4;color:{right_color};font-weight:700;margin:0 0 7px 0;font-family:{FF};">✓ {esc(content.get("right_label", "真实情况"))}</p><p style="font-size:15px;line-height:1.65;color:{TEXT};margin:0;font-family:{FF};">{esc(content.get("right", ""))}</p></td></tr></tbody></table>'
        return f'<section style="margin:20px 0;"><p style="font-size:13px;line-height:1.4;color:{ACCENT};font-weight:700;margin:0;font-family:{FF};">核心判断</p>{table_html}</section>'
    if component_type == "simple_compare_table":
        return render_table(content)
    if component_type == "image_block":
        src = content.get("src", "")
        if src:
            return f'<section style="margin:20px 0;text-align:center;"><img style="display:block;width:100%;max-width:100%;height:auto;border-radius:8px;" src="{html.escape(src, quote=True)}" alt="{html.escape(content.get("alt", "图片"), quote=True)}"></section>'
        return f'<section style="background:{PALE};border:1px dashed #D8DCE2;border-radius:10px;padding:20px;margin:20px 0;text-align:center;"><p style="font-size:13px;line-height:1.6;color:{GREY};margin:0;font-family:{FF};">图片占位：{esc(content.get("alt", "图片"))}</p></section>'
    if component_type == "image_caption":
        return f'<p style="font-size:12px;line-height:1.6;color:#A5A5A5;margin:6px 0 18px 0;text-align:center;font-family:{FF};">{esc(content)}</p>'
    if component_type == "checklist":
        items = content.get("items", []) if isinstance(content, dict) else content
        rows = "".join(f'<p style="font-size:16px;line-height:1.7;color:{TEXT};margin:0 0 10px 0;font-family:{FF};"><span style="display:inline-block;width:6px;height:6px;background:{ACCENT};border-radius:50%;margin-right:10px;vertical-align:3px;"></span>{esc(item)}</p>' for item in items)
        return f'<section style="margin:18px 0;">{rows}</section>'
    if component_type == "numbered_points":
        rows = "".join(f'<p style="font-size:16px;line-height:1.7;color:{TEXT};margin:0 0 14px 0;font-family:{FF};"><span style="display:inline-block;font-size:12px;line-height:1;color:#FFFFFF;background:{ACCENT};border-radius:999px;padding:5px 7px;font-weight:700;margin-right:8px;vertical-align:2px;">{idx + 1:02d}</span><span style="font-weight:700;">{esc(item)}</span></p>' for idx, item in enumerate(content))
        return f'<section style="background:{PALE};border:1px solid {LINE};border-radius:10px;padding:16px 18px;margin:20px 0;">{rows}</section>'
    if component_type == "divider":
        return render_divider(content)
    if component_type == "summary_card":
        return f'<p style="{body_style()}">{esc(content)}</p>'
    if component_type == "references_block":
        rows = "".join(f'<p style="font-size:12px;line-height:1.6;color:#A5A5A5;margin:0 0 6px 0;font-family:{FF};">{esc(item)}</p>' for item in content)
        return f'<section style="margin:18px 0 0 0;padding-top:14px;border-top:1px solid {LINE};">{rows}</section>'
    if component_type == "soft_cta":
        items = content if isinstance(content, list) else [content]
        rows = "".join(f'<p style="font-size:12px;line-height:1.6;color:{GREY};margin:0 0 6px 0;font-family:{FF};">{esc(item)}</p>' for item in items if item)
        return f'<section style="border-top:1px solid {LINE};padding-top:16px;margin:28px 0 0 0;">{rows}</section>' if rows else ""
    library_html = render_library_component(component_type, content)
    if library_html:
        return library_html
    return ""


def render_content_html(tree: dict[str, Any]) -> str:
    return "".join(render_component(component) for component in tree["components"])


def normalized_fidelity_text(text: str) -> str:
    return re.sub(r"[\s，。；：、！？!?;:\-—“”\"'《》（）()【】\[\]]+", "", str(text or ""))


def collect_source_payloads(component: dict[str, Any]) -> list[str]:
    values: list[str] = []
    component_type = component.get("type")
    content = component.get("content")
    if component_type in {"intro_conclusion_card", "summary_card", "image_caption"} and isinstance(content, str):
        values.append(content)
    elif component_type == "soft_cta":
        if isinstance(content, list):
            values.extend(str(item) for item in content)
        elif isinstance(content, str):
            values.append(content)
    elif component_type in {"body_paragraph", "semantic_color_block", "outlined_text_box", "gradient_emphasis_bar", "left_quote", "editorial_note"} and isinstance(content, dict):
        values.append(content.get("text", ""))
    elif component_type == "double_compare" and isinstance(content, dict):
        values.extend([content.get("left", ""), content.get("right", "")])
    elif component_type == "checklist":
        if isinstance(content, dict):
            values.extend(str(item) for item in content.get("items", []))
        elif isinstance(content, list):
            values.extend(str(item) for item in content)
    elif component_type in {"numbered_points", "references_block"} and isinstance(content, list):
        values.extend(str(item) for item in content)
    else:
        values.extend(source_payloads_for_library_component(component_type, content))
    for child in component.get("children", []):
        values.extend(collect_source_payloads(child))
    return [value for value in values if value]


def collect_coverage_payloads(component: dict[str, Any]) -> list[str]:
    values: list[str] = []
    if component.get("type") == "double_compare" and isinstance(component.get("content"), dict):
        values.append(component["content"].get("source", ""))
    else:
        values.extend(collect_source_payloads({**component, "children": []}))
    for child in component.get("children", []):
        values.extend(collect_coverage_payloads(child))
    return [value for value in values if value]


def build_fidelity_report(plan: dict[str, Any], tree: dict[str, Any]) -> dict[str, Any]:
    source_raw = plan.get("source_text", "")
    source = normalized_fidelity_text(source_raw)
    visible_payloads = [value for component in tree.get("components", []) for value in collect_source_payloads(component)]
    coverage_payloads = [value for component in tree.get("components", []) for value in collect_coverage_payloads(component)]
    invented: list[str] = []
    positions: list[int] = []
    search_start = 0
    for payload in visible_payloads:
        normalized = normalized_fidelity_text(payload)
        if not normalized:
            continue
        position = source.find(normalized, search_start)
        if position < 0:
            position = source.find(normalized)
        if position < 0:
            invented.append(payload)
        else:
            positions.append(position)
            search_start = position + len(normalized)
    order_preserved = all(left <= right for left, right in zip(positions, positions[1:]))
    coverage_text = normalized_fidelity_text("".join(coverage_payloads))
    missing_source_segments: list[str] = []
    for segment in plan.get("source_segments", []):
        normalized_segment = normalized_fidelity_text(segment)
        if normalized_segment and normalized_segment not in coverage_text:
            missing_source_segments.append(segment)
    source_heads = plan.get("source_outline", [])
    output_heads = [section.get("heading", "") for section in plan.get("sections", [])]
    headings_preserved = all(heading in output_heads for heading in source_heads)
    unbalanced_source = [segment for segment in plan.get("source_segments", []) if not balanced_pairs(segment)]
    unbalanced_output = [payload for payload in visible_payloads if not balanced_pairs(payload)]
    forbidden = [phrase for phrase in FORBIDDEN_TEMPLATE if phrase in "".join(visible_payloads + output_heads)]
    status = "pass" if not invented and not missing_source_segments and order_preserved and headings_preserved and not unbalanced_source and not unbalanced_output and not forbidden else "fail"
    return {
        "status": status,
        "headings_preserved": headings_preserved,
        "source_headings": source_heads,
        "output_headings": output_heads,
        "source_order_preserved": order_preserved,
        "source_coverage_complete": not missing_source_segments,
        "missing_source_segments": missing_source_segments,
        "invented_content": invented,
        "unbalanced_source_pairs": unbalanced_source,
        "unbalanced_output_pairs": unbalanced_output,
        "template_injection": forbidden,
    }


def marker_usage_report(content_html: str, tree: dict[str, Any]) -> dict[str, Any]:
    counts = {
        "underline": len(re.findall(r"border-bottom:2px solid", content_html, re.I)),
        "strikethrough": len(re.findall(r"text-decoration:line-through", content_html, re.I)),
        "inline_highlight": len(re.findall(r"<span[^>]+padding:1px", content_html, re.I)),
        "color_block": 0, "outlined_text_box": 0, "left_quote": 0, "capsule_label": len(re.findall(r"border-radius:999px", content_html, re.I)),
        "double_compare": 0, "gradient_emphasis_bar": 0, "editorial_note": 0,
        "data_emphasis": len(re.findall(r"<span[^>]*>\d+(?:\.\d+)?\s*(?:%|％|倍|年|天|小时|分钟|元|万|亿|人|次)</span>", content_html, re.I)),
        "divider": 0, "numbered_points": 0, "library_total": 0, "library_by_category": {},
    }
    def walk(component: dict[str, Any]) -> None:
        mapping = {
            "semantic_color_block": "color_block", "emphasis_sentence": "color_block",
            "outlined_text_box": "outlined_text_box",
            "left_quote": "left_quote", "core_quote_card": "left_quote",
            "double_compare": "double_compare", "gradient_emphasis_bar": "gradient_emphasis_bar",
            "editorial_note": "editorial_note", "divider": "divider", "numbered_points": "numbered_points",
        }
        key = mapping.get(component.get("type"))
        if key:
            counts[key] += 1
        category = library_marker_category(component.get("type", ""))
        if category:
            counts["library_total"] += 1
            counts["library_by_category"][category] = counts["library_by_category"].get(category, 0) + 1
        for child in component.get("children", []):
            walk(child)
    for root in tree.get("components", []):
        walk(root)
    return counts


def build_draftbox_payload(plan: dict[str, Any], content_html: str, validation_report: dict[str, Any], marker_report: dict[str, Any]) -> dict[str, Any]:
    return {
        "title": plan["title"],
        "digest": plan["digest"][:120],
        "content_html": content_html,
        "cover_image_brief": plan.get("cover_image_brief", {}),
        "image_asset_list": plan.get("image_assets", []),
        "smart_image_plan": plan.get("smart_image_plan", {}),
        "semantic_marker_report": marker_report,
        "validation_report": validation_report,
        "publish_checklist": [
            "content fidelity passed", "paired punctuation preserved", "source order preserved",
            "semantic markers are meaning-driven and sparse", "one inline marker type maximum per paragraph",
            "gradient emphasis no more than one", "section numbers bound to headings",
            "cover 2.35:1 and center 1:1 crop safe", "inline images 3:4 when needed",
            "third-party copyright watermarks are never removed", "strict_draftbox passed",
            "mobile preview required", "no markdown residue",
        ],
    }


def compile_all(raw: str, profile: str = "strict_draftbox", theme: str = "auto") -> tuple[Any, ...]:
    normalized, tables = normalize_input(raw)
    plan = build_article_plan(normalized, tables)
    theme_name = auto_theme(plan["article_type"]) if theme == "auto" else theme
    theme_profile = apply_theme(theme_name)
    plan["theme"] = theme_name
    plan["theme_profile"] = theme_profile
    rhythm = build_text_rhythm_plan(plan)
    visual = build_visual_plan(plan, theme_name)
    tree = build_component_tree(plan, rhythm, visual, profile)
    raw_html = render_content_html(tree)
    content_html = sanitize_wechat_html(raw_html)
    validation = validate_content_html(content_html, profile)
    visual_report = visual_rhythm_score(content_html)
    fidelity = build_fidelity_report(plan, tree)
    visible_text = html.unescape(re.sub(r"<[^>]+>", "", content_html))
    generated_copy = [label for label in GENERATED_UI_LABELS if label in visible_text and label not in plan.get("source_text", "")]
    fidelity["generated_copy"] = generated_copy
    fidelity["generated_labels"] = len(generated_copy)
    fidelity["rewritten_paragraphs"] = len(fidelity.get("invented_content", []))
    if generated_copy:
        fidelity["status"] = "fail"
    marker_report = marker_usage_report(content_html, tree)
    payload = build_draftbox_payload(plan, content_html, validation, marker_report)
    payload["content_fidelity_report"] = fidelity
    return plan, rhythm, visual, tree, content_html, validation, visual_report, payload, fidelity, marker_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--profile", default="strict_draftbox", choices=["strict_draftbox", "rich_article"])
    parser.add_argument("--theme", default="auto", choices=["auto", "editorial", "business", "minimal", "course"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    raw = Path(args.input).read_text(encoding="utf-8")
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
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(content_html)


if __name__ == "__main__":
    main()
