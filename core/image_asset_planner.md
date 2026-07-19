# core/image_asset_planner.md

## 阶段 3：图片资产规划

**输入：** article_structure + style_plan
**输出：** image_asset_plan

## 目标

为文章规划封面图与文内图，输出结构化图片资产清单。详细规则见 `references/image-rules.md`。

## 原则

1. 图片负责氛围、场景和记忆点。
2. 正文观点必须由 HTML 文本表达，不靠图片。
3. 不把核心中文标题写进生成图片。
4. 封面图 21:9，文内图 16:9，行动清单图 3:4，分享卡 1:1。

## 输出结构（image_asset_plan）

```yaml
cover_image_brief:
  ratio: "21:9"
  prompt: "封面图说明"
  text_overlay: "封面建议叠加文字"
image_asset_list:
  - image_id: image_01
    usage: cover | section | concept | action_card
    ratio: "21:9 | 16:9 | 3:4 | 1:1"
    prompt: "图片生成提示词"
    placement: "插入在哪个小节之后"
    requires_upload_to_wechat: true
```

## 必填字段

每张图必须有：用途 usage、比例 ratio、插入位置 placement、提示词 prompt。缺一不可。
