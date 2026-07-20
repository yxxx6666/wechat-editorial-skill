#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three-level validator: quick, regression, release."""
from __future__ import annotations

import argparse
import json
import re
import sys
sys.dont_write_bytecode = True
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from md_to_wechat import compile_all, render_component, semantic_marker_role, VISUAL_HEADING_TYPES

VERSION = "0.6.2"
REQUIRED = [
    "SKILL.md", "agents/openai.yaml", "README.md", "VERSION.md", "CHANGELOG.md", "pipeline.yaml",
    "scripts/md_to_wechat.py", "scripts/build_article.py", "scripts/sanitize_wechat_html.py",
    "scripts/validate_content_html.py", "scripts/visual_rhythm_validator.py",
    "core/semantic_marker_system.md", "core/content_aware_article_visual.md", "core/content_fidelity_protocol.md", "core/wechat_component_contract.md", "core/section_visual_orchestrator.md",
    "references/semantic-marker-examples.md", "references/editorial-marker-catalog.md", "templates/theme-profiles.json", "templates/editorial-marker-registry.json",
    "scripts/editorial_marker_library.py", "scripts/render_marker_showcase.py", "core/editorial_marker_library.md",
    "examples/v0.6.2-all-markers-showcase.html",
    "schema/article_plan.schema.json", "schema/component_tree.schema.json", "schema/draftbox_payload.schema.json",
]


def check_skill_frontmatter(errors: list[str]) -> None:
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append("SKILL.md missing valid YAML frontmatter")
        return
    try:
        import yaml
        data = yaml.safe_load(match.group(1))
    except Exception as exc:
        errors.append(f"SKILL.md frontmatter parse failed: {exc}")
        return
    if set(data or {}) != {"name", "description"}:
        errors.append("SKILL.md frontmatter must contain only name and description")
    if (data or {}).get("name") != "wechat-editorial-skill":
        errors.append("SKILL.md name must be wechat-editorial-skill")


def static_checks(errors: list[str], warnings: list[str]) -> None:
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            errors.append("missing " + rel)
    check_skill_frontmatter(errors)
    schema_contract_checks(errors)
    marker_library_checks(errors)
    for rel in ["README.md", "VERSION.md", "pipeline.yaml", "RELEASE_REPORT.md"]:
        path = ROOT / rel
        if path.exists() and VERSION not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel} missing current version {VERSION}")
    for path in ROOT.rglob("*"):
        if path.is_dir():
            if path.name == "__pycache__":
                errors.append("cache directory found: " + str(path.relative_to(ROOT)))
            continue
        if path.suffix == ".pyc":
            errors.append("compiled cache found: " + str(path.relative_to(ROOT)))
        if path.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json", ".html", ".txt"}:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                errors.append(f"UTF-8 decode failed: {path.relative_to(ROOT)}: {exc}")
                continue
            if chr(0xFFFD) in text:
                errors.append("replacement character found: " + str(path.relative_to(ROOT)))
    for path in (ROOT / "scripts").glob("*.py"):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc:
            errors.append(f"python compile failed: {path.name}: {exc}")
    try:
        themes = json.loads((ROOT / "templates/theme-profiles.json").read_text(encoding="utf-8"))
        if set(themes) != {"editorial", "business", "minimal", "course"}:
            errors.append("theme profiles incomplete")
    except Exception as exc:
        errors.append(f"theme profile parse failed: {exc}")


def _resolve_local_ref(root_schema: dict, ref: str) -> dict:
    if not ref.startswith("#/"):
        raise ValueError(f"unsupported non-local schema reference: {ref}")
    node = root_schema
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            raise ValueError(f"unresolved schema reference: {ref}")
        node = node[part]
    if not isinstance(node, dict):
        raise ValueError(f"schema reference does not resolve to an object: {ref}")
    return node


