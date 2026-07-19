# 微信公众号正文节奏引擎（wechat_text_rhythm_engine）

> v0.3.2 Publishing Polish。目标不是大改架构，而是把 v0.3.1 的正文节奏、图片说明、中文引用、辅助信息和 release 校验扣到稳定发布级。

## 1. paragraph_group 默认模式

公众号文章不是口播稿。不是每句话都要独立成段。

默认使用 `paragraph_group`：

1. 同一语义组内的短句优先合并。
2. 解释性句子不要单独成段。
3. 案例描述不要一句一行。
4. 背景信息不要一句一行。
5. 只有金句、转折、结论、强提醒可以短句独立。
6. 普通正文默认 2-4 句组成一段。
7. 每段表达一个完整意思。
8. 每段在手机上约 3-6 行。

## 2. 人工公众号节奏目标

好的公众号正文节奏不是平均分布，而是：

```text
自然段
自然段
重点句
自然段
引用卡片
自然段
小标题
自然段
行动清单
总结卡片
轻 CTA
```

禁止：

```text
句子
句子
句子
句子
句子
句子
句子
```

## 3. 短段落阈值

- `short_paragraph`：中文字符数 < 28
- `very_short_paragraph`：中文字符数 < 15
- 连续 short_paragraph >= 6：`paragraph rhythm too fragmented`
- 全文 short_paragraph 比例 > 60%：`too many short paragraphs`
- 全文 very_short_paragraph 比例 > 35%：`too many single-sentence paragraphs`

以上三项在 release 模式下必须失败。

## 4. 长段落阈值

- 单段中文字符数 > 220：`paragraph too long`
- 连续 3 段都 > 180：`dense reading block`

这两个是 warning，不一定 release fail。

## 5. 图片说明识别

以下独立短行必须识别为 `image_caption`，不能进入 `body_paragraph`：

- `图：`
- `图片：`
- `图片说明：`
- `图注：`
- `Caption：`
- `caption:`
- `说明：`（仅图片附近或独立短行）
- `资料图：`
- `配图：`

渲染：12px、line-height 1.6、#A5A5A5、居中、margin 6px 0 18px 0。

## 6. 中文引用保护

`protect_chinese_quotes(text)` / `restore_chinese_quotes(text)`：

1. 中文引号 “……” 内部不能被普通断句拆开。
2. 书名号 《……》 内部不能被拆开。
3. 括号 （……） 内部尽量不要被拆开。
4. 引号内的句号、问号、感叹号不触发普通段落拆分。

引用观点 ≠ 辅助信息。

- 引用观点：14-15px，浅底卡片，左侧细线，行高 1.7，可轻突出。
- 辅助信息：12-13px，浅灰，行高 1.55-1.65，不加粗，不抢正文。

## 7. 重点分层

1. 关键词重点：句内 span 加粗 + accent 色。
2. 重点句：单独成段 + 轻加粗。
3. 重点卡片：浅底卡片 + 左侧线。

质量规则：

- 全文 strong/span font-weight:700 的文字比例 > 12%：`too many bold marks`
- 单段内重点标记超过 2 个：`too many highlights in paragraph`
- 连续 3 段都有加粗：`highlight fatigue`

这些暂为 warning。

## 8. CTA 规则

文末 CTA 是轻提示，不是强广告按钮：12-13px、muted 灰、浅底轻卡片、不使用大面积高亮背景。
