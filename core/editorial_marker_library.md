# Section-Orchestrated Editorial Marker Library

## 目标

v0.6.2 将标识库从 84 个扩展到 94 个，补齐 6 个章节分隔符、段首微型符号、重点句角标、逻辑递进轨道和数据组合轨道；同时把既有列表、数据、引用与文章结束标识接入真实自动编排。完整组件库必须通过 `section_visual_coverage` 证明已经进入文章。

## 四级启用

- `auto_safe`：低风险，可由现有语义规则稀疏自动使用。
- `source_triggered`：仅当原文已有明确结构或前缀时启用。
- `manual`：用户明确指定后启用。
- `wechat_fallback`：互动或复杂布局只输出静态微信安全版本。

## 不可突破的边界

- 所有可见文字必须逐字来自原文。
- 不生成标签、标题、CTA、总结和结论。
- 每个标识必须有注册表记录、Schema 类型、真实渲染器、展示样例和回归测试。
- 默认自动预算不超过 20 类能力，单篇实际出现数量继续受密度控制。
- Tabs、手风琴、Tooltip、动画、Sticky、Grid 和 Flex 不进入微信正文；只能静态降级。

## 文件

- 注册表：`templates/editorial-marker-registry.json`
- 渲染器：`scripts/editorial_marker_library.py`
- 展示生成器：`scripts/render_marker_showcase.py`
- 全量展示页：`examples/v0.6.2-all-markers-showcase.html`
- 目录：`references/editorial-marker-catalog.md`
