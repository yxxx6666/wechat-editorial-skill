# Release Report — v0.5.2

## Release scope

- Fixed deterministic recognition for `01` + next-line headings, same-line `01 标题`, Markdown headings, and HTML `<br>` transport.
- Removed synthetic section-heading generation when the source has no headings.
- Added exact heading count, wording, order, and generated-heading gates.
- Replaced local `可以 / 开始` action matching with explicit instruction plus action-verb classification.
- Added DraftBox `runtime_manifest` with Skill ID, runtime version, entrypoint, compiler, and gate execution status.
- Added the uni-context article regression for five source headings and representative false-action phrases.

## Validation results

- Quick: `PASS`
- Regression: `PASS`
- Release: `PASS`
- Markdown examples: `30/30`
- Marker renderers: `72/72`
- Files: `94`
- P0: `0`
- P1: `0`
- Generated copy: `0`
- Generated labels: `0`
- Rewritten paragraphs: `0`
- Uni-context regression fidelity: `PASS`
- Uni-context visual score: `92`
- Full marker showcase visual QA: `PASS`
- Heading fidelity visual QA: `PASS`
- Horizontal overflow: `0`
- Failed resources: `0`
- Unicode replacement characters: `0`
- Python cache / bytecode in package: `0`

## Runtime contract

```text
skill_id: xingchen/wechat-editorial-skill
runtime_version: 0.5.2
entrypoint: scripts/build_article.py
compiler: scripts/md_to_wechat.py
content_fidelity_gate: executed
semantic_classifier: executed
```

## Release decision

`RESULT: PASS`
