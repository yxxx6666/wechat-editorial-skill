# references/workbuddy-draftbox-rules.md

## WorkBuddy 草稿箱规则

### 发布边界（必须遵守）

- **只进公众号草稿箱，不自动发布，不群发。**
- 图片需先上传到微信素材库，正文使用微信素材 URL。
- 图片 URL 不可用时用文字占位，不让草稿箱报错。

### 输出结构（draftbox_payload）

输出给 WorkBuddy 的结构必须是：

```json
{
  "title": "公众号标题",
  "digest": "120字以内摘要",
  "content_html": "微信公众号安全HTML片段",
  "cover_image_brief": {
    "ratio": "21:9",
    "prompt": "封面图说明",
    "text_overlay": "封面建议叠加文字"
  },
  "image_asset_list": [
    {
      "image_id": "image_01",
      "usage": "cover / section / concept / action_card",
      "ratio": "21:9 / 16:9 / 3:4 / 1:1",
      "prompt": "图片生成提示词",
      "placement": "插入在哪个小节之后",
      "requires_upload_to_wechat": true
    }
  ],
  "publish_checklist": [
    "检查草稿箱样式是否保留",
    "检查图片是否成功上传到微信素材库",
    "检查手机预览字号和间距",
    "检查是否存在样式丢失",
    "检查是否出现 &ensp;、&emsp;、&nbsp; 字样"
  ]
}
```

### 字段要求

- `title`、`digest`、`content_html` 必填。
- `digest` 不超过 120 字。
- `content_html` 必须是微信安全 HTML 片段。
- `image_asset_list` 每项需 image_id / usage / ratio / prompt / placement / requires_upload_to_wechat。
- `publish_checklist` 不可缺失。
