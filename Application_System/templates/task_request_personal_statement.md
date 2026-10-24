# 个人陈述任务输入模板

## 任务信息

- 学生姓名：
- 目标学校：
- 目标专业：
- 申请方向：
- 输出语言：英文 + 中文
- 输出顺序：同一 `.md` 文件内英文在前，中文在后
- 英文长度：默认 700-1000 words，目标约 800 words；如项目官方明确要求其他范围，填写项目覆盖值并附来源
- 字数门禁：英文低于下限或高于上限时，候选稿不得进入正式发布
- 特别限制：

## 素材范围

- Basic_Info：
- Personalization_Info：
- Personalization_Materials：
- Course_Info：
- Resume：
- Program_Info 或项目资料：
- Major Selected：
- 禁止使用资料：

## 个性化素材状态

- 是否已有腾讯文档个性化素材：
- 是否需要生成补写候选：
- 待确认问题：

## 申请组合差异化

- 是否已有其他目标项目 PS：
- 本次一句话核心命题：
- 本次因果路径：
- 必须使用的证据及职责：
- 主动舍弃的素材：
- 复用经历的既有写法：
- 本篇语义增量（片段/问题/行动焦点/约束/能力结论）：
- 禁止复用的事实组合、行动链和反思结论：
- 预期结构签名：
- 与近邻项目至少改变的两项设计维度：
- 本次需要避开的既有开头、段落功能序列或能力结论：
- `Student_Profile/PS_申请组合叙事矩阵.md` 是否已更新：

## 版本与审查

- 目标输出目录：`Personal_Statement/`
- 版本 key：`学生名-目标专业或学校-Personal-Statement`
- 审查类型：`Personal-Statement`
- 单篇内容门禁：七维平均分不低于 8.5，且无 P0/需继续修改的 P1
- 内容审查轮次：初始单篇 `C1-C5`（最多 5 轮）；有其他申请目标时，独立组合 `P1-P5`（最多 5 轮，不占 `C`）；组合修改后的补充单篇复核 `S1-S5`（最多 5 轮，不占 `C` 或 `P`）
- 审稿输入模板：`Application_System/templates/ps_content_review_input.md`
- 隔离修改模板：`Application_System/templates/ps_isolated_revision_packet.md`
- 隔离要求：每轮审稿人和每轮修改者都使用全新、不继承上下文的 Subagent
- 过程文件位置：任务专用临时目录
- 横向检查：`check_ps_portfolio_similarity.py` + `external-application-review` 的 `portfolio-differentiation`
- 阻塞条件：缺少关键事实、目标项目、申请方向、或个性化素材无法追溯。
