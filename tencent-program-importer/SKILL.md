---
name: tencent-program-importer
description: 当前 Application-MSC Vault 专用腾讯在线表格专业信息导入 skill。根据用户提供的腾讯文档表格地址、学生姓名和“学校名 + 专业名”列表，从 Postgraduate Program List/Major List.xlsx 生成候选匹配与安全写入计划；由本 skill 负责最终确认、阻塞判断和 Tencent Docs MCP 写入。
---

# Tencent Program Importer

## 使用场景

当用户要求把某些学校/专业信息写入学生的腾讯在线表格、择校表、专业选择表、留学专业表，或从 `Major List.xlsx` 同步专业信息到腾讯文档时，使用本 skill。

本 skill 是正式入口；`Application_System/tools/prepare_tencent_program_import.py` 只是本 skill 使用的本地候选匹配与写入计划生成器。Python 工具不做最终业务判断，也不直接写腾讯文档。

## 必要输入

1. 腾讯在线表格 URL。
2. 学生姓名。如果用户未提供，可留空，但有 `学生姓名` 字段时建议补充。
3. 专业列表，每项格式通常为：

```text
学校英文名 专业英文名
```

示例：

```text
The Chinese University of Hong Kong Master of Accountancy
National University of Singapore MSc Finance
```

## 必读资料

1. `Postgraduate Program List/Major List.xlsx`
2. `Application_System/templates/学校专业信息收集模板.xlsx`
3. 必要时读取 `Application_System/reports/tencent_program_import_plan.md`

## 默认流程

1. 从腾讯在线表格 URL 获取 `file_id` 和目标 `sheet_id`：
   - 使用 Tencent Docs MCP 的 `sheet_get_sheet_info` 查看子表名称、ID、行列数量。
   - 如有多个子表且用户未说明目标子表，优先选择与专业库、Program、Database、择校、申请、专业信息相关的子表；仍不确定时询问用户。
2. 读取目标子表前几行，确定表头：
   - 使用 `sheet_get_cell_data` 读取表格开头区域。
   - 优先识别包含 `学校英文名`、`Program Name`、`项目中文名`、`学费`、`语言要求` 等字段的表头行。
   - 将目标表头保存为 JSON list，供本地匹配工具使用。
3. 运行本地工具生成候选匹配与写入计划：

```bash
python3 Application_System/tools/prepare_tencent_program_import.py \
  --file-url '<腾讯在线表格URL>' \
  --file-id '<file_id>' \
  --sheet-id '<sheet_id>' \
  --student '<学生姓名>' \
  --item '<学校英文名 专业英文名>' \
  --target-headers '<目标表头JSON或JSON文件>' \
  --output Application_System/reports/tencent_program_import_plan.json \
  --markdown Application_System/reports/tencent_program_import_plan.md
```

4. 检查报告：
   - 如果有 `unmatched`，不要写入，向用户列出未匹配项和候选项，请用户确认真实专业。
   - 如果有 `ambiguous`，不要写入，向用户列出候选项，请用户选择。
   - 即使工具标记为 `matched`，也要快速复核学校名、专业名和关键字段；Python 匹配结果是候选结果，不是最终业务判断。
   - 只有 `unmatched_count = 0`、`ambiguous_count = 0`，且 skill 复核无异常时，才进入写入步骤。
5. 写入腾讯在线表格：
   - 读取 `tencent_program_import_plan.json` 中的 `mcp_sheet_set_range_value`。
   - 使用 Tencent Docs MCP 的 `sheet_set_range_value` 写入。
6. 写入后复查：
   - 使用 `sheet_get_cell_data` 读取刚写入的区域，确认行数和关键字段已落地。
   - 输出写入摘要：写入几条专业、写入行号、未写入项、需要人工补充字段。

## 匹配与阻塞规则

- 专业匹配必须谨慎，不确定时宁可不写。
- Python 工具只负责候选匹配和结构化计划；最终是否写入由本 skill 根据上下文和用户确认决定。
- 如果学校匹配但专业不确定，标记为 `ambiguous` 或 `unmatched`，等待用户确认。
- 如果用户提供的是简称，例如 `NUS Finance`，可进行模糊匹配，但必须展示匹配结果。
- 如果最高分候选和第二候选接近，不自动写入。
- 不把 Major List 中没有的信息编造进腾讯表格。
- 目标表格没有对应字段时留空，不新增列，除非用户明确要求。

## 字段映射规则

默认字段映射由 `prepare_tencent_program_import.py` 执行，核心关系：

- `学校英文名` -> `学校英文名`
- `项目中文译名` -> `项目中文名`
- `项目英文名` -> `Program Name`
- `学制` -> `学制`
- `语言要求（IELTS简化/原文保留）` -> `语言要求`
- `学费（非本地学生，数字）` -> `学费`
- `项目官网URL` -> `来源URL`
- `课程（中文 / English；分号分隔）` -> `核心课程` / `原文摘录/证据`

如果目标表格字段与默认模板不同，应以目标表头为准，只填能匹配的字段。

## 安全写入规则

- 默认不清空、不覆盖整张表。
- 只写入本次计划中的非空单元格。
- 若目标行已有内容，写入前必须确认是否追加到新行；不要覆盖已有专业记录。
- 写入前必须先生成 `Application_System/reports/tencent_program_import_plan.md` 供人工检查。
- 有未匹配或歧义专业时禁止调用 `sheet_set_range_value`。
- 用户明确要求“先别写/只做匹配/先给我看计划”时，只生成报告，不调用 MCP 写入。

## 输出

每次执行至少保留：

- `Application_System/reports/tencent_program_import_plan.json`
- `Application_System/reports/tencent_program_import_plan.md`

执行完成后向用户报告：

- 匹配成功的专业。
- 未匹配或歧义专业。
- 写入的腾讯文档子表。
- 写入行号。
- 空缺字段或需要人工补充的信息。

## 阻塞条件

- 无法从腾讯在线表格 URL 确认 `file_id` 或 `sheet_id`。
- 目标子表表头无法识别。
- 专业存在 `unmatched` 或 `ambiguous`。
- 目标行已有内容且用户未确认是否追加或覆盖。
- 用户明确要求只生成计划、暂不写入。

## 最小输出

- `Application_System/reports/tencent_program_import_plan.json`
- `Application_System/reports/tencent_program_import_plan.md`
- 若实际写入，报告写入子表、行号、成功项、未写入项和空缺字段。
