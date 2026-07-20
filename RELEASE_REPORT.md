# Release Report — v0.6.4

## Release

- Version: `0.6.4`
- Name: `Unified Macro Framework`
- Skill ID: `xingchen/wechat-editorial-skill`
- Runtime entrypoint: `scripts/build_article.py`
- Compiler: `scripts/md_to_wechat.py`

## Unified macro framework

- One chapter-heading structure per article: enforced.
- One chapter-divider structure per article: enforced.
- Duplicate section-end signature plus divider: removed.
- Body-level semantic variety: retained.

## Structural-prefix hotfix

- `PARALLEL_ITEM::` leakage from intro `lead_groups`: fixed.
- Structural prefixes found in compiled HTML: 0.
- Real-world uni-context regression fidelity: pass.

## Hotfix audit

- Solid underline uses the semantic foreground color and remains visibly distinct from bold text.
- Keyword corner outline uses a visible foreground bottom rule.
- Malformed font-stack attributes: 0.
- Empty style attributes: 0.
- Registry activation split: 73 content-auto / 17 manual / 4 static fallback.

## Scope

- Editorial marker registry: `94` markers.
- New runtime markers: `10`.
- New separators: `6`.
- New micro and relationship markers: paragraph lead symbol, key sentence bracket, logic progress rail, data cluster rail.
- Existing markers activated at runtime: solid/hollow/diamond lists, zero-padded list, data badge, big number, pull quote and article end mark.

## Fidelity gates

- Heading count/text/order preserved: pass.
- Generated headings: 0.
- Generated copy: 0.
- Generated labels: 0.
- Rewritten paragraphs: 0.
- Source coverage complete: pass.

## Visual coverage gates

- `section_visual_coverage`: pass.
- Dry sections: 0.
- Single-marker long sections: 0.
- Repeated adjacent visual signatures: 0.
- Long sections without separators: 0.
- Repeated separator types: 0.
- Decorative symbol overload: 0.
- Data marker underuse: 0.
- Quote style repetition: false.
- Unreachable runtime markers: 0.

## Validation

- Quick: PASS.
- Regression: PASS.
- Release: PASS.
- Marker renderers: 94/94.
- P0: 0.
- P1: 0.
- Full-symbol regression visual score: 100.
- Heading-fidelity regression visual score: 100.
- 390 px mobile horizontal overflow: 0.
- Marker showcase horizontal overflow: 0.
- Replacement characters: 0.
- Cache artifacts: 0.

## Artifacts

- Full marker showcase: `examples/v0.6.4-all-markers-showcase.html`
- Full symbol regression: `examples/regression/full_symbol_orchestration.md`
- Section orchestrator regression: `examples/regression/section_visual_orchestrator.md`
- Heading-fidelity regression: `examples/regression/unicontext_heading_fidelity.md`
