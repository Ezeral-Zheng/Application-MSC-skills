---
name: application-review
description: 当前 Application-MSC Vault 专用文书自动审查 skill。用于在推荐信、PS、简历生成或修改后自动审查事实、结构、版本、重复和文书类型规则，并把审查问题独立记录到 Review_Memory 与 Review_History。
---

# Application Review

## 使用场景

每次生成或修改推荐信、个人陈述、简历后自动使用本 skill。用户也可以单独要求审查某篇 `.md` 文书。
生成或修改 Resume-Experience 项目经历片段后也必须使用本 skill。

## 必读资料

1. 待审查 `.md` 成稿。
2. `Student_Profile/学生偏好总结.md`。
3. `Review_Memory/审查问题记忆.md`。
4. 与文书类型相关的资料源：
   - 推荐信：`Recommender_Info/*.md`、`Basic_Info/*.md`，必要时读 `Course_Info/*.md`。
   - PS：`Basic_Info/*.md`、`Personalization_Info/*.md`、`Personalization_Materials/*.md`、`Course_Info/*.md`、`Resume/*.md`、`Major Selected/*.xlsx`（如可读取）、`Student_Profile/PS_申请组合叙事矩阵.md`、同一学生其他申请目标的最新正式 PS，或用户本次明确提供的目标专业信息。
   - 简历：`Basic_Info/*.md`、`Course_Info/*.md`、`Resume/*.md`。
   - Resume-Experience：`Course_Info/*.md`，必要时读 `Basic_Info/*.md`。
   - 若上述资料中出现附件文件名，读取 `Additional_Documents/` 中匹配的同名 `.md`。
5. `references/全局审查规则.md`。

## 审查结果

审查报告必须给出一个状态：

- `Pass`：达到审查标准，可以交付。
- `Needs Fix`：有可自动修复的问题，应根据报告生成下一个内部 `Rn` 候选稿并复查；不得递增正式 `Vn`。
- `Blocked`：缺少关键事实或用户输入，继续自动写会导致编造，应停止并要求补充。

## 通用审查标准

- 正式交付文件只输出 `.md`，文件名包含正确版本号 `Vn`。正式发布前允许审查任务专用临时目录中的 `Rn` 候选稿；报告必须同时记录预留交付版本和内部轮次。
- 所有事实能在学生资料、推荐人资料、用户输入或本次上下文中找到依据。
- 使用附件内容的事实必须能追溯到 `Additional_Documents/*.md`；资料中提到但未落地的附件不得作为事实依据。
- PS 中的个人化动机、经历反思和职业偏好应能追溯到 `Personalization_Info/*.md`、`Personalization_Materials/*.md`、其他学生资料或用户本次明确输入。
- `Personalization_Materials/` 中标为“待确认”的内容不得被写成确定事实；标为“合理推断/表达方向”的内容不得扩写成未经证实的具体经历、数据、奖项或结果。
- 不伪造课程、成绩、项目、学校、专业、时间、奖项、数据。
- 不混用不同学生、不同推荐人、不同文书类型的素材。
- 无明显 reference 原文残留、模板句重复、占位符遗漏。
- 目标学校或项目未知时，使用通用表达，不编造项目匹配信息。
- PS 中涉及目标学校、专业、课程、项目特色或职业前景的信息，应能追溯到 `Major Selected/`、用户本次明确输入或其他可读项目资料；无法追溯时不得写成确定事实。
- 如果发现审查记忆中记录过的错误模式，必须重点检查。
- 修改稿正文段落之间不应有空行，段落开头不应有空格、缩进或中文全角空格；Markdown 标题、列表和表格的必要换行除外。

## 类型审查标准

推荐信：

- 保持推荐人第三方口吻，不写成学生自述。
- 可变段绑定当前推荐人的课程交集，不混用另一位推荐人的素材。
- 推荐人姓名、职位、院系、课程和观察范围必须与 `Recommender_Info` 一致；必要时按 `recommendation-letter-writer/references/推荐人身份一致性检查表.md` 逐项核对。
- 两封推荐信结构不同，核心例证不同，能力标签不过度重复。
- 推荐人自我介绍可以存在，但不能两封同等篇幅、同等句式重复。
- 固定段只保留功能，不能保留 reference 原句；可变段必须按学生资料重写。

个人陈述：

- 默认同一 `.md` 文件内输出双语版本：英文正文在前，中文正文在后。
- 英文和中文都应是连贯文章，不分点，不写成提纲。
- 英文正文建议 500-1000 words，理想约 700 words；明显低于或高于该范围时，检查是否内容不足、过度扩写或没有按申请要求控制篇幅。
- 中文版本应与英文版本事实一致，可自然改写，但不得新增英文版没有的事实。
- 应届生顺序为：本科专业选择原因、本科经历、职业规划、硕士专业/学校选择原因。
- 时间线正确，经历发生顺序合理。
- 不堆砌全部经历，只保留服务申请专业主线的素材。
- 如果个性化素材为空但 PS 仍出现大量具体个人动机或经历细节，必须核查是否来自其他资料；无法追溯时判为 `Needs Fix` 或 `Blocked`。
- 学生偏好总结只能作为风格和详略依据，不能作为新增事实依据；若偏好总结与个性化素材或基础资料冲突，要求修正或人工确认。
- 如果同一学生已有其他目标项目 PS，运行 `Application_System/tools/check_ps_portfolio_similarity.py`。工具结果是预警证据，不单独替代人工判断。
- 出现相同开头、相同前三段叙事、完整非事实句大量复用，或只有职业目标与 Why Program 不同时，判为 `Needs Fix`，问题类型使用 `Cross-Application Similarity`。
- 修复跨申请重复时必须回到 `PS_申请组合叙事矩阵.md` 重构核心问题、素材排序或经历功能；仅替换同义词、学校名、专业名和课程名不能通过。

