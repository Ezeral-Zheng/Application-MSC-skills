---
name: recommendation-letter-writer
description: 当前 Application-MSC Vault 专用推荐信写作 skill。根据 Recommender_Info、Course_Info、Basic_Info、Resume 和学生偏好总结撰写英文推荐信，并只输出 Markdown 版本。
---

# Recommendation Letter Writer

## 使用场景

当用户要求为某个学生写推荐信、推荐信初稿、推荐人视角材料时使用。

## 必读资料

1. `Student_Profile/学生偏好总结.md`
2. `Recommender_Info/*.md`
3. `Basic_Info/*.md`
4. 相关 `Course_Info/*.md`
5. 必要时参考 `Resume/*.md`
6. 如果 `Recommender_Info` 或课程素材中出现附件文件名，读取 `Additional_Documents/` 中匹配的同名 `.md`

## Reference 使用规则

- 本 skill 的参考文档放在 `Application_System/skills/recommendation-letter-writer/references/`。
- 写推荐信前必须读取当前两篇核心 reference：
  - Reference 1：`parallel-course-structure.md`
  - Reference 2：`course-project-structure.md`
- 写推荐信前还应按需读取以下规则库：
  - `固定段功能库.md`：拆解固定段功能，避免照抄 reference。
  - `课程推荐信能力标签库.md`：选择能力表达，但必须绑定事实依据。
  - `双信差异检查表.md`：同一学生两封信完成后的重复度和结构差异检查。
  - `推荐人身份一致性检查表.md`：检查推荐人身份、课程、观察范围和双信差异。
- Reference 只提供通用结构、段落功能和语气，不提供可直接套用的专业内容。
- 不要整篇照抄 reference。先拆出固定段和可变段：
  - 固定段：称呼、开头推荐语、必要推荐人身份、总体评价、结尾推荐语和签名；需要替换学生姓名、推荐人身份、申请专业，并改写句式。
  - 可变段：课程、课程作业、课堂表现、实验/报告、presentation、team project、沟通等事实；必须结合该学生和该推荐人的真实课程交集重写。
- 每个学生通常有两封推荐信：一封参考 Reference 1 的“并列课程型”结构，一封参考 Reference 2 的“深挖课程项目型”结构。
- 两封推荐信不能高度重复；必须在结构、开头、结尾、核心例证、能力重点和措辞上做区分。
- 推荐信默认按课程类推荐信处理；科研、研讨或实习素材只有在资料明确提供时才作为补充，不作为默认结构。
- 两封信都可以有推荐人身份介绍，但不要都写成长篇自我介绍；第二封通常应更快进入课程关系和学生表现。

## 写作规则

- 使用推荐人第三方视角，不使用学生第一人称。
- 优先使用推荐人与学生的真实课程交集：课程名称、课程成绩、课程重点、作业/实验/报告、课堂表现、presentation、team project、沟通频率。
- 如果交集材料薄弱，保持克制，用课程表现、学习能力、专业潜力补足，不虚构密切互动。
- 可变段必须从 `Recommender_Info` 中该推荐人的课程与交集信息出发，再用 `Course_Info`、`Resume`、`Basic_Info` 补足背景。
- 如果推荐人信息中提到课程作业、汇报、PDF、PPT、DOCX 等附件文件名，必须优先查找并读取 `Additional_Documents/同名.md`；只有该 Markdown 中有依据的细节才能写入推荐信。
- 不要把另一个推荐人的课程、项目或评价写进当前推荐信。
- 推荐信应包含：
  - 推荐人身份和与学生关系
  - 学生学术/专业表现
  - 具体课程、项目或能力例证
  - 个人品质或潜力评价
  - 与申请专业的匹配
  - 明确推荐结尾
- 缺失关键事实时用 `[待补充：...]` 标记。

## 双推荐信流程

当用户要求为同一学生生成两封推荐信时：

1. 解析 `Recommender_Info` 中的两个推荐人。
2. 分配两种通用结构：
   - 一封使用 Reference 1 的“并列课程型”结构，侧重课程学习、课堂表现和综合潜力。
   - 一封使用 Reference 2 的“深挖课程项目型”结构，侧重具体课程任务、项目/案例/竞赛和问题解决。
   - 如果两个推荐人的素材明显不同，把素材更简洁或更适合并列课程叙述的推荐人分给 Reference 1，把有更具体作业/项目/案例素材的推荐人分给 Reference 2；否则按推荐人顺序分配。
3. 为每封信分别列出内部素材槽位：
   - 固定段需要替换的信息：学生姓名、推荐人姓名、推荐人职位、学校、申请专业。
   - 可变段需要写入的信息：课程名称、成绩、课程重点、作业/实验/报告、presentation、team project、沟通场景、学生表现、与目标专业相关的学科能力。
   - 如果 reference 原文里有不属于当前课程事实的具体专业内容，删除并替换成学生真实课程内容。
4. 写完两封后做重复性检查：
   - 开头句不能相同。
   - 结尾段不能相同。
   - 核心例证不能完全相同。
   - 能力标签不能高度重叠。
   - 推荐人自我介绍不能同等篇幅、同等句式重复。
   - 两封信应体现不同推荐人的观察角度。
5. 使用 `双信差异检查表.md` 复核；如果资料不足以支撑两封差异化推荐信，标记为 `Blocked`，不要用空泛表达硬凑差异。

## 输出

保存到 `Recommendation_Letters/`：

- `.md` 成稿

命名规则：

- 文件名必须带版本号 `Vn`。
- 文件名不得添加日期前缀。
- 生成前扫描 `Recommendation_Letters/` 中同一学生、同一推荐人的历史推荐信，取最高版本加 1。
- 可用 `Application_System/tools/next_version_path.py` 生成路径。
- 该 `Vn` 是本次任务唯一预留的正式交付版本。内部写作与审查只使用临时 `R1`、`R2` 等候选稿；全部审查通过后才发布该 `Vn`。

示例：

`学生名-推荐人姓名-Recommendation-Letter-V1.md`

## 阻塞条件

- 无法确认推荐人姓名、身份或与学生关系。
- 推荐人课程交集缺失，且没有其他可观察事实支撑推荐信。
- 两封推荐信资料高度重叠，无法安全写出差异化版本。
- 资料中推荐人、课程或学生事实互相冲突，无法判断真伪。

## 最小输出

- `Recommendation_Letters/` 下唯一的新正式版本 `.md`；内部候选稿不得进入该目录。
- 调用 `application-review`，生成对应 `Review_History/` 审查报告。
- `application-review` 为 `Pass` 后，由隔离 Subagent 调用 `external-application-review`；如需修改，由主控 Agent 制作净化交接包，再由另一个全新且不继承审稿或写作上下文的修改 Subagent 生成下一个内部 `Rn`，并再次调用 `application-review`，正式 `Vn` 不变。
- 双信任务完成时，完成双信差异和推荐人身份一致性自检。
- 必要时更新 `Student_Profile/Task_Board.md`。
