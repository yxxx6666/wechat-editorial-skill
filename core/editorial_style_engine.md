# core/editorial_style_engine.md

## 阶段 2：编辑风格规划

**输入：** raw_article + article_structure
**输出：** style_plan

## 目标

为文章选择一套星辰主题，并给出每个小节的组件映射与颜色使用计划。一篇文章只选一套主题。

## 主题选择规则

| input_type | 默认主题 |
| --- | --- |
| 方法论 / 深度文 / AI 长文 | `xingchen-editorial` |
| 商业分析 / 项目复盘 / 产品解读 | `xingchen-business` |
| 认知 / 读书笔记 / 严肃长文 | `xingchen-minimal` |
| 课程复盘 / 培训 / 时间管理 | `xingchen-course` |

详细色彩与组件见 `references/style-system.md`。

## 输出结构（style_plan）

```yaml
theme: editorial | business | minimal | course
theme_profile: templates/theme-profiles.json#editorial
palette:
  text: "#1F2933"
  heading: "#111827"
  muted: "#6B7280"
  accent: "#1746A2"
  bg: "#F6F8FB"
section_components:
  - heading: "小节标题"
    component: section_title + insight_card
```

## 颜色约束

- 同一篇文章颜色不超过三种（正文色 + 标题色 + 一个强调色，灰与浅背景不计入“重色”）。
- 保持克制高级，不堆叠颜色。
