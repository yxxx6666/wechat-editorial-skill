# Visual Rhythm Validator（视觉节奏校验）v0.3.3

视觉校验不只检查 HTML 安全，还检查是否像成熟公众号编辑排出来的文章。

## 检查项

1. 是否出现“模块 1 / 模块 2”
2. 是否有设计感小标题
3. 是否有开头结论卡片
4. 是否有视觉节奏变化
5. 是否卡片过多
6. 是否全文纯段落
7. 是否重点过多
8. 是否 CTA 太强
9. 是否图注混入正文
10. 是否引用块过丑或过多
11. 是否出现 Skill 元内容
12. 是否出现固定模板句

## 输出

```json
{
  "visual_score": 92,
  "layout_rhythm": "pass",
  "heading_beauty": "pass",
  "component_balance": "pass",
  "cta_style": "pass",
  "issues": []
}
```

## 评分

- 90-100：可直接发布
- 80-89：基本好看，可微调
- 70-79：安全但普通
- 70 以下：不建议发布

release 模式下：`visual_score < 85` 必须 FAIL。

# v0.3.3.1 content_deduplication_engine

- title、digest、intro、emphasis、summary 不得直接复用同一句。
- summary 必须重新压缩，不得复制 intro。
- digest 像导语；intro_conclusion_card 像观点；emphasis_sentence 像重点判断；summary_card 像收束。
- 同一核心句最多出现 2 次，超过则重写。
- actions 只能从原文提取；原文没有行动建议，不生成 checklist。
- 禁止输出通用三连句：先抓住文章的核心判断 / 再看每个部分如何展开 / 最后把方法带回自己的场景。

## Bullet List Visual Hotfix v0.3.3.2

关键判断、问题清单、行动清单中的列表项必须“一行一个真实项目”。禁止输出只有黑点没有文字的空段落；禁止把 `•` 单独放一行、文字另起一行。正确结构是同一个 `<p>` 内包含 `<span>•</span>` 与文本，项目间距用 `margin-bottom` 控制。


## v0.3.4 Section Number & Highlight Checks

新增检查：

- `detached section number`：发现 `01 / 02 / 03` 独立成段且后面紧跟标题时失败。
- `missing key sentence cards`：核心判断卡片不足时扣分。
- 章节编号必须绑定标题，重点句必须形成可扫读的视觉锚点。

验收标准：读者滑动手机时，每隔 1-2 屏能抓到一个标题、一个重点句或一个明确停顿点。


## v0.3.4.1 Natural Rhythm Checks

新增检查：

- `body title block rendered`：strict_draftbox 正文不得重复公众号后台标题。
- `repeated core judgment labels`：不得连续输出多个“核心判断”。
- `too many key cards`：重点卡片过多会扣分。

验收标准：像真人编辑稀疏强调，而不是每一节都被系统贴标签。
