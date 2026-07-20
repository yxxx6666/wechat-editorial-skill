# Content Fidelity Protocol｜纯排版内容保真协议

## 唯一定位

本 Skill 只改变 HTML 结构与视觉样式，不改变文案。原文标题、正文、段落、列表、引用、标点、顺序、事实和 CTA 均视为不可变数据。

## 允许的变化

- 字号、字重、行距、段距、留白、边框、底色和安全内联样式。
- 在原句内部对已有短语添加加粗、下划线、删除线、文字色或浅色背景。
- 把原文中完整、重要的句子在原位置转换成无标题色块或矩形描边框；框中文字必须逐字来自原文，且不得复制。
- 一级大标题可增加与标题绑定的 01/02/03 大序号；序号属于结构标识，不得使用左侧竖线。
- 将原文已有标题、列表、引用、表格和图片转换为等义的微信安全 HTML。
- 使用不承载新语义的纯 CSS 线条、圆点和留白作为视觉节奏。

## 绝对禁止

- 改写、润色、总结、提炼、扩写、删减或重组原文。
- 自动生成核心判断、行动建议、注意事项、风险提醒、最后总结、编辑注、阅读重点、问题、导航、金句、章节编号或 CTA。
- 把普通段落升级成带新标签的结论卡片；允许无标题、无图标、只承载原文句子的稀疏色块。
- 把原文没有的文字、数字、图标含义或观点加入可见正文。
- 为提高视觉评分而复制、移动或删除原句。

## 发布门禁

以下全部满足才允许 Release：

- `source_coverage_complete: true`
- `source_order_preserved: true`
- `headings_preserved: true`
- `heading_count_preserved: true`
- `heading_order_preserved: true`
- `generated_headings: []`
- `invented_content: []`
- `generated_copy: []`
- `generated_labels: 0`
- `color_block_text_from_source: true`
- `color_block_label_empty: true`
- `rewritten_paragraphs: 0`
- `template_injection: []`
- 成对标点完整

任何新增文案均为 P0，立即阻断发布。标题只能来自原文显式结构；无标题原文不得自动生成章节标题。
