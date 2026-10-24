# Application MSC 文书写作系统

这是当前 Obsidian Vault 专用的申请文书工作流系统。

## 核心入口

- 总控说明：`AGENTS.md`
- 专项 skills：`Application_System/skills/`
- 工具脚本：`Application_System/tools/`

## 学生版叙事矩阵

使用 `ps-narrative-matrix` 生成可先交给学生看的申请方案。可直接请求“生成示例学生的叙事矩阵”“生成某学生某学校某专业的叙事矩阵”或“在原有矩阵中新增某专业”。已有矩阵时保留原有目标，新增总览行与项目叙事卡；同校不同专业优先降低叙事重复，跨校同方向允许适度复用。

学生版采用V7学生交付规范：六列组合总览与九字段项目叙事卡，交付为 `Student_Profile/学生名-PS申请组合叙事矩阵-Vn.md`，不包含思考过程、审查记录或内部状态。格式模板位于 `Application_System/skills/ps-narrative-matrix/assets/student-matrix.md`。原 `Student_Profile/PS_申请组合叙事矩阵.md` 继续作为 PS 工作输入，保留内部记录，新增方案备份后局部同步。

仅生成矩阵时完成事实、格式、原有项目保留和同校差异检查；PS 正文的独立审稿流程在后续写作时执行。

## 可视化流程设计原型

本地 `Application Studio` 可只读查看当前 skills 的输入、产物与原始规则，按通用、商科、理工或跨专业方向添加配置，并组合流程。支持节点画布、规则工作表和分步向导三种视图，方案可导出/导入 JSON，也可生成 Markdown 执行提示。

```bash
python3 Application_System/tools/skill-studio-prototype/serve.py
```

访问 `http://127.0.0.1:8765/?variant=A`。这是流程设计原型；方向配置保存在方案中，未写回基础 skills，且尚未接入实际文书任务执行。具体边界见 `Application_System/tools/skill-studio-prototype/NOTES.md`。

## 常用命令

标准化某个学生资料：

```bash
python3 Application_System/tools/normalize_materials.py --student 示例学生
```

标准化所有学生资料：

```bash
python3 Application_System/tools/normalize_materials.py --all
```

预览但不写入：

```bash
python3 Application_System/tools/normalize_materials.py --student 示例学生 --dry-run
```

只初始化标准目录和支持文件，不转换资料：

```bash
python3 Application_System/tools/normalize_materials.py --all --initialize-only
```

刷新全局版本索引：

```bash
python3 Application_System/tools/build_version_index.py --write
```

检查系统规则和目录一致性：

```bash
python3 Application_System/tools/validate_application_system.py --write
```

批量查看所有学生状态：

```bash
python3 Application_System/tools/batch_status_report.py --all
```

保存批量状态报告：

```bash
python3 Application_System/tools/batch_status_report.py --all --write
```

完整腾讯表格写入流程请使用 skill：

```text
tencent-program-importer
```

如需单独生成本地候选匹配和写入计划，可运行工具：

```bash
python3 Application_System/tools/prepare_tencent_program_import.py \
  --file-url '腾讯在线表格URL' \
  --student '学生姓名' \
  --item '学校英文名 专业英文名' \
  --output Application_System/reports/tencent_program_import_plan.json \
  --markdown Application_System/reports/tencent_program_import_plan.md
```

如果报告里出现 `unmatched` 或 `ambiguous`，先人工确认，不要写入腾讯表格。
即使全部显示为 matched，也应由 `tencent-program-importer` 复核后再决定是否写入。

导入或补写 PS 个性化素材请使用 skill：

```text
personalization-material-importer
```

个性化素材保存到学生目录下的 `Personalization_Materials/`。如果腾讯文档素材为空或缺失，系统可以基于学生已有资料和申请方向生成“个性化素材补写候选”，但必须区分已确认事实、合理推断和待确认问题。

生成下一个版本文件名：

```bash
python3 Application_System/tools/next_version_path.py \
  --dir '示例学生/Personal_Statement' \
  --key '示例学生-MSc-Electrical-Engineering-Personal-Statement'
```

检查某篇 PS 与同一学生其他申请目标是否高度雷同：

```bash
python3 Application_System/tools/check_ps_portfolio_similarity.py \
  --target '示例学生/Personal_Statement/目标稿.md'
```

该工具比较开头、全文段落功能、经历段复用与结构风险，只提供预警；最终由隔离 Subagent 的 `portfolio-differentiation` 审稿判断。

## 资料原则

