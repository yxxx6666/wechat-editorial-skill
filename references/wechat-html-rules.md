# 微信公众号安全 HTML 规则（v0.3.0）

默认 profile：`strict_draftbox`。完整定义见 `core/wechat_compat_profiles.md`。

## strict_draftbox allowed_tags

`section` / `p` / `span` / `strong` / `br` / `img` / `blockquote` / `table` / `tbody` / `tr` / `td`

## rich_article allowed_tags（可选，不是默认）

在 strict_draftbox 基础上额外允许 `h1/h2/h3/ul/ol/li`。

## 禁止

- 完整网页标签：`html/head/body`
- 样式脚本：`style/script/link/meta`
- 危险或不稳定标签：`div/iframe/svg/video/canvas/button/form/input`
- 属性：`class/id/data-*` 和所有 `on*` 事件属性
- CSS：flex/grid/absolute/fixed/sticky/animation/transition/keyframes/hover/CSS 变量/外部字体/base64
- 空格实体：`&nbsp;` / `&ensp;` / `&emsp;`

## strict_draftbox 标题和列表

标题、列表必须用 `p + span` 模拟，不使用 h1/h2/h3/ul/ol/li。

## 图片

图片不使用 base64。图片观点不能替代正文观点。图片应有 caption 或 placement。
