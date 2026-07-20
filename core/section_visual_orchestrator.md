# Section Visual Orchestrator｜章节视觉编排器

## 目标

让每个有足够信息量的章节形成“章节入口 + 行内细节 + 段落结构或重点组件 + 章节收尾”的视觉节奏。禁止只重复“大序号标题 + 单一色块”。

## 五层编排

1. 章节入口：在 `chapter_double_rule / chapter_corner_frame / chapter_dot_rail / chapter_diamond_mark / large_number_heading` 之间按章节轮换。
2. 行内细节：在 `soft_marker_underline / keyword_corner_outline / dual_tone_phrase` 之间按语义和章节位置变化。
3. 段落结构：连续问题使用 `question_stack`，并列原句使用 `parallel_sentence_rail`，自然对照句使用 `contrast_pair_plain`。
4. 重点组件：定义、事实、案例、风险、注意和洞察继续使用原文块级组件；短章最多 1 个，长章最多 2 个。
5. 章节过渡：在 6 种纯 CSS 分隔符之间轮换，相邻章节不得重复。
6. 微型符号：重点段落可使用段首圆点、菱形或短竖线；重点句可使用角标。
7. 关系结构：递进原句使用 `logic_progress_rail`，连续数据使用 `data_cluster_rail`。
8. 章节收尾：长章节可使用 `chapter_end_signature`；全文最后一句可使用 `closing_focus_frame`，随后使用无文字 `article_end_mark`。

## 不可变边界

- 所有可见文字逐字来自原文。
- 允许改变 HTML 结构和添加纯 CSS 几何符号，但不得生成标签、标题、总结或 CTA。
- 每段最多一种行内标识；同一短语不得重复标识。
- 事实与知识使用蓝色，行动使用绿色，注意使用橙色，风险使用红色，洞察使用紫色。
- `fact_box` 必须使用蓝色，不得借用绿色行动语义。
- 连续块级卡片最多 2 个；结尾禁止连续堆叠多个色块。

## 发布门禁

- `section_visual_coverage.status: pass`
- `dry_sections: []`
- `single_marker_only_sections: []`
- `repeated_adjacent_signatures: []`
- 长章节 `marker_events >= 3`
- 同篇文章的章节视觉签名必须随内容变化。

## v0.6.2 扩展门禁

- `no_separator_long_sections: []`
- `repeated_separator_types: []`
- `decorative_symbol_overload_sections: []`
- `data_marker_underuse_sections: []`
- `quote_style_repetition: false`
- `unused_runtime_markers: []`
