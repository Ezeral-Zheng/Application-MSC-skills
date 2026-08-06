---
name: resume-writer
description: 当前 Application-MSC Vault 专用简历写作 skill。先将经历整理为 Resume-Experience，再按目标专业筛选和编排完整简历；Markdown 是正式内容源，DOCX 仅作为可选模板化导出和视觉 QA 产物。
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
- 完整简历生成前，先读取已通过审查的 `Resume_Experience/`；若没有合适片段，先调用 `resume-experience-writer` 整理经历。
- 根据目标专业的课程、能力要求、研究/职业方向建立筛选依据，明确保留、弱化和舍弃的经历；不得只按时间顺序机械罗列。
- 先完成专业版 Markdown 内容，再进入模板化 DOCX 导出；不要在 Word 排版阶段反向改写事实或新增内容。
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

### 可选版式导出

当用户提供 Word 参考格式或明确要求 Word 排版时，完成 Markdown 正式稿后再执行：

1. 使用 `Application_System/references/resume-docx-template-workflow.md` 中的模板规则，将 Markdown 映射为模板化 DOCX。
2. DOCX 只作为展示/投递格式，不替代 `Resume/` 下的正式 Markdown，也不进入正式版本索引。
3. 使用文档 skill 的 `render_docx.py` 渲染 PNG，逐页检查字体替换、日期对齐、横线、表格边界、分页和空白页。
4. 若版式不合格，只修改导出层；内容事实变化必须回到 Markdown 候选稿并重新审查。
5. 导出临时文件和渲染图片放在任务专用 `mktemp -d` 目录；用户明确要求时才复制最终 DOCX 到指定位置。

命名规则：

- 文件名必须带版本号 `Vn`。
- 文件名不得添加日期前缀。
- 生成前扫描 `Resume/` 中同一学生、同一目标专业/用途的历史简历，取最高版本加 1。
- 可用 `Application_System/tools/next_version_path.py` 生成路径。
- 该 `Vn` 是本次任务唯一预留的正式交付版本。内部写作与审查只使用临时 `R1`、`R2` 等候选稿；全部审查通过后才发布该 `Vn`。

示例：

`学生名-目标专业或用途-Resume-V1.md`

## 阻塞条件

- 缺少基础身份、教育背景或目标用途，无法确定简历结构。
- 经历资料只有标题，没有职责、行动、工具、方法或结果依据。
- 用户要求写入无法核实的量化结果、奖项、岗位或项目成果。
- 目标项目要求特定格式，但未提供格式要求或参考文件。

## 最小输出

- `Resume/` 下唯一的新正式版本 `.md`；内部候选稿不得进入该目录。
- 调用 `application-review`，生成对应 `Review_History/` 审查报告。
- `application-review` 为 `Pass` 后，由隔离 Subagent 调用 `external-application-review`；如需修改，由主控 Agent 制作净化交接包，再由另一个全新且不继承审稿或写作上下文的修改 Subagent 生成下一个内部 `Rn`，并再次调用 `application-review`，正式 `Vn` 不变。
- 必要时更新 `Student_Profile/Task_Board.md`。
- 若引用 Resume-Experience，优先使用已通过审查的版本。
- 用户要求模板化 Word 时，额外完成一次 DOCX 渲染 QA；最终仍以 Markdown 作为正式内容交付。
