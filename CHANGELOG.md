# CHANGELOG

## v0.5.2｜Heading Fidelity Runtime Guard｜标题保真运行时修复

- 修复纯文本 `01` + 下一行标题、同一行 `01 标题` 与 HTML `<br>` 传输下的标题识别。
- 删除无原文标题时的自动小标题提炼；正文重点句、绿色短语和关键词不再有机会被提升为章节标题。
- 标题门禁升级为数量、原文、顺序完全一致，并新增 `generated_headings` P0 检查。
- 行动语义改为“明确指令 + 动作动词”联合判断；“可以传播 / 可以识别 / 开始害怕 / 开始健身”等描述句不再机械标绿。
- DraftBox 载荷新增 `runtime_manifest`，记录 Skill ID、实际版本、入口、编译器与门禁执行状态。
- 新增“为什么网络让世界越来越负面”回归样例，锁定 5 个原始章节标题与典型误判短语。
- 72 个视觉标识、微信安全渲染、纯排版边界和配图策略保持不变。

## v0.5.1｜Content-Aware Article Visuals｜公众号排版-文章视觉

- 不减少标识，不设置单篇固定标识种类上限；标识数量由文章内容与信息密度决定。
- 语义角色扩展为知识、数据、行动、风险、注意、洞察和旧认知，整句判断优先于局部关键词。
- 修复“可以增加 / 可以帮助”等知识解释被机械标成绿色行动的问题。
- 新增内容自动组件选择器：定义、事实、案例、警告、重要判断等原文可自动进入不同视觉组件。
- 自动语义颜色不再只选最多三种角色；凡原文具备明确阅读功能即可自动标识。
- 新增组件类型与语义角色使用报告，便于审核视觉丰富度与自动识别覆盖。
- 保持纯排版边界：生成文案、生成标签和改写段落继续为 0。

## v0.5.0｜Editorial Marker Library｜全量文章视觉标识库

- 新增 72 个可执行文章标识，覆盖行内强调、标题、色块与 Callout、引用、列表流程、数据媒体和元信息。
- 新增 `editorial-marker-registry.json`，每个标识包含启用级别、原文策略、微信支持、密度组、渲染器和测试样例。
- 新增完整微信安全渲染器与原文前缀触发器；定义、事实、案例、提示、警告、作者、日期、阅读时间和来源可在原文明确存在时自动转换。
- 新增全标识展示页和 72/72 渲染回归，禁止只写文档不实现代码。
- 保持纯排版边界：所有正文文字逐字来自原文，生成文案、生成标签和改写段落继续为 0。
- 互动组件统一静态降级，禁止 Script、Flex、Grid、动画和 Sticky 进入微信正文。

## v0.4.4｜Schema Validation Hotfix｜Schema 枚举与独立降级校验修复版

> 版本规范：固定使用 `vX.Y.Z` 三段式；本次热修复直接升级为 v0.4.4。

- 修复 `schema/component_tree.schema.json` 遗漏 `outlined_text_box` 类型导致真实 JSON Schema 校验失败的问题。
- 将无 `jsonschema` 环境的降级验证从仅检查顶层 required，升级为递归校验 type、enum、required、properties、additionalProperties、items、长度、pattern、not 和本地 `$ref`。
- 新增渲染器实际输出组件类型与 Schema enum 的静态一致性门禁。
- 新增非法组件类型拒绝自测，防止降级校验再次产生假 PASS。
- 功能与视觉规则保持 v0.4.3 不变：大序号标题、无标题左竖线、原文填充色块与矩形原文框。

## v0.4.3｜Numbered Headings & Text Boxes｜大序号标题与矩形原文框增强版

- 一级大标题改为醒目的 `01 / 02 / 03` 大序号，序号与标题绑定在同一模块，删除标题左竖线。
- 新增矩形原文框：白底、完整描边、顶部色条和小圆角，框内只显示原文完整句子。
- 矩形框禁止新增标题、标签或图标文字；短文最多 1 个，中长文最多 2 个。
- 修复复合句语义优先级：“可以”不再覆盖“但 / 而 / 真正 / 本质 / 关键”等整句判断语义。
- 新增大序号存在、标题无左竖线、矩形框文字逐字来自原文和密度上限门禁。

## v0.4.2｜Source-Text Visual Markers｜原文色块与无文字视觉标识增强版

- 在纯排版边界内恢复原文重点色块：色块只承载原文完整句子，不增加标题、标签或图标文字。
- 短文最多 1 个色块，中长文最多 2 个；色块在原位置替换普通段落，不复制、不移动原句。
- 按语义自动选择浅蓝、浅绿、浅橙、浅红、浅紫或浅灰背景与左侧竖线。
- 保留小标题左竖线、章节短横线、CSS 圆点、局部边框、圆角底纹、引用竖线、原文数字与关键词强调。
- 新增色块文字非空、逐字回溯原文、标签为空、图标为空和密度上限门禁。
- 继续保持 `generated_copy = 0`、`generated_labels = 0`、`rewritten_paragraphs = 0`。

## v0.4.1｜Pure Layout Fidelity｜纯排版与文案零改动修复版

