---
name: resume-writer
description: 当前 Application-MSC Vault 专用简历写作 skill。根据 Course_Info、Resume、Basic_Info、参考格式和学生偏好总结撰写英文简历，并只输出 Markdown 版本。
---

# Resume Writer

## 使用场景

当用户要求生成、整理、改写英文简历或 CV 时使用。

## 必读资料

1. `Student_Profile/学生偏好总结.md`
2. `Basic_Info/*.md`
3. `Resume/*.md`
4. `Course_Info/*.md`
5. 用户提供的目标专业或简历参考格式

## 参考资料

- 本 skill 的参考文档放在 `Application_System/skills/resume-writer/references/`。
- 可放简历模板、目标专业简历样例、bullet 表达库、ATS 格式要求、学校或项目的 CV 要求等。
- 写作前如参考目录中有与当前目标专业、用途、格式或语言风格相关的文件，应优先读取相关文件；不要无差别读取全部参考资料。
- 默认优先读取：
  - `action-verbs-and-bullets.md`：英文 bullet 动词和句式规则。
  - `resume-review-checklist.md`：事实、格式和虚构风险检查。
- 如果任务涉及 Course_Info 项目经历或 Resume-Experience，还应读取 `resume-experience-format.md`。

## 写作规则

- 使用英文简历格式，信息密度高，避免长段落。
- 经历 bullet 以动作动词开头，尽量体现任务、方法、结果。
- 有数字、成绩、排名、工具、项目成果时优先保留。
- 不虚构量化结果；缺失时用 `[待补充：...]` 标记。
- 根据目标专业调整项目和经历排序。
- 完整简历可以读取 `Resume_Experience/` 中已通过审查的 Resume-Experience 项目经历片段；如果没有通过审查的片段，应回到 `Course_Info` 核查。

## 推荐结构

- Education
- Research / Academic Projects
- Internship / Work Experience
- Leadership / Activities
- Skills
- Honors / Awards

## 输出

保存到 `Resume/`：

- `.md` 成稿

命名规则：

- 文件名必须带版本号 `Vn`。
- 生成前扫描 `Resume/` 中同一学生、同一目标专业/用途的历史简历，取最高版本加 1。
- 可用 `Application_System/tools/next_version_path.py` 生成路径。
- 该 `Vn` 是本次任务唯一预留的正式交付版本。内部写作与审查只使用临时 `R1`、`R2` 等候选稿；全部审查通过后才发布该 `Vn`。

示例：

`YYYY-MM-DD-学生名-Resume-V1.md`

## 阻塞条件

- 缺少基础身份、教育背景或目标用途，无法确定简历结构。
- 经历资料只有标题，没有职责、行动、工具、方法或结果依据。
- 用户要求写入无法核实的量化结果、奖项、岗位或项目成果。
- 目标项目要求特定格式，但未提供格式要求或参考文件。

## 最小输出

- `Resume/` 下唯一的新正式版本 `.md`；内部候选稿不得进入该目录。
- 调用 `application-review`，生成对应 `Review_History/` 审查报告。
- `application-review` 为 `Pass` 后，由隔离 Subagent 调用 `external-application-review`；如需修改，由主控 Agent 生成下一个内部 `Rn` 并再次调用 `application-review`，正式 `Vn` 不变。
- 必要时更新 `Student_Profile/Task_Board.md`。
- 若引用 Resume-Experience，优先使用已通过审查的版本。
