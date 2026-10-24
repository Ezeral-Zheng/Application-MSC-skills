# Application MSC Agent

面向硕士申请文书的本地 Agent 工作流。包含资料标准化、推荐信、双语个人陈述、学生版叙事矩阵、定向简历、独立审稿、隔离修改、版本管理和 Word 导出。

本仓库保留原有根目录 skills 路径，同时收录总控 `AGENTS.md`、`Application_System/` 下的工具、模板、配置和测试。它是供支持文件访问与独立子代理的 Agent 环境执行的规则及工具集，不是自动连接模型的独立服务。

## 快速开始

需要 Python 3.10+。在本仓库中创建工作区：

```bash
git clone https://github.com/Ezeral-Zheng/Application-MSC-skills.git
cd Application-MSC-skills
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python setup_workspace.py
python Application_System/tools/validate_application_system.py
python -m unittest discover -s Application_System/tests -v
```

Windows 可用 `.venv\Scripts\activate`。`setup_workspace.py` 将根目录的 skills 复制到工作流所需的 `Application_System/skills/`；该副本不进入 Git。根目录始终是 skills 的维护源。拉取更新后运行 `python setup_workspace.py --refresh`；已生成的旧副本会先备份，未知来源的已有目录不会被覆盖。

在支持独立子代理的 Codex/Agent 环境打开本目录，先读取 `AGENTS.md`。例如：“整理某学生的申请资料”“根据反馈修改某学生的个人陈述”“生成某学生的定向简历”。具体任务要求和最新事实优先于模板。

## 数据与版本

为每位学生建立单独目录，放入 `Basic_Info/`、`Course_Info/`、`Resume/` 等资料，然后预览标准化操作：

```bash
mkdir -p '示例学生/Basic_Info'
python Application_System/tools/normalize_materials.py --student '示例学生' --dry-run
python Application_System/tools/normalize_materials.py --student '示例学生'
```

学生原始资料、申请正文、记忆、任务日志、导出文件、索引和运行报告不属于代码仓库，已由默认忽略规则排除。不要在根目录的通用 skills 中写入学生材料。

正式文书以带 `Vn` 的 Markdown 为内容源；一次任务只预留一个正式版本，内部修订保存在临时目录。PS 默认英文700–1000词、英文在前中文在后；项目官方要求可以覆盖。事实审查通过后进行全新隔离的内容审稿；初始单篇、组合差异和补充单篇各有独立计数。详见 [总控规则](AGENTS.md) 和 [系统说明](Application_System/README.md)。

## 外部能力与可选工具

- `.docx` 导出使用 python-docx，Excel 模板读取使用 openpyxl。
- PDF资料提取可安装 Poppler 提供 `pdftotext`；旧 `.doc` 转换依赖 macOS `textutil` 或另行提供的转换环境。
- Word/PDF视觉验收需要渲染器。Codex中优先使用环境提供的文档工具；`export_resume_docx.py --render` 会查找当前用户的Codex内置运行时，未安装时应先配置渲染环境。
- 腾讯文档读写需要相应连接器；专业导入工具依赖自行提供的 `Postgraduate Program List/Major List.xlsx`。本仓库仅包含空白专业信息模板，不包含学生专业库或第三方完整数据集。
- 独立审稿与隔离修改需要运行环境支持全新、不继承上下文的子代理。工具脚本本身不发送模型请求。

## 流程设计原型

```bash
python Application_System/tools/skill-studio-prototype/serve.py
```

访问 http://127.0.0.1:8765/ 。该原型用于查看 skills、组织流程及导出方案，尚未连接实际文书任务执行器。

## 维护

修改根目录skills后重新运行 `setup_workspace.py --refresh`，再执行测试和一致性检查。真实推荐信范文不随当前版本分发；推荐信目录中提供两种通用结构说明，使用时仍必须读取当前学生和推荐人的真实资料。示例姓名及测试夹具只用于验证格式和逻辑，不构成可复用申请事实。