- Skill 身份统一为 `xingchen/wechat-editorial-skill`，目录名与调用名恢复为 `wechat-editorial-skill`。
- 定位锁定为纯排版工具：语义分析只选择样式，不生成、改写、总结、提炼、扩写、删减或重组文案。
- 删除自动注入的“核心判断、行动建议、注意事项、最后总结、阅读重点”等标签。
- 默认关闭自动结论卡片、渐变重点条、双栏重组、编辑批注、导航和新增章节编号。
- 标题只保留原文字样；列表使用无文字 CSS 圆点；表格不增加“对比重点”或正误标签。
- 新增 `generated_copy`、`generated_labels`、`rewritten_paragraphs` 发布门禁，任何新增文案立即 Release FAIL。
- 重做视觉评分：不再强制开头结论卡片或组件数量，卡片密度过高反而扣分。
- 修复 Python 缓存自污染；无 `jsonschema` 时启用内置 required/type 校验，不再静默跳过。

## v0.4.0｜Semantic Editorial System｜语义编辑标记系统全面修复版

- 修复 `SKILL.md` YAML frontmatter 和 `agents/openai.yaml`，可被 ChatGPT 正确识别与调用。
- 新增 `scripts/build_article.py`，一次生成 `.wechat.html` 与 `.wechat.json`。
- 内容保真升级为覆盖率、顺序、原始小标题、成对标点、模板注入和新增内容六重门禁。
- 修复小标题前导语遗漏、多个 CTA 丢失、普通“课程/关注/项目地址”误判 CTA、引用右引号漂移和乱码。
- 新增十四类语义标记与自动预算：下划线、删除线、色块、高亮、竖线引用、胶囊标签、小图标、双栏对比、渐变重点条、批注、数据强调、分隔线、绑定编号和文章级颜色规划。
- 四套主题通过 `templates/theme-profiles.json` 接入真实渲染，并支持 `--theme`。
- 验证拆为 quick、regression、release；release 动态编译全部 Markdown 示例，不依赖陈旧输出文件。
- 清理缓存、旧输出和 Unicode 替换字符。

## v0.3.6.1｜Content Fidelity Hotfix｜内容保真全面修复版

- 原文 Markdown 小标题不再被剥离，按原顺序进入章节结构。
- 禁止文章类型模板替换原文开头、小标题和总结。
- 移除“时间 / 地点”触发课程推广类型的误判。
- intro、summary、行动项必须来自原文；行动项只接受短而明确的可执行句。
- 新增 content_fidelity_report：检查标题保留、模板注入和新增内容。
- 内容保真失败在 release 模式下直接 FAIL。
- 语义强调色由文章级规划器限制为最多三种。
- 补齐橙色 attention 标记。
- 清理 README 与 SKILL 重复版本章节。

## v0.3.6｜Semantic Marker System｜语义化标记系统版

- 新增 `core/semantic_marker_system.md`，建立“标记即阅读语法”的统一规则。
- 新增灰色删除线、蓝色数据下划线、绿色行动高亮、红色风险下划线、紫色洞察下划线。
- 重点卡片按标签语义自动切换蓝 / 绿 / 红 / 紫色调。
- 每段最多 1 个行内标记；同一句禁止叠加；整篇默认最多 3 种语义强调色。
- sanitizer 新增安全的 `text-decoration` 白名单。
- Visual Rhythm Validator 新增 `semantic marker fatigue` 和未知强调色检查。
- 新增 `semantic_marker_article.md` 回归样例与 release 门禁。

## v0.3.5｜Smart Cover & Illustration Planner｜智能封面与配图规划版

- 新增 `smart_image_plan`：自动根据文章内容类型、情绪、场景和传播目标匹配图片风格。
- 新增内容视觉识别：AI/科技/商业、健康/生活方式、宇宙/硬核科普、个人成长、知识杂志等方向自动匹配不同视觉风格。
- 封面图默认规划 `2.35:1` 横版提示词，并强制加入中心 `1:1` 裁切安全规则。
- 正文配图默认规划 `3:4`，根据文章长度和章节结构自动决定 1-3 张，并给出插入位置。
- `draftbox_payload.cover_image_brief` 改为真实封面提示词对象，不再只是占位说明。
- `image_asset_list` 输出封面图 + 正文配图任务清单，包含 ratio、prompt、placement、visual_style、content_domain、quality_rules。
- 生图执行保持可选：默认先输出提示词、风格说明、插图位置和质检规则。
- 新增版权安全规则：新增背景重构法去水印 / 水印处理：仅限自有图片或本流程生成图片，允许通过背景重绘、边缘补全、局部重构清理模型水印、伪水印、平台生成痕迹和画面瑕疵；第三方版权水印、署名、Logo、平台标识不得自动移除，发现后默认重生成、替换素材或要求授权无水印版本。
- quick_validate 新增智能配图检查：封面比例、1:1 裁切安全、正文 3:4 配图规划、背景重构法去水印边界。
- 新增回归样例：`examples/visual_polish/smart_image_planning_article.md`。


## v0.3.4.1｜Natural Editorial Rhythm Hotfix｜自然编辑节奏修复版

