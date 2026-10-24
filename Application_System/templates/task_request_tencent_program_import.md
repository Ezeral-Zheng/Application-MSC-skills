# 腾讯择校表专业信息导入任务输入模板

## 任务信息

- 学生姓名：
- 腾讯在线表格 URL：
- 目标子表：
- 专业列表：

## 本地资料

- Major List：`Postgraduate Program List/Major List.xlsx`
- 目标表头：
- 写入计划输出：

## 匹配规则

- 未匹配专业：不写入，先请用户确认。
- 歧义专业：不写入，先列候选项。
- 目标字段缺失：留空，不编造。
- 目标行已有内容：不覆盖，除非用户明确要求。

## 输出

- JSON 写入计划：`Application_System/reports/tencent_program_import_plan.json`
- Markdown 写入计划：`Application_System/reports/tencent_program_import_plan.md`
- 阻塞条件：无法确认 file_id/sheet_id、表头不明、专业匹配歧义、用户要求只看计划。
