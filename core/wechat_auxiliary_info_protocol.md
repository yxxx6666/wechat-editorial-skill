# 辅助信息小字协议（wechat_auxiliary_info_protocol）

> v0.2.1 新增。正文负责阅读，引用 / 注释 / 来源 / 引流负责辅助。辅助信息必须降级显示，不能和正文抢视觉权重。

## 1. 适用范围

以下内容一律进入「辅助信息小字系统」：

- 引用来源
- 资料出处
- 图片注释
- 作者说明
- 参考链接
- 免责声明
- 引流文案
- 关注提示
- 二维码说明
- 往期推荐
- WorkBuddy 指令类说明
- 公众号名片前后的补充文字

## 2. 字号规则

| 信息类型 | 字号 | 颜色 | 样式 |
| --- | --- | --- | --- |
| 正文 | 15px–16px | #2A2E34 / #333333 | 主阅读层 |
| 正文重点 | 15px–16px | 主强调色或正文色 | 加粗 / 轻卡片 |
| 引用块 | 13px | #777777 / #888888 | 左侧浅灰竖线，轻缩进 |
| 图片注释 | 12px | #999999 / #A5A5A5 | 图片下方，小字 |
| 来源说明 | 12px | #A5A5A5 | 不加粗 |
| 作者介绍 | 12px–13px | #888888 | 文末小卡片 |
| 参考资料 | 12px | #999999 | 细分割线后 |
| 引流说明 | 12px–13px | #888888 | 轻卡片，不硬广 |
| 二维码说明 | 12px | #999999 | 二维码下方 |
| 免责声明 | 12px | #A5A5A5 | 文末 |

## 3. 强制规则

1. 辅助信息不得使用正文同级字号。
2. 辅助信息不得使用主标题 / 二级标题样式。
3. 辅助信息不得使用大面积强调色。
4. 辅助信息默认使用 12px–13px、小行高、浅灰色。
5. 除非引用本身是文章核心金句，否则不得做成大卡片。
6. 引流信息只做轻提示，不做强营销按钮。
7. 图片说明、资料来源、免责声明必须比正文更轻。

## 4. 推荐 HTML 组件

### 引用块

```html
<section style="margin:24px 0;padding:12px 14px;border-left:3px solid #D8D8D8;background:#F8F8F8;">
  <p style="margin:0;font-size:13px;line-height:1.8;color:#777777;font-family:FF;">这里是引用内容。</p>
</section>
```

### 图片注释

```html
<p style="margin:8px 0 24px;font-size:12px;line-height:1.6;color:#A5A5A5;text-align:center;font-family:FF;">图：图片说明 / 来源说明</p>
```

### 参考资料

```html
<section style="margin:32px 0 0;padding-top:16px;border-top:1px solid #EAEAEA;">
  <p style="margin:0 0 8px;font-size:13px;line-height:1.6;color:#666666;font-weight:600;font-family:FF;">参考资料</p>
  <p style="margin:0;font-size:12px;line-height:1.8;color:#999999;font-family:FF;">[1] 来源名称，链接或说明。</p>
</section>
```

### 文末轻引流

```html
<section style="margin:36px 0 0;padding:16px;background:#F8F8F8;border-radius:10px;">
  <p style="margin:0 0 8px;font-size:13px;line-height:1.7;color:#555555;font-weight:600;font-family:FF;">关于本号</p>
  <p style="margin:0;font-size:12px;line-height:1.8;color:#888888;font-family:FF;">这里放一句很轻的介绍，不抢正文，不硬广。</p>
</section>
```

## 5. 检查门禁

- 图片注释 / 来源 / 参考资料字号大于正文：fail。
- 引流文案使用正文大段样式：warning。
- 引用块使用主强调色大卡片且非核心金句：warning。
- 辅助信息使用多个强调色：warning。