简历：

- 结构清晰，信息密度高，不过度扩写。
- bullet 动词驱动，经历排序服务目标专业。
- 不虚构量化结果、奖项、工具、职责或成果。
- 不写成长段 PS。

Resume-Experience：

- 每条正文项目必须能追溯到 `Course_Info` 或用户本次明确补充的信息。
- 不虚构课程、项目、时间、角色、工具、模型、数据、指标、成果、奖项或软件著作权。
- 不混入其他学生、完整简历、推荐信、PS 或参考格式文档中的事实素材。
- 信息不完整项目不得被强行写入正文；应放入 `未纳入项目` 并说明缺失原因。
- 格式应符合参考经历格式：项目名加粗、竖线后写项目类型、可选角色行、可选时间行、随后是 bullet 列表。
- 每个项目建议 2-4 条 bullet；bullet 应为英文简历语言，以动作动词开头，不写成 PS 段落。
- 若缺少时间或角色，允许省略对应行；不允许为了填满格式而写无依据的 `[待补充]` 或虚构内容。
- `资料依据` 必须列出读取过的 `Course_Info` 文件路径，便于后续核查。

## 自动修稿流程

1. 任务开始时扫描正式输出目录，只预留一个下一个交付版本 `Vn`。
2. 将初稿或修改稿保存为任务专用临时目录中的 `R1` 候选稿，不写入正式输出目录。
3. 审查当前 `Rn`；内部审查报告保存在同一任务临时目录，不写入学生的 `Review_History/`。
4. 若状态为 `Pass`，停止当前事实修订循环。
5. 若状态为 `Needs Fix`，根据审查报告生成下一个内部轮次 `R(n+1)`，正式交付版本号保持不变，并再次审查。
6. 若状态为 `Blocked`，停止自动修稿，报告需要补充的事实。
7. 自动修稿最多新增 3 个内部轮次；仍未通过时，不发布预留的正式 `Vn`，并在报告中列出剩余问题。
8. 本审查为 `Pass` 后，主控 Agent 再按 `external-application-review` 启动上下文隔离 Subagent 做单篇内容审稿；PS 已有其他申请目标时，还需执行 `portfolio-differentiation` 隔离审稿。本 skill 不代替独立审稿。
9. 独立内容审稿和必要的内部修订全部完成后，才把最后通过的候选稿一次性保存为预留的正式 `Vn`。随后对正式文件做最终一致性确认，并只把这份正式审查报告写入 `Review_History/YYYY-MM-DD-文书类型-Vn-审查报告.md`。

## 审查报告结构

每份审查报告至少包含：

- 顶部 frontmatter，字段固定为 `student`、`doc_type`、`draft_path`、`version`、`status`、`severity`、`issue_types`、`evidence_path`、`fix_action`、`memory_update`、`review_time`
- 学生
- 文书类型
- 审查稿件路径
- 审查版本
- 预留正式交付版本和内部修订轮次（审查内部候选稿时）
- 审查时间
- 审查状态：`Pass` / `Needs Fix` / `Blocked`
- 事实依据检查
- 类型规则检查
- 版本与输出格式检查
- 重复性或模板痕迹检查
- 需要修复的问题
- 自动修稿建议
- 是否写入审查记忆

frontmatter 示例：

```md
---
student: 周星彤
doc_type: Recommendation-Letter
draft_path: 周星彤/Recommendation_Letters/2026-06-07-周星彤-Liu-Yue-Recommendation-Letter-V1.md
version: V1
status: Pass
severity: Low
issue_types: []
evidence_path: 周星彤/Recommender_Info/xxx.md
fix_action: None
memory_update: false
review_time: 2026-07-17 12:00:00
---
```

`status` 只能使用 `Pass`、`Needs Fix` 或 `Blocked`。`issue_types` 建议从以下类型中选择：`Fact`、`Format`、`Version`、`Reference Residue`、`Material Mixing`、`Structure`、`Cross-Application Similarity`、`Missing Input`、`Tool Failure`、`Style`。

如果审查稿件仍包含 `[待补充：...]`、`[待确认：...]` 或类似占位符，审查状态不能为 `Pass`；应为 `Needs Fix` 或 `Blocked`。

## 审查记忆更新

审查问题写入 `Review_Memory/审查问题记忆.md`，不写入 `Student_Profile/学生偏好总结.md`，除非该结论明确属于学生个人风格偏好。

写入审查记忆的问题包括：

- 事实错误或资料来源缺失。
- 推荐人素材混用。
- 版本命名或输出格式错误。
- reference 原文残留。
- 两封推荐信重复度高。
- PS 分点、顺序错误或时间线错乱。
- PS 与同一学生其他申请目标高度雷同，或只替换职业目标与 Why Program。
- PS 把个性化素材补写候选或待确认内容误当作已确认事实。
- 简历虚构量化或过度扩写。
- Resume-Experience 收录信息不足项目、格式错误、或把无依据事实写成项目 bullet。

跨学生反复出现的问题，应沉淀到 `references/全局审查规则.md`。
