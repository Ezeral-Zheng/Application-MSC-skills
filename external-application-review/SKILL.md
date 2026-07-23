---
name: external-application-review
description: Use when a recommendation letter, personal statement, resume, or Resume-Experience draft has passed factual compliance review and needs an independent, context-isolated assessment of structure, content, logic, specificity, persuasion, reader impact, or AI/template feel before final delivery.
---

# External Application Review

## 核心原则

以第一次看到成稿的外部读者身份审稿。审稿人与写作者必须上下文隔离；只提交意见，不直接修改正文。目标是发现有实质收益的问题，不是证明文章永远还能润色。

## 强制隔离

主控 Agent 必须启动一个全新 Subagent，并且不继承当前对话或写作上下文（例如使用 `fork_turns: "none"`）。只传入：

1. 本 skill 路径与待审成稿路径。
2. 文书类型、目标项目或用途。
3. 用户明确给出的字数、题目或项目要求。
4. 可选的最小事实摘要；只有判断内容覆盖度确有必要时才提供。

不得传入写作过程、作者解释、旧稿、既有审查结论、主 Agent 的评价或预期答案。Subagent 不得读取其他学生目录、`Review_History/`、`Revision_History/`、`Review_Memory/` 或写作 skill。

调用提示必须明确写明“你是已隔离的最终审稿人”。收到这一标记的 Subagent 直接执行本 skill，禁止再次派生审稿 Subagent。只有仍处于原写作上下文的主控 Agent 才负责启动隔离 Subagent。

如果平台无法创建隔离 Subagent，停止并报告 `Blocked`；不得由原写作者假装独立审稿。

## 审查边界

- 审查结构、内容取舍、逻辑、个性化、说服力、目标适配、读者记忆点、重复和模板/AI 痕迹。
- 不重复承担 `application-review` 的完整事实核查、版本检查和素材溯源。
- 可以标记“疑似需要核实”，但没有资料时不得断言事实错误。
- 不得要求补写资料中未提供的新经历、数字、课程、领导行为、冲突、成果或项目细节。
- 如果某项改善依赖新事实，标为 `Needs Confirmation`，而不是 `Must Fix`。
- 不因纯个人措辞偏好判定必须修改。

审查前读取 [独立内容审稿规则.md](references/独立内容审稿规则.md)。审查 Personal Statement / SOP 时还必须完整读取 [个人陈述五维质量标准.md](references/个人陈述五维质量标准.md)，并按五个维度逐项输出结论。

## 执行流程

1. 只读成稿和允许提供的最小任务信息。
2. 先完成无背景的读者盲审：主线、记忆点、最强段、最弱段、阅读阻力。
3. 再完成目标适配审查：素材是否支持申请方向，目标与项目是否形成因果关系。
4. 对每条建议标注优先级、定位、影响、修改方向和事实边界。
5. 明确列出 `Do Not Change`，保护有效内容。
6. 按下方“审稿人与主 Agent 交接协议”输出报告，不修改成稿、不创建新的正式版本。

## 优先级与状态

| 标签 | 用法 |
|---|---|
| `Must Fix` | 有明确文本证据的结构断裂、核心论证缺失、严重重复或自相矛盾 |
| `Should Fix` | 修改有清晰收益，且能用现有文本安全完成 |
| `Optional` | 合理但主观的风格选择，不应触发自动改稿 |
| `Needs Confirmation` | 需要新增或确认事实；不得自动写入正文 |
| `Do Not Change` | 已有效且应在修稿中保留的内容 |

报告状态只能是：

- `Pass`：无 `Must Fix`，且 `Should Fix` 不足以值得生成新版本。
- `Revise`：至少一项可用现有内容安全处理的实质问题。
- `Blocked`：无法获得隔离环境、无法读取成稿，或所有关键改善都依赖待确认信息。

## 报告格式

保存到 `External_Review_History/YYYY-MM-DD-文书类型-Vn-独立内容审稿.md`。报告可以在 frontmatter 中记录实际审查的内部轮次，但文件名只使用本次预留的正式 `Vn`，不得因内部轮次生成多个正式版本号。frontmatter 至少包含：

```yaml
---
student: 学生名
doc_type: Personal-Statement
draft_path: 相对路径
version: V1
internal_iteration: R1
status: Pass
review_mode: isolated-subagent
must_fix_count: 0
should_fix_count: 0
needs_confirmation_count: 0
review_time: YYYY-MM-DD HH:MM:SS
---
```

Personal Statement 报告正文依次写：一句话结论、五维审查摘要、问题清单、`Do Not Change`、给主 Agent 的修改交接单。其他文书类型保留读者盲审和目标适配结构。禁止只写“更深入”“更具体”“增强个性化”等不可执行意见。

