# 微信公众号兼容 Profile（wechat_compat_profiles）

> v0.3.0 新增。默认 profile 是 `strict_draftbox`，目标是复制到微信公众号草稿箱后尽量不变形。`rich_article` 只是可选增强模式，不作为默认输出。

## profile: strict_draftbox（默认）

### allowed_tags

`section` / `p` / `span` / `strong` / `br` / `img` / `blockquote` / `table` / `tbody` / `tr` / `td`

### forbidden_tags

`html` / `head` / `body` / `style` / `script` / `div` / `iframe` / `svg` / `video` / `canvas` / `h1` / `h2` / `h3` / `ul` / `ol` / `li` / `link` / `meta` / `button` / `form` / `input`

### allowed_attributes

- 全部标签：`style`
- `img`：`src` / `alt` / `style`
- `table`：`style`
- `td`：`style` / `colspan` / `rowspan`

### forbidden_attributes

`class` / `id` / `data-*` / `onclick` / `onerror` / `onload` / 所有 `on*` 事件属性

### forbidden_css

`display:flex` / `display:grid` / `position:absolute` / `position:fixed` / `position:sticky` / `animation` / `transition` / `@keyframes` / `:hover` / `var(--*)` / CSS 变量 / 外部字体 / `url(data:)`

### image_rules

- 图片必须是微信素材 URL、普通 HTTPS 图片占位或本地生成后的上传占位。
- 禁止 base64 图片。
- 图片必须内联 style，常用 `width:100%;display:block;border-radius:8px;`。
- 图片之后应有 `image_caption` 或明确 placement；无 caption 记为 P1 warning。

### space_entity_rules

- 禁止使用 `&nbsp;`、`&ensp;`、`&emsp;` 做间距。
- 视觉间距必须通过 `margin` / `padding` / `span margin-right` 实现。

### title_and_list_rules

- 严格模式下不使用 `h1/h2/h3/ul/ol/li`。
- 标题用 `p + span` 模拟。
- 列表用多个 `p` 和编号 `span` 模拟。

## profile: rich_article（可选，不是默认）

### allowed_tags

`section` / `p` / `span` / `strong` / `br` / `img` / `blockquote` / `table` / `tbody` / `tr` / `td` / `h1` / `h2` / `h3` / `ul` / `ol` / `li`

### forbidden_tags

`html` / `head` / `body` / `style` / `script` / `div` / `iframe` / `svg` / `video` / `canvas` / `link` / `meta` / `button` / `form` / `input`

### allowed_attributes

同 `strict_draftbox`，额外允许 `h1/h2/h3/ul/ol/li` 使用内联 `style`。

### forbidden_attributes

同 `strict_draftbox`。

### forbidden_css

同 `strict_draftbox`。

### image_rules

同 `strict_draftbox`。

### space_entity_rules

同 `strict_draftbox`。

### usage_note

`rich_article` 只在用户明确要求保留语义标题或列表时使用。默认永远使用 `strict_draftbox`。