- `.md` 是主要资料源。
- `.docx`、`.doc`、`.pdf` 是原始附件或转换来源。
- `Personalization_Materials/` 是 PS 个性化素材的主要输入之一，用于保存腾讯文档复制内容和待确认补写候选。
- `Major Selected/` 是每个学生的目标专业库目录，默认保存 Excel 专业清单；用户后续提供模板后按模板维护。
- 转换时采用“保留并更新”：已有 `.md` 较新则跳过；源文件较新则备份旧 Markdown 后更新。
- PDF 第一版 best-effort；没有 `pdftotext` 时会标记为待人工处理。
- 系统目录定义集中在 `Application_System/config/directory_schema.json`；新增正式目录时优先更新该配置，再同步 skill 规则。

## 写作原则

- 推荐信、PS、简历和修改稿都只生成 Markdown。
- 正式成稿和修改稿文件名必须带版本号：`V1`、`V2`、`V3`。每次用户请求只预留下一个正式版本；上次交付为 `V1` 时，本次无论内部修订多少轮，最终只发布 `V2`。
- 所有新生成文件均不使用日期前缀。正式文书使用“稳定 key + `Vn`”，审查和修改记录跟随对应目标与版本；日期保留在 frontmatter 或正文中。已有日期前缀历史文件不重命名，版本工具仍会读取。
- 内部候选稿使用临时 `R1`、`R2` 等轮次号，不进入正式输出目录和版本索引。事实审查未通过时只递增 `Rn`，最多新增 3 个内部轮次。
- 内部审查报告随候选稿保存在任务临时目录；`Review_History/` 和版本索引只记录最终交付的正式 `Vn`。交付回复默认只展示这一正式版本。
- 事实审查通过后，由全新且不继承写作、修改或历史审稿上下文的 Subagent 执行 PS 八维框架下的单篇独立内容审稿（前七维评分，第八维无组合输入时为 N/A）。平均分低于 `8.5` 或仍有 P0/P1 时继续优化，初始单篇最多执行 `C1-C5` 五轮。
- 每轮修改也由另一个全新隔离 Subagent 执行。主控 Agent 只传入当前稿、净化问题单和最小事实包；完整报告、分数、旧稿和过程推理不得在审稿人与修改者之间流转。
- `C1-C5`、独立组合 `P1-P5`、组合修改后的补充单篇复核 `S1-S5` 报告，以及内部候选稿、净化交接包和核销表都只存在于任务临时目录；正式目录只保存最后通过版本对应的一份报告。
- PS 已存在其他申请目标时，写作前维护 `Student_Profile/PS_申请组合叙事矩阵.md`，并读取其他目标各自最新正式 PS。
- PS 已有其他目标时，单篇通过后无论是否到 `C5`，都必须由另一个隔离 Subagent 执行独立 `P1-P5` `portfolio-differentiation` 横向审稿，检查开头、经历顺序、叙事功能和能力结论。组合若要求修改，新稿重新事实审查并进入独立 `S1-S5` 单篇复核，再由全新审稿人继续下一轮组合审稿；未取得组合 Pass 不发布。
- 审查报告顶部使用固定 frontmatter，供版本索引和批量报告解析 `Pass`、`Needs Fix`、`Blocked` 状态。
- 每个学生使用 `Student_Profile/Task_Board.md` 跟踪任务状态、阻塞项和最终版本。
- 全局版本记录使用 `Application_System/indexes/Version_Index.md`。
- 审查报告写入 `Review_History/`，审查问题记忆写入 `Review_Memory/审查问题记忆.md`。
- 同一学生两封推荐信分别参考两种课程推荐信结构：一封用“并列课程型”，一封用“深挖课程项目型”。固定段只保留功能并改写句式，可变段必须根据该推荐人的课程/交集重写，并控制重复度。
- PS 默认在同一 `.md` 文件内输出双语版本：英文在前、中文在后，不分点；英文默认硬性控制 700-1000 words，目标约 800 words；覆盖本科专业选择原因、本科经历、职业规划、硕士专业/学校选择原因四项信息责任，顺序与段落由论证决定。目标专业信息优先参考学生 `Major Selected/` 和用户本次输入。
- 多专业 PS 必须让目标专业改变核心问题、开头视角、素材排序、经历功能、能力缺口和职业目标。相同硬事实允许复用，完整非事实句和整套前段叙事不得复制；机械换词不算差异化。
- PS 写作使用五维非量化质量边界；隔离审稿使用八维框架，单篇以前七维平均分与 `8.5` 提交门禁。审稿报告通过稳定问题 ID 和修改交接单向主 Agent 返回原文定位、问题、影响、修改动作、事实边界与验收标准。
- 写 PS 前读取 `Personalization_Materials/`；学生偏好总结只管风格和长期偏好，不能替代事实依据。
- 修改后自动更新每个学生的 `Student_Profile/学生偏好总结.md`；只有真正属于学生风格或个人偏好的结论写入学生偏好。
- 学生偏好分为稳定偏好和待观察偏好，避免一次反馈污染长期风格。
