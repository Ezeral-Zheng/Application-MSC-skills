---
name: resume-experience-writer
description: 当前 Application-MSC Vault 专用 Resume-Experience 整理 skill。将学生 Course_Info 中已有课程项目全量转化为独立英文 Markdown 项目经历片段，并在生成后触发 application-review 的 Resume-Experience 审查。
---

# Resume Experience Writer

## 使用场景

当用户要求整理 `Course_Info` 项目、生成 Resume-Experience、课程项目经历、项目经历片段，或把课程项目改写为英文简历经历时使用本 skill。

本 skill 只产出独立项目经历片段，不直接改写完整简历；完整简历生成仍使用 `resume-writer`，但可以读取本 skill 的输出作为项目经历来源。

## 必读资料

1. `Student_Profile/学生偏好总结.md`
2. `Student_Profile/资料完整性检查.md`
3. `Course_Info/*.md`
4. 必要时读取 `Basic_Info/*.md`，用于确认学生姓名、学校、专业或课程背景
5. 用户提供的目标专业、用途或额外限制

## 参考资料

- 写作前读取 `Application_System/skills/resume-writer/references/resume-experience-format.md`。
- 写作 bullet 时可读取 `Application_System/skills/resume-writer/references/action-verbs-and-bullets.md`。
- 生成后用 `Application_System/skills/resume-writer/references/resume-review-checklist.md` 做自检。

## 转化范围

- 本步骤是 Course_Info 到 Resume-Experience 的资料转化，不按目标专业、申请方向、含金量或“是否适合简历”做择优筛选。
- 默认将 `Course_Info` 中能提取到有效内容的项目全部转化为英文项目经历；有多少可转化项目就生成多少项目条目。
- “可转化”至少应包含：
  - 项目名称或课程项目主题
  - 项目类型、课程名或可判断为课程项目的来源
  - 学生承担的具体任务、方法或行动
  - 可写入 bullet 的过程、工具、分析方法、问题解决或结果信息
- 若缺少时间或角色，但其他项目内容充分，可以保留项目；时间或角色必须使用资料中已有表达，不能编造。
- 只有标题、空模板字段、明确标注“还没做”、泛泛一句话或无法判断学生具体贡献的项目，放入文末 `## 未纳入项目`，说明缺失原因。
- 不收录 `Course_Info` 之外无法追溯的项目，除非用户在本次对话中明确补充。

## 写作格式

默认英文输出，保存为 `.md`。

课程项目为主时使用：

```md
## Project Experience
```

若资料明确是科研、论文、实验室或软件著作权等研究类项目，可使用：

```md
## Research Experience
```

单个项目使用以下格式：

```md
**Project Name** | *Course Project / Research Project / Competition Project*
*Role*
Date - Date

- Action-driven bullet...
- Action-driven bullet...
```

格式要求：

- 项目名使用 `**...**` 加粗。
- 项目类型放在竖线后，优先写 `*Course Project*`、`*Research Project*`、`*Competition Project*` 或资料中明确的项目性质。
- 角色行仅在资料中有依据时填写，例如 `*Team Leader*`、`*Team Member*`、`*Individual Project*`；没有依据则省略角色行，不编造。
- 时间行仅在资料中有依据时填写；没有依据则省略时间行，不写 `[待补充]`。
- 每个项目写 2-4 条 bullet。
- bullet 应以英文动作动词开头，体现任务、方法、工具、分析过程、问题解决或结果。
- 有数字、工具、模型、数据集、课程名称或成果时，只有在资料中明确出现才可写入。

## 写作规则

- 保留每个可转化项目中已有的技术、分析、商业、工程、研究或实践能力；不因目标专业相关性而删减整个项目。
- 不把所有原文信息机械搬运进 bullet；选择能体现能力和结果的内容。
- 不虚构量化结果、工具、模型、数据规模、奖项、角色、课程名称、时间或项目产出。
- 如果原始资料是中文，允许翻译和压缩为英文简历语言，但事实边界必须保持不变。
- 不写成长段叙事，不写成个人陈述，不解释申请动机。
- 不使用参考简历中的具体公司、项目、学校、成果或措辞作为当前学生事实。

## 输出

保存到目标学生目录：

```text
Resume_Experience/
```

文件名必须带版本号 `Vn`。生成前扫描 `Resume_Experience/` 中同一 key 的最高版本，取最高版本加 1。
该 `Vn` 是本次任务唯一预留的正式交付版本。内部生成与审查只使用临时 `R1`、`R2` 等候选稿；全部审查通过后才发布该 `Vn`。

版本 key：

```text
学生名-Resume-Experience
```

推荐使用工具生成路径：

```bash
python3 Application_System/tools/next_version_path.py \
  --dir '<学生名>/Resume_Experience' \
  --key '<学生名>-Resume-Experience'
```

推荐文件名示例：

```text
YYYY-MM-DD-学生名-Resume-Experience-V1.md
```

## 输出结构

成稿至少包含：

- 标题：`# 学生名 Resume Experience Vn`
- 项目经历正文：`## Project Experience` 或 `## Research Experience`
- `## 未纳入项目`：列出未写入正文的项目名称和缺失原因；如果无未纳入项目，写 `- 无`
- `## 资料依据`：列出读取过的 `Course_Info` 文件路径，便于审查追溯

## 生成后审查

生成后必须调用 `application-review`，文书类型标记为 `Resume-Experience`。
`application-review` 为 `Pass` 后，由隔离 Subagent 调用 `external-application-review`；如需修改，由主控 Agent 生成下一个内部 `Rn` 并再次调用 `application-review`，正式 `Vn` 不变。

审查为：

- `Pass`：停止。
- `Needs Fix`：根据审查报告生成下一个内部 `Rn` 并复查；不得递增正式 `Vn`。
- `Blocked`：停止，不继续编造，并列出需要用户补充的资料。

自动修稿最多新增 3 个内部轮次；最终只发布一个正式版本。

## 阻塞条件

- `Course_Info/` 为空或只有模板字段。
- 所有项目都缺少学生具体行动、方法、工具、过程或结果信息。
- 用户要求写入无法追溯到 `Course_Info` 或本次明确补充的信息。
- 资料中项目名称、时间、角色或来源互相冲突，无法判断真伪。

## 最小输出

- `Resume_Experience/` 下唯一的新正式版本 `.md`；内部候选稿不得进入该目录。
- 正文项目经历，或在无可转化项目时列出 `未纳入项目` 和缺失原因。
- `## 资料依据`，列出读取过的 `Course_Info` 文件路径。
- 对应 `Review_History/` 审查报告。
- 必要时更新 `Student_Profile/Task_Board.md`。
