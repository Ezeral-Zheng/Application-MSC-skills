# Reports

本目录用于保存批量巡检、失败报告和系统状态报告。

推荐输出：

- `Batch-Status-Report.md`
- `任务key-Failure-Report.md`
- `System-Validation.md`
- `tencent_program_import_plan.md`

批量状态报告会扫描学生正式文档目录：`Recommendation_Letters/`、`Personal_Statement/`、`Resume/`、`Resume_Experience/`。

系统一致性检查报告用于检查 skill、Agent 规则、目录结构、版本命名、禁用 `Drafts/` 路径、非 Markdown 输出和系统缓存文件。

新报告文件名不添加日期前缀。批量状态和系统校验报告为滚动快照，每次执行刷新固定文件；生成时间保留在报告正文中。

批量状态报告可通过以下命令生成：

```bash
python3 Application_System/tools/batch_status_report.py --all --write
```

系统一致性检查可通过以下命令生成：

```bash
python3 Application_System/tools/validate_application_system.py --write
```
