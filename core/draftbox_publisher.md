# core/draftbox_publisher.md

## 阶段 5：草稿箱发布封装

**输入：** title + digest + content_html + image_asset_plan
**输出：** draftbox_payload

## 目标

把渲染结果封装成 WorkBuddy 可直接发布到公众号草稿箱的结构。详细规则见 `references/workbuddy-draftbox-rules.md`。

## 发布边界

- **只进公众号草稿箱，不自动发布，不群发。**
- 图片需先上传到微信素材库，正文使用微信素材 URL。
- 图片 URL 不可用时，使用文字占位提醒，不让草稿箱报错。

## 输出结构（draftbox_payload）

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

## 必填

`title`、`digest`、`content_html` 三项缺一不可，否则为 P0 问题。
