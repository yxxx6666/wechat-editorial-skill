# references/forbidden-html.md

## 禁用清单（微信公众号）

以下内容出现在 content_html 中均为不合格，校验器会报 P0：

| 禁用 | 说明 |
| --- | --- |
| `<html>` / `<head>` / `<body>` | 只输出片段 |
| `<style>` | 不能用样式标签 |
| `<script>` | 不能用脚本 |
| `class="..."` | 不能用 class |
| 外部 CSS / `<link rel=stylesheet>` | 不能引入外部样式 |
| `var(--x)` CSS 变量 | 不支持 |
| `display:flex` | 不支持 |
| `display:grid` | 不支持 |
| `position:absolute` / `position:fixed` | 不支持 |
| `animation` / `:hover` / `@media` | 不支持 |
| `&ensp;` / `&emsp;` / `&nbsp;` | 不用 HTML 空格实体 |
| `base64` 图片 | 不用 base64 |

## 替代方案

- 间距 → 用 `margin` / `padding`。
- 多列 → 改为单栏堆叠。
- 空格对齐 → 用 `span` + `margin-right`。
- 图片 → 微信素材 URL 或占位符。
