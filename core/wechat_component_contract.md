# 微信公众号组件契约｜v0.4.0

## HTML 白名单

只允许：`section p span strong br img blockquote table tbody tr td`。所有视觉样式使用内联 `style`。禁止 class、id、data-*、事件属性、script、style 标签、flex、grid、定位、动画和 base64 图片。

## 组件

| 组件 | 用途 | 默认上限 |
| --- | --- | --- |
| article_container | 单列正文容器 | 1 |
| title_block | rich_article 内嵌标题 | 0-1 |
| intro_conclusion_card | 普通开篇结论 | 0-1 |
| article_nav | 长文导航 | 0-1 |
| section_title | 章节路标，编号与标题绑定 | 按章节 |
| body_paragraph | 正文自然段 | 按原文 |
| semantic_color_block | 章节级结论 | 1-2 |
| gradient_emphasis_bar | 全文最强判断 | 0-1 |
| left_quote | 完整引用或金句 | 0-2 |
| double_compare | 认知或方法对比 | 0-2 |
| editorial_note | 编辑批注和边界 | 0-1 |
| checklist | 问题、风险或行动清单 | 按原文 |
| numbered_points | 三项以上有序观点 | 0-1 |
| simple_compare_table | 简单表格或复杂表格降级 | 0-2 |
| image_block | 原文图片或占位 | 按原文 |
| image_caption | 12px 图注 | 按图片 |
| divider | 节奏分隔 | 1-3 |
| summary_card | 原文末尾总结 | 0-1 |
| references_block | 来源和声明 | 0-1 |
| soft_cta | 12px 轻 CTA | 0-1 |

## 关键规则

- `strict_draftbox` 不渲染正文主标题。
- 编号必须和标题或内容在同一视觉单元。
- 双栏使用 table；列数不超过 2，普通表格不超过 3 列、8 行。
- 图注不得进入 16px 正文段落。
- 软 CTA 使用 12px 灰色文字，不做按钮。
- 渐变、色块和胶囊不计作普通正文，但参与密度门禁。
