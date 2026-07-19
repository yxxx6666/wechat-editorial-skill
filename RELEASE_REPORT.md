# Release Report

- Version: `0.5.0`
- Skill ID: `xingchen/wechat-editorial-skill`
- Release scope: 72-marker editorial library, static WeChat renderers, registry/schema/showcase consistency

## Required gates

- Registry contains exactly 72 unique markers.
- Every marker exists in Schema enum and returns non-empty WeChat-safe HTML.
- Every marker appears in the all-markers showcase.
- Generated copy, labels and rewritten paragraphs remain zero.
- Quick, regression, release and independent audit pass.
- Visual QA passes at desktop and mobile widths.

## Verified result

- Quick validation: PASS
- Regression validation: PASS
- Release validation: PASS
- Independent audit: PASS
- Registry markers: 72/72 unique
- Renderers: 72/72 non-empty and P0-free
- Activation layers: auto safe 13, source triggered 33, manual 22, WeChat fallback 4
- Categories: inline 12, heading 10, box/callout 16, quote 6, list/process 10, data/media 10, metadata/reference 8
- Markdown examples: 28/28
- Source-trigger runtime: definition_box and fact_box PASS
- Generated copy: 0
- Generated labels: 0
- Rewritten paragraphs: 0
- P0: 0
- P1: 0
- Visual score range: 92–100
- Desktop visual QA: PASS, no overlap or horizontal overflow
- Mobile visual QA at 390px: PASS, single-column responsive layout
- Full-page visual QA: PASS, all seven categories inspected
- UTF-8, security, cache and compiled artifact scans: PASS