- 整合本轮手机预览反馈：章节编号、重点句、核心判断卡片频率、正文重复标题四类问题统一修复。
- 取消“每个章节强制核心判断卡片”：整篇默认最多 1 个章节重点卡片，且不得连续出现同款蓝色卡片。
- “核心判断”不再作为每节固定标签；根据语义自动改为“反直觉点 / 关键提醒 / 研究发现 / 可以先做 / 这一节的重点”。
- 普通章节重点改为正文局部加粗或自然段首强调，不再强制上卡片。
- strict_draftbox 默认不再渲染 `title_block`：公众号标题只进入 `draftbox_payload.title`，正文不重复主标题。
- Visual Rhythm Validator 新增 `body title block rendered`、`repeated core judgment labels`、`too many key cards` 检查。
- quick_validate 新增重复正文标题门禁：发现正文首屏渲染 22px 标题块则 FAIL。
- 发布检查改为 `no duplicated body title`、`sparse natural highlights`、`section numbers bound to headings`。
- 新增回归样例：`examples/visual_polish/natural_rhythm_article.md`。


## v0.3.4｜Section Number & Highlight Upgrade｜章节编号与重点句增强版

- 修复章节编号 `01 / 02 / 03` 孤立显示的问题：编号必须和章节标题绑定成同一个视觉模块，不再像手机截图里的独立页码。
- 新增 `section_title_numbered` 渲染规则：教程、知识拆解、观点文等标题都会把编号纳入标题组件。
- 新增 `choose_section_key_sentence()`：每个章节自动提取 1 句核心判断，优先识别“真正 / 本质 / 关键 / 反直觉 / 不是……而是……”等判断句。
- `emphasis_sentence` 升级为核心判断卡片：浅蓝底、左侧主色线、圆角、短标签，形成每 1-2 屏一个视觉停顿。
- 新增 `emphasize_inline()`：正文段落只对少量关键词做温和加粗，避免整段加粗和高亮疲劳。
- Visual Rhythm Validator 新增 `detached section number` 与 `missing key sentence cards` 检查。
- 发布检查新增：章节编号必须绑定标题、核心判断卡片必须存在、移动端扫读必须有标题和重点句。
- 新增回归样例：`examples/visual_polish/section_highlight_article.md`。


## v0.3.3.2｜Bullet List Visual Hotfix｜列表空黑点修复版

- 修复“关键判断”卡片中每个列表项之间出现空黑点的问题。
- `normalize_input` 新增 `normalize_lonely_bullet_lines()`：独立的 `• / · / ● / - / *` 行会被视为列表标记，不作为正文段落输出。
- `checklist` 渲染改为“一行一个真实列表项”：`<span>•</span> + 文本` 在同一个 `<p>` 内，间距由 `margin-bottom` 控制。
- Visual Rhythm Validator 新增 `empty bullet paragraph` 与 `split bullet rows` 检查。
- 新增 `examples/visual_polish/bullet_spacing.md` 回归样例。

## v0.3.3.1｜WeChat Layout Research Polish｜公众号排版研究落地修复版

### v0.3.3.1 audit hotfix｜Full Example Coverage

- Fixed: dirty inline Markdown table input like `正文。| 项目 | A | B |` is split before table detection.
- Fixed: short table-heavy examples now keep at least two semantic visual road signs, avoiding `heading beauty missing`.
- Improved: `quick_validate.py --mode release` now also covers `examples/before_after/*.output.html`, `examples/demo_output.html`, and `examples/wechat_article_sample.html`.
- Verified: `raw_table_article.output.html` now reports `visual_score: 100`, `heading_beauty: pass`.
- Verified: `artifact_residue_scan: PASS`, `all_output_html_validation: PASS`, `style_probe: PASS`.


- Fixed: component_tree 不再包含 visual_plan；visual_plan 移到顶层 JSON。
- Fixed: RELEASE_REPORT 必须记录实际 quick_validate release 结果，禁止假 PASS。
- Added: references/wechat-layout-research-rules.md，把公众号排版技巧落为执行规则、组件规则、节奏规则、反模式、validator 检查项和文章类型骨架。
- Added: core/article_type_layout_recipes.md，并与 article_type_layout_templates.md 合并兼容。
- Improved: sanitizer 支持 padding-left/right/top/bottom、margin-left/right、border-top/bottom、display:inline-block，同时继续禁止 flex/grid/position/animation/transition/keyframes/hover/var()。
- Improved: 胶囊标签使用 span inline-block，左线标题保留 padding-left。
- Fixed: actions 只从原文提取，不再默认生成模板感 checklist。
- Added: content_deduplication_engine，避免 digest、intro、重点句和 summary 复用同一句。
- Improved: highlight fatigue 与颜色统计忽略结构性加粗、灰色、正文色和浅背景色。
- Improved: 复杂 Markdown 表格降级为对比卡 / 信息卡，不输出管道符残留。
- Improved: Markdown 图片转 image_block，紧跟图注绑定为 12px image_caption。
- Improved: Visual Rhythm Validator release 阈值提升到 visual_score >= 88。
