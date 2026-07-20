# references/publish-checklist.md

## 发布前检查清单

### 样式与兼容

- [ ] content_html 是安全片段，无 html/head/body/style/script。
- [ ] 无 class、外部 CSS、CSS 变量。
- [ ] 无 flex / grid / absolute / fixed / animation / hover / media query。
- [ ] 所有样式为内联 style。
- [ ] 无 `&ensp;` / `&emsp;` / `&nbsp;` 字样。

### 手机端预览

- [ ] 微信编辑器手机预览字号与间距正常。
- [ ] 样式没有丢失。
- [ ] 单栏阅读顺畅。

### 图片

- [ ] 封面图 21:9 已准备。
- [ ] 文内图已上传到微信素材库。
- [ ] 正文使用微信素材 URL，无 base64。
- [ ] 每张图有 usage / ratio / placement / prompt。

### 发布边界

- [ ] 只进草稿箱，不自动发布，不群发。
- [ ] title / digest / content_html 齐全。
- [ ] digest 在 120 字以内。

## v0.6.2 视觉标识完整性

- [ ] 实线下划线使用可见前景色，不能使用接近白色的背景色作为线色。
- [ ] 点状、双线和实线下划线在桌面端与 390px 手机端可清楚区分。
- [ ] 关键词角线描边同时保留左线和底线。
- [ ] 输出 HTML 没有被字体栈双引号拆出的未知属性。
- [ ] 没有空 `style` 属性。
- [ ] 展示页 94 个组件均非空、无溢出、无异常属性。
- [ ] 注册表启用分层为 73 个内容自动识别、17 个手动指定、4 个微信降级。

## v0.6.0 章节视觉覆盖

- [ ] `section_visual_coverage.status` 为 `pass`。
- [ ] 没有干巴章节或单标识章节。
- [ ] 相邻章节没有重复视觉签名。
- [ ] 连续卡片不超过 2 个。
- [ ] 事实使用蓝色，绿色只用于明确行动。