在“五维审查摘要”之后必须追加课程堆砌检查；即使最终判断为 `Pass` 也不得省略：

```md
## 课程堆砌检查

- 具名课程数量：3
- 是否连续罗列：否
- 是否逐项连接经历与能力缺口：是
- 课程内容占 Why Program 的比例：适中
- 判断：Pass
- 关联问题 ID：—
```

如果出现 4 门及以上具名课程、连续课程名列表、课程内容占据 Why Program 主要篇幅，或课程未连接具体经历与能力缺口，按 `个人陈述五维质量标准.md` 生成 `PS-FIT` 问题。该项未修复时报告状态不得为 `Pass`。

## 审稿人与主 Agent 交接协议

Personal Statement 的每个问题都必须使用稳定 ID：

- 英文语言质量：`PS-LANG-001`
- 结构与逻辑主线：`PS-STRUCT-001`
- 素材、细节与反思：`PS-EVID-001`
- 专业与项目匹配：`PS-FIT-001`
- 个人辨识度与说服力：`PS-VOICE-001`

同一报告内按出现顺序递增末尾数字，不得重复。先输出维度摘要：

```md
## 五维审查摘要

| 维度 | 结论 | 关联问题 ID | 一句话判断 |
|---|---|---|---|
| 英文语言质量 | Pass | — | 英文准确自然，无影响交付的问题 |
| 结构与逻辑主线 | Needs Fix | PS-STRUCT-001 | 第三段打断主线 |
| 素材、细节与反思深度 | Pass | — | 核心经历有行动与反思 |
| 专业与项目匹配度 | Needs Fix | PS-FIT-001 | 课程罗列替代能力缺口论证 |
| 个人辨识度与申请说服力 | Needs Confirmation | PS-VOICE-001 | 职业聚焦需要学生确认 |
```

随后每个问题严格使用以下字段，不得省略：

```md
### PS-FIT-001｜课程罗列削弱项目匹配逻辑

- 维度：专业与项目匹配度
- 优先级：Should Fix
- 原文定位：英文第 7 段 / 中文对应段
- 问题内容：连续列出多门课程，但没有说明各自回应的能力缺口。
- 原文证据：引用最短必要片段，或在无法安全引用时准确概述。
- 对读者的影响：读者能看出项目相关，却不知道它为何是申请人的必要下一步。
- 修改动作：保留 2–3 项资源，分别连接既有经历、能力缺口和未来用途。
- 事实边界：只使用正文已有课程和经历；不得新增项目特色或学生经历。
- 必须保留：保留申请人已经建立的核心专业动机。
- 是否需要确认：否
- 验收标准：Why Program 中每项保留资源都完成“经历—缺口—资源—用途”的连接，且不再出现课程清单。
```

最后输出给主 Agent 的唯一执行入口：

```md
## 给主 Agent 的修改交接单

| 执行顺序 | 问题 ID | 建议处置 | 可否自动修改 | 依赖信息 | 验收标准摘要 |
|---|---|---|---|---|---|
| 1 | PS-FIT-001 | 采纳 | 是 | 无 | 课程按能力缺口组织 |
| 2 | PS-VOICE-001 | 待确认 | 否 | 学生首选职业方向 | 未确认前不补写 |
```

“可否自动修改”只能填 `是` 或 `否`：`Must Fix` 和可安全处理的 `Should Fix` 可填 `是`；`Optional` 默认填 `否`；`Needs Confirmation` 必须填 `否`。

## 返回主控 Agent

主控 Agent 必须先制作“建议—采纳决策表”，再调用 `application-revision`：

- 自动处理 `Must Fix` 和被采纳的 `Should Fix`。
- `Optional` 默认不触发新版本。
- `Needs Confirmation` 只进入待确认项，未经用户确认不得写入正文。
- 修改后生成下一个内部 `Rn` 候选稿，预留的正式 `Vn` 不变，再调用 `application-review` 做事实与合规兜底。
- 独立内容审稿默认只运行一轮；只有结构被整体重写、用户补充了被阻塞的信息或用户明确要求时才进行第二轮。
- 修改时按交接单顺序处理，并以每条问题的“验收标准”逐项复核；不得只根据问题标题自由发挥。

## 常见错误

- 让原写作者直接执行本 skill：不具备独立性，应启动隔离 Subagent。
- 已隔离的最终审稿人再次派生 Subagent：造成递归和职责漂移；看到“已隔离的最终审稿人”标记后必须直接审稿。
- 把所有建议都列为必须修改：会造成无止境修稿和风格磨平。
- 用常识补全领导力、动机或职业细节：应标记 `Needs Confirmation`。
- 直接改稿：审稿人只报告，主控 Agent 决定是否采纳。
- 读取完整资料库：会污染盲审；事实兜底仍由 `application-review` 完成。
