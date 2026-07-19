---
name: wechat-editorial-skill
description: 公众号纯排版与全量文章视觉标识库（v0.5.0）｜把中文文章或 Markdown 排成微信公众号手机端安全 HTML 和草稿箱 JSON，原文逐字保真，72 个文章视觉标识 + 4 套主题 + 智能配图 + 三级验证。当用户需要公众号排版、微信公众号文章美化、Markdown 转公众号 HTML、文章视觉层级、语义高亮、重点卡片、公众号封面与正文配图规划，或需要验证和打包公众号排版时使用。
---

# 公众号纯排版与全量文章视觉标识库

## 默认目标

把原文排成适合微信公众号手机端连续阅读的安全 HTML。原文是不可变数据：不得改写、润色、总结、提炼、扩写、删减、重组或生成任何新文案。语义分析只能选择稀疏的视觉样式，不能生成“核心判断、行动建议、最后总结”等标签。

## 工作流

1. 读取原文，保留标题、原始小标题、引用、图片、图注、表格、参考资料和 CTA。
2. 默认使用 `strict_draftbox`，标题只写入 JSON 的 `title`，不要在正文重复主标题。
3. 运行：

```bash
python scripts/build_article.py <input.md> --output-dir <output-dir> --profile strict_draftbox --theme auto
```

4. 根据文章类型自动选择主题：知识科普用 `editorial`，商业与工具发布用 `business`，观点、故事和读书笔记用 `minimal`，课程说明用 `course`。用户明确指定时使用 `--theme editorial|business|minimal|course`。
5. 检查生成的 `.wechat.html` 和 `.wechat.json`：
   - `content_fidelity_report.status` 必须是 `pass`。
   - `source_coverage_complete` 和 `source_order_preserved` 必须为 `true`。
   - `validation_report.P0` 和 `P1` 必须为空。
   - `visual_report.visual_score` 必须不低于 88。
6. 若任一门禁失败，修复输入解析、组件规划或样式后重新生成，不要绕过验证。
7. 交付 HTML 和 JSON；只有用户明确要求且有可用发布连接器时才执行发布。

## 语义标记

先识别整句主要作用，再选择标记，但只允许修改样式，不能增加文字。转折后的落点优先于局部关键词。不要“能用都用”。

- 下划线：轻强调核心概念、判断或风险。
- 删除线：只用于被修正的旧认知。
- 段内高亮：关键词、行动、提醒和数据。
- 原文重点色块：允许把原文中完整、重要且适合独立呈现的句子原样放入浅色背景与左侧竖线中；不得增加标签、标题或图标文字。短文最多 1 个，中长文最多 2 个。
- 左侧竖线：完整引用或可截图金句。
- 无文字视觉标识：允许使用左侧竖线、短横线、渐变细线、CSS 圆点、局部边框、圆角底纹和原文数字强调；禁止自动生成文字标签。
- 双栏对比：默认关闭，避免拆分和重组原文。
- 渐变重点条：默认关闭，不自动提炼判断。
- 批注：仅保留原文已有批注，不生成“编辑注”。
- 数据强调：百分比、年份、时长、金额、倍数等。
- 分隔线：控制章节节奏，按语义选择短线、点线、渐变线或标签线。
- 编号：只保留原文已有编号，禁止自动增加 01/02/03。

每段最多使用 1 种行内标记；整篇可见强调色最多 3 种；灰色和正文色不计入。详见 [core/semantic_marker_system.md](core/semantic_marker_system.md)。

## v0.5.0 全量标识库

使用组件前读取 `templates/editorial-marker-registry.json` 与 `core/editorial_marker_library.md`。72 个标识全部进入 Skill 包，但不得全部自动启用：`auto_safe` 可稀疏自动使用，`source_triggered` 仅在原文已有明确结构时使用，`manual` 需要用户指定，复杂互动能力统一降级为静态微信安全样式。

任何组件只允许承载原文。不得为了使用组件生成标题、标签、总结、解释、CTA 或补充文案。

## 内容保真

执行前阅读 [core/content_fidelity_protocol.md](core/content_fidelity_protocol.md)。必须检查：

- 原文小标题按顺序保留。
- 导语、正文、引用、图注、参考资料和 CTA 无遗漏。
- 中文引号、书名号、括号和方括号成对。
- 双栏对比可以重组视觉结构，但左右内容必须来自原文。
- 不把课程、项目地址、研究者“关注”等普通陈述误判为 CTA。
- 不生成原文没有的行动清单、案例、数据、机构或结论。

## 图片规划

需要封面或正文配图时，读取 [core/smart_image_planner.md](core/smart_image_planner.md)。默认输出：

- 2.35:1 公众号封面提示词，并兼容中心 1:1 裁切。
- 3:4 正文配图提示词和插入位置。
- 只允许清理自有图或本流程生成图中的模型伪水印和画面瑕疵；不得移除第三方版权水印、署名或 Logo。

## 验证

开发时使用三级验证：

```bash
python scripts/quick_validate.py . --mode quick
python scripts/quick_validate.py . --mode regression
python scripts/quick_validate.py . --mode release
```

发布 Skill 前必须运行 `release`。组件允许范围和微信 HTML 约束见 [core/wechat_component_contract.md](core/wechat_component_contract.md)。
