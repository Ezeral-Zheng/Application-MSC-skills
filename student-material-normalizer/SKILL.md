---
name: student-material-normalizer
description: 当前 Application-MSC Vault 专用资料标准化 skill。用于扫描学生目录，将 docx/doc/pdf 等资料转成结构化 Markdown，初始化 Student_Profile、Revision_History、Review_History、Review_Memory，并检查资料完整性。
---

# Student Material Normalizer

## 使用场景

当用户要求“转换资料”“整理学生文件”“写作前准备资料”“检查某个学生资料是否完整”，或任何写作/修改任务开始前，先使用本 skill。

## 默认流程

1. 确认学生目录存在。
2. 运行 `Application_System/tools/normalize_materials.py --student <学生名>`。
3. 检查生成或更新的 `.md`。
4. 确认以下目录存在：
   - `Additional_Documents/`
   - `Student_Profile/`
   - `Revision_History/`
   - `Review_Memory/`
   - `Review_History/`
   - `Student_Profile/Task_Board.md`
5. 写作前读取 `Student_Profile/资料完整性检查.md`。

## 参考资料

- 本 skill 的参考文档放在 `Application_System/skills/student-material-normalizer/references/`。
- 可放资料字段模板、目录规范、Markdown 标准化样例、常见源文件问题处理说明等。
- 标准化前如参考目录中有与当前资料类型或转换问题相关的文件，应优先读取相关文件；不要无差别读取全部参考资料。

## 转换规则

- `.md` 是正式资料源。
- `.docx` / `.doc` / `.pdf` / `.pptx` 是原始附件或转换来源。
- `Additional_Documents/` 用于保存腾讯文档附件预览导出的原始文件及同名 Markdown；原文件和转写后的 `.md` 必须并排保存。
- 通过 Tencent Docs MCP 导入材料并保存 Markdown 时，若正文出现 `ATTACHMENT ... \f 文件名`，应在导入阶段立即尝试下载/导出附件到 `Additional_Documents/`，然后运行标准化生成同名 `.md`。
- 如果同名 `.md` 不存在，生成新的标准化 Markdown。
- 如果同名 `.md` 已存在且源文件更新，先备份旧 `.md`，再更新。
- 如果同名 `.md` 已存在且源文件没有更新，保留现有 `.md`。
- PDF 第一版 best-effort；PPTX 按幻灯片页码提取文本；无法提取时在完整性检查中提示人工处理。

## 输出要求

标准化 Markdown 至少包含：

- 文件标题
- 来源文件路径
- 标准化时间
- 正文内容
- 未能解析或需要人工补充的问题

资料完整性检查应列出：

- 已存在资料类别
- 缺失资料类别
- 转换失败文件
- 可能为空或仍需学生补充的文件