def _fallback_validate(instance, schema: dict, root_schema: dict | None = None, path: str = "$") -> None:
    """Validate the JSON Schema features used by this package when jsonschema is unavailable."""
    root_schema = root_schema or schema
    if "$ref" in schema:
        _fallback_validate(instance, _resolve_local_ref(root_schema, schema["$ref"]), root_schema, path)
        return
    if "enum" in schema and instance not in schema["enum"]:
        raise ValueError(f"{path}: {instance!r} is not one of {schema['enum']!r}")
    expected = schema.get("type")
    checks = {
        "object": lambda value: isinstance(value, dict),
        "array": lambda value: isinstance(value, list),
        "string": lambda value: isinstance(value, str),
        "boolean": lambda value: isinstance(value, bool),
        "integer": lambda value: isinstance(value, int) and not isinstance(value, bool),
        "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
        "null": lambda value: value is None,
    }
    if expected and expected in checks and not checks[expected](instance):
        raise ValueError(f"{path}: expected {expected}, got {type(instance).__name__}")
    if isinstance(instance, dict):
        missing = [field for field in schema.get("required", []) if field not in instance]
        if missing:
            raise ValueError(f"{path}: missing required fields {missing}")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                _fallback_validate(value, properties[key], root_schema, f"{path}.{key}")
            elif schema.get("additionalProperties") is False:
                raise ValueError(f"{path}: additional property {key!r} is not allowed")
    if isinstance(instance, list) and isinstance(schema.get("items"), dict):
        for index, value in enumerate(instance):
            _fallback_validate(value, schema["items"], root_schema, f"{path}[{index}]")
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise ValueError(f"{path}: string shorter than minLength {schema['minLength']}")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            raise ValueError(f"{path}: string longer than maxLength {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], instance):
            pass
        elif "pattern" in schema:
            raise ValueError(f"{path}: string does not match pattern {schema['pattern']!r}")
    if "not" in schema:
        try:
            _fallback_validate(instance, schema["not"], root_schema, path)
        except ValueError:
            pass
        else:
            raise ValueError(f"{path}: instance matches forbidden schema")


def schema_contract_checks(errors: list[str]) -> None:
    """Catch emitted component types that are missing from the schema enum."""
    schema = json.loads((ROOT / "schema/component_tree.schema.json").read_text(encoding="utf-8"))
    allowed = set(schema["$defs"]["component"]["properties"]["type"]["enum"] )
    source = (ROOT / "scripts/md_to_wechat.py").read_text(encoding="utf-8")
    emitted = set(re.findall(r"comp\(\s*[\"']([a-z0-9_]+)[\"']", source))
    missing = sorted(emitted - allowed)
    if missing:
        errors.append(f"component types emitted by renderer but missing from schema enum: {missing}")
    invalid = {
        "profile": "strict_draftbox",
        "components": [{"type": "__invalid_component__", "role": "test", "content": {}, "style_token": "body"}],
    }
    try:
        _fallback_validate(invalid, schema)
    except ValueError:
        pass
    else:
        errors.append("internal schema fallback failed its enum rejection self-test")


def marker_library_checks(errors: list[str]) -> None:
    from sanitize_wechat_html import sanitize
    from validate_content_html import validate
    registry = json.loads((ROOT / "templates/editorial-marker-registry.json").read_text(encoding="utf-8"))
    markers = registry.get("markers", [])
    if len(markers) != 94:
        errors.append(f"marker registry must contain 94 markers, found {len(markers)}")
    ids = [item.get("id") for item in markers]
    if len(ids) != len(set(ids)):
        errors.append("marker registry contains duplicate ids")
    allowed_activations = {"content_auto", "manual", "wechat_fallback"}
    required = {"id", "name_zh", "category", "activation", "wechat_support", "source_policy", "generated_text_policy", "density_group", "renderer", "sample", "source_fields"}
    schema = json.loads((ROOT / "schema/component_tree.schema.json").read_text(encoding="utf-8"))
    allowed = set(schema["$defs"]["component"]["properties"]["type"]["enum"])
    showcase = (ROOT / "examples/v0.6.2-all-markers-showcase.html").read_text(encoding="utf-8") if (ROOT / "examples/v0.6.2-all-markers-showcase.html").exists() else ""
    activation_counts = {name: sum(1 for item in markers if item.get("activation") == name) for name in allowed_activations}
    if activation_counts != {"content_auto": 73, "manual": 17, "wechat_fallback": 4}:
        errors.append(f"marker activation split invalid: {activation_counts}")
    if 'border-bottom:2px solid #1746A2' not in showcase:
        errors.append("solid underline visibility gate failed")
    if 'border-left:2px solid #6B46C1;border-bottom:2px solid #6B46C1' not in showcase:
        errors.append("keyword corner outline visibility gate failed")
    if re.search(r'style="[^"<>]*font-family:[^"<>]*"(?:Segoe UI|PingFang SC|Microsoft YaHei)"', showcase):
        errors.append("showcase contains attribute-breaking font-family quotes")
    if re.search(r'style=(?:""|(?=>))', showcase):
        errors.append("showcase contains empty style attribute")
    for item in markers:
        marker_id = item.get("id", "")
        if set(item) != required:
            errors.append(f"marker registry fields invalid for {marker_id}")
        if item.get("activation") not in allowed_activations:
            errors.append(f"invalid activation for {marker_id}")
        if item.get("generated_text_policy") != "forbidden":
            errors.append(f"generated text not forbidden for {marker_id}")
        if marker_id not in allowed:
            errors.append(f"registry marker missing from schema enum: {marker_id}")
        rendered = sanitize(render_component({"type": marker_id, "role": "registry_test", "content": item.get("sample"), "style_token": "test", "children": []}))
        if not rendered:
            errors.append(f"marker renderer returned empty HTML: {marker_id}")
        else:
            validation = validate(rendered)
            if validation.get("P0"):
                errors.append(f"marker renderer P0 for {marker_id}: {validation['P0']}")
        if f'data-marker-id="{marker_id}"' not in showcase:
            errors.append(f"marker missing from showcase: {marker_id}")


def schema_checks(result: dict, errors: list[str], warnings: list[str]) -> None:
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    mapping = {
        "article_plan": "article_plan.schema.json",
        "component_tree": "component_tree.schema.json",
        "draftbox_payload": "draftbox_payload.schema.json",
    }
    for key, filename in mapping.items():
        try:
            schema = json.loads((ROOT / "schema" / filename).read_text(encoding="utf-8"))
            if jsonschema is not None:
                jsonschema.validate(result[key], schema)
            else:
                _fallback_validate(result[key], schema)
        except Exception as exc:
            errors.append(f"schema validation failed for {key}: {exc}")


def compile_case(path: Path, errors: list[str], warnings: list[str], require_all_markers: bool = False) -> dict:
    raw = path.read_text(encoding="utf-8")
    plan, rhythm, visual, tree, content_html, validation, visual_report, payload, fidelity, marker_report = compile_all(raw)
    result = {
        "article_plan": plan, "text_rhythm_plan": rhythm, "visual_plan": visual, "component_tree": tree,
        "content_html": content_html, "draftbox_payload": payload, "validation_report": validation,
        "visual_report": visual_report, "content_fidelity_report": fidelity, "semantic_marker_report": marker_report,
        "section_visual_coverage": payload.get("section_visual_coverage", {}),
    }
    label = str(path.relative_to(ROOT))
    if fidelity.get("status") != "pass":
        errors.append(f"{label}: fidelity failed: {fidelity}")
    if validation.get("P0"):
        errors.append(f"{label}: P0: {validation['P0']}")
    if validation.get("P1"):
        errors.append(f"{label}: P1: {validation['P1']}")
    if visual_report.get("visual_score", 0) < 88:
        errors.append(f"{label}: visual score below 88: {visual_report}")
    if "visual_plan" in tree:
        errors.append(f"{label}: visual_plan leaked into component_tree")
    if not fidelity.get("source_coverage_complete"):
        errors.append(f"{label}: source coverage incomplete")
    if fidelity.get("generated_copy"):
        errors.append(f"{label}: generated copy found: {fidelity['generated_copy']}")
    if marker_report.get("gradient_emphasis_bar", 0) or marker_report.get("double_compare", 0) or marker_report.get("editorial_note", 0):
        errors.append(f"{label}: generative editorial components found: {marker_report}")
    source_length = len(re.sub(r"\s+", "", raw))
    color_limit = max(2, min(4, source_length // 500 + 1))
    if marker_report.get("color_block", 0) > color_limit:
        errors.append(f"{label}: too many source-text color blocks: {marker_report.get('color_block')} > {color_limit}")
    if marker_report.get("outlined_text_box", 0) > color_limit:
        errors.append(f"{label}: too many outlined text boxes: {marker_report.get('outlined_text_box')} > {color_limit}")
    source_headings = plan.get("source_outline", [])
    heading_components: list[dict] = []
    def collect_headings(component: dict) -> None:
        if component.get("type") in VISUAL_HEADING_TYPES and component.get("role") == "section_heading":
            heading_components.append(component)
        for child in component.get("children", []):
            collect_headings(child)
    for component in tree.get("components", []):
        collect_headings(component)
    if source_headings and len(heading_components) != len(source_headings):
        errors.append(f"{label}: large numbered heading renderer missing")
    if fidelity.get("source_headings") != fidelity.get("output_headings"):
        errors.append(f"{label}: source/output heading mismatch")
    if fidelity.get("generated_headings"):
        errors.append(f"{label}: generated headings found: {fidelity['generated_headings']}")
    def check_source_blocks(component: dict) -> None:
        if component.get("type") in {"semantic_color_block", "outlined_text_box"}:
            content = component.get("content") or {}
            text = str(content.get("text", "")).strip()
            kind = component.get("type")
            if not text:
                errors.append(f"{label}: empty {kind}")
            if text and text not in raw:
                errors.append(f"{label}: {kind} text not found verbatim in source: {text}")
            if content.get("label") or content.get("icon"):
                errors.append(f"{label}: {kind} contains generated label or icon")
        if component.get("type") in VISUAL_HEADING_TYPES and component.get("role") == "section_heading":
            content = component.get("content") or {}
            if not content.get("index"):
                errors.append(f"{label}: heading missing large index")
        for child in component.get("children", []):
            check_source_blocks(child)
    for component in tree.get("components", []):
        check_source_blocks(component)
    schema_checks(result, errors, warnings)
    if require_all_markers:
        required_components = {"double_compare", "gradient_emphasis_bar", "semantic_color_block", "editorial_note", "numbered_points", "left_quote", "divider"}
        types: set[str] = set()
        def walk(component: dict) -> None:
            types.add(component.get("type", ""))
            for child in component.get("children", []):
                walk(child)
        for component in tree.get("components", []):
            walk(component)
        missing = required_components - types
        if missing:
            errors.append(f"{label}: semantic components missing: {sorted(missing)}")
        for key in ("strikethrough", "inline_highlight", "data_emphasis"):
            if marker_report.get(key, 0) < 1:
                errors.append(f"{label}: marker missing: {key}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=str(ROOT))
    parser.add_argument("--mode", choices=["quick", "regression", "release"], default="quick")
    args = parser.parse_args()
    if Path(args.root).resolve() != ROOT.resolve():
        print("WARNING: root argument is ignored; validator uses its own skill root")
    started = time.time()
    errors: list[str] = []
    warnings: list[str] = []
    print(f"mode: {args.mode}")
    print("[1/3] static checks")
    static_checks(errors, warnings)

    print("[2/3] compile checks")
    quick_cases = [ROOT / "examples/semantic_marker_system.md", ROOT / "examples/quote_integrity.md"]
    for path in quick_cases:
        compile_case(path, errors, warnings, require_all_markers=False)
    underline = compile_case(ROOT / "examples/inline_underline.md", errors, warnings)
    if underline["semantic_marker_report"].get("underline", 0) < 1:
        errors.append("examples/inline_underline.md: underline marker missing")
    quote_html = compile_case(ROOT / "examples/quote_integrity.md", errors, warnings)["content_html"]
    exact_quote = "“系统的意义，不是让人少思考，而是让人把注意力放在真正重要的判断上。”"
    if quote_html.count(exact_quote) != 1:
        errors.append("quote integrity regression failed")

    if args.mode in {"regression", "release"}:
        regression = [
            ROOT / "examples/before_after/raw_dirty_input.md",
            ROOT / "examples/before_after/raw_cta_article.md",
            ROOT / "examples/before_after/raw_with_image_caption.md",
            ROOT / "examples/visual_polish/bullet_spacing.md",
            ROOT / "examples/visual_polish/table_degrade.md",
            ROOT / "examples/visual_polish/attention_marker_article.md",
            ROOT / "examples/regression/unicontext_heading_fidelity.md",
            ROOT / "examples/regression/section_visual_orchestrator.md",
            ROOT / "examples/regression/full_symbol_orchestration.md",
        ]
        for path in regression:
            compile_case(path, errors, warnings)

    if args.mode == "release":
        print("[3/3] full example suite")
        checked = set(quick_cases + [ROOT / "examples/inline_underline.md"])
        for path in sorted((ROOT / "examples").rglob("*.md")):
            if path not in checked:
                compile_case(path, errors, warnings)
    else:
        print("[3/3] full suite skipped")


    content_case = ROOT / "examples/content_aware_article_visual.md"
    if content_case.exists():
        compiled = compile_case(content_case, errors, warnings)
        roles = compiled["semantic_marker_report"].get("semantic_role_counts", {})
        if len([k for k,v in roles.items() if v]) < 2:
            errors.append("content-aware article must activate at least two semantic roles")
        if compiled["semantic_marker_report"].get("library_total", 0) < 4:
            errors.append("content-aware article must activate at least four library markers")

    unicontext_case = ROOT / "examples/regression/unicontext_heading_fidelity.md"
    if unicontext_case.exists():
        compiled = compile_case(unicontext_case, errors, warnings)
        expected = [
            "为什么负面内容总能赢",
            "为什么身份开始压过品格",
            "为什么所有人都在和世界冠军比较",
            "为什么注意力变成了一场战争",
            "问题不只是网络，而是生活失去了房间",
        ]
        actual = [section.get("heading", "") for section in compiled["article_plan"].get("sections", []) if section.get("heading")]
        if actual != expected:
            errors.append(f"unicontext heading fidelity regression failed: {actual}")
        false_actions = [
            "可以开一些只有彼此才懂的玩笑",
            "可以跨越语言传播",
            "可以在一秒钟内识别的信息",
            "人们开始害怕误解",
            "可以看到战争、股市、明星离婚、朋友旅行、同行成功和陌生人的愤怒",
        ]
        misclassified = [text for text in false_actions if semantic_marker_role(text) == "action"]
        if misclassified:
            errors.append(f"unicontext descriptive phrases misclassified as actions: {misclassified}")
        true_actions = ["少看所有人的排行榜，多记录自己的长期变化。", "用主动选择的订阅，替代永远刷不完的推荐。"]
        missing_actions = [text for text in true_actions if semantic_marker_role(text) != "action"]
        if missing_actions:
            errors.append(f"unicontext explicit actions not classified as actions: {missing_actions}")
        htmlish = "# 测试文章<br>01<br>为什么负面内容总能赢<br>正文。<br>02 为什么身份开始压过品格<br>正文。"
        htmlish_plan = compile_all(htmlish)[0]
        htmlish_headings = [section.get("heading", "") for section in htmlish_plan.get("sections", []) if section.get("heading")]
        if htmlish_headings != ["为什么负面内容总能赢", "为什么身份开始压过品格"]:
            errors.append(f"HTML break heading transport regression failed: {htmlish_headings}")
        _, _, _, unstructured_tree, _, _, _, unstructured_payload, unstructured_fidelity, _ = compile_all("# 无小标题文章\n\n正文只有普通段落。第二句话继续说明。")
        if any(component.get("type") in VISUAL_HEADING_TYPES and component.get("role") == "section_heading" for root_component in unstructured_tree.get("components", []) for component in root_component.get("children", [])):
            errors.append("unstructured source must not receive generated section headings")
        manifest = unstructured_payload.get("runtime_manifest", {})
        if manifest.get("runtime_version") != VERSION or manifest.get("content_fidelity_gate") != "executed":
            errors.append(f"runtime manifest missing or stale: {manifest}")
        if unstructured_fidelity.get("generated_headings"):
            errors.append(f"unstructured source generated headings: {unstructured_fidelity['generated_headings']}")
        coverage = compiled.get("section_visual_coverage", {})
        if coverage.get("status") != "pass":
            errors.append(f"unicontext section visual coverage failed: {coverage}")
        rows = coverage.get("sections", [])
        if len(rows) != 5:
            errors.append(f"unicontext visual coverage section count failed: {len(rows)}")
        for row in rows:
            if row.get("marker_events", 0) < 3 or len(row.get("marker_types", [])) < 3:
                errors.append(f"unicontext dry section found: {row}")
        signatures = [row.get("visual_signature", "") for row in rows]
        if len(signatures) != len(set(signatures)):
            errors.append(f"unicontext repeated visual signatures: {signatures}")

    orchestrator_case = ROOT / "examples/regression/section_visual_orchestrator.md"
    if orchestrator_case.exists():
        compiled = compile_case(orchestrator_case, errors, warnings)
        component_types: set[str] = set()
        def collect_component_types(component: dict) -> None:
            component_types.add(component.get("type", ""))
            for child in component.get("children", []):
                collect_component_types(child)
        for component in compiled["component_tree"].get("components", []):
            collect_component_types(component)
        required_orchestrated = {"parallel_sentence_rail", "question_stack", "closing_focus_frame", "article_end_mark", "short_double_divider"}
        missing = required_orchestrated - component_types
        if missing:
            errors.append(f"section visual orchestrator components missing: {sorted(missing)}")
        coverage = compiled.get("section_visual_coverage", {})
        if coverage.get("status") != "pass" or coverage.get("dry_sections") or coverage.get("repeated_adjacent_signatures"):
            errors.append(f"section visual orchestrator coverage failed: {coverage}")

    full_symbol_case = ROOT / "examples/regression/full_symbol_orchestration.md"
    if full_symbol_case.exists():
        compiled = compile_case(full_symbol_case, errors, warnings)
        component_types: set[str] = set()
        def collect_full_symbol_types(component: dict) -> None:
            component_types.add(component.get("type", ""))
            for child in component.get("children", []):
                collect_full_symbol_types(child)
        for component in compiled["component_tree"].get("components", []):
            collect_full_symbol_types(component)
        required_new = {
            "short_double_divider", "diamond_line_divider", "dot_chain_divider", "dual_tone_divider",
            "center_node_divider", "chapter_transition_divider", "paragraph_lead_symbol",
            "key_sentence_bracket", "logic_progress_rail", "data_cluster_rail",
        }
        required_existing = {
            "solid_circle_list", "hollow_circle_list", "diamond_list", "zero_padded_list",
            "big_number", "pull_quote", "article_end_mark",
        }
        missing = (required_new | required_existing) - component_types
        if missing:
            errors.append(f"full symbol runtime components missing: {sorted(missing)}")
        coverage = compiled.get("section_visual_coverage", {})
        runtime_types = set(coverage.get("runtime_marker_types", []))
        if "data_badge" not in runtime_types:
            errors.append("full symbol runtime data badge missing")
        if coverage.get("status") != "pass" or coverage.get("repeated_separator_types") or coverage.get("unused_runtime_markers") or coverage.get("decorative_symbol_overload_sections"):
            errors.append(f"full symbol coverage failed: {coverage}")

    for warning in sorted(set(warnings)):
        print("WARNING:", warning)
    print("elapsed_seconds:", round(time.time() - started, 2))
    if errors:
        print("RESULT: FAIL")
        for error in errors:
            print("-", error)
        raise SystemExit(1)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
