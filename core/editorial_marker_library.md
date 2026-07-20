# Content-Aware Article Visuals

## 目标

v0.5.2 继续将 72 个文章视觉标识统一收录到注册表、Schema、渲染器、展示页和发布测试中。完整组件库不等于一篇文章全部显示。

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
- 全量展示页：`examples/v0.5.2-all-markers-showcase.html`
- 目录：`references/editorial-marker-catalog.md`
