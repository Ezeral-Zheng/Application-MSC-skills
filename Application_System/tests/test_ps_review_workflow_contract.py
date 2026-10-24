#!/usr/bin/env python3

from __future__ import annotations

import unittest
from pathlib import Path


SYSTEM_DIR = Path(__file__).resolve().parents[1]
SKILLS_DIR = SYSTEM_DIR / "skills"
VAULT_ROOT = SYSTEM_DIR.parent


class PsReviewWorkflowContractTest(unittest.TestCase):
    def read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_external_review_contract_has_eight_dimensions_and_85_gate(self) -> None:
        review = self.read(SKILLS_DIR / "external-application-review" / "SKILL.md")
        rubric = self.read(
            SKILLS_DIR
            / "external-application-review"
            / "references"
            / "个人陈述八维评分与校准标准.md"
        )

        for dimension in [
            "逻辑结构",
            "经历与专业匹配",
            "语言表达",
            "个人辨识度",
            "动机说服力",
            "学校与项目匹配",
            "职业规划",
            "跨申请结构独立性与相似度",
        ]:
            self.assertIn(dimension, rubric)
        self.assertIn("第八维", review)
        self.assertIn("PS-PORTFOLIO-008", review)
        self.assertIn("8.5", review)
        self.assertIn("P0", review)

    def test_review_and_revision_are_fresh_context_isolated_workers(self) -> None:
        agents = self.read(VAULT_ROOT / "AGENTS.md")
        revision = self.read(SKILLS_DIR / "application-revision" / "SKILL.md")
        external = self.read(SKILLS_DIR / "external-application-review" / "SKILL.md")

        self.assertIn("最多 5", agents)
        self.assertIn("不继承", external)
        self.assertIn("全新", external)
        self.assertIn("不继承", revision)
        self.assertIn("全新", revision)
        self.assertIn("净化", revision)

    def test_internal_review_artifacts_stay_out_of_formal_directories(self) -> None:
        agents = self.read(VAULT_ROOT / "AGENTS.md")
        external = self.read(SKILLS_DIR / "external-application-review" / "SKILL.md")

        self.assertIn("任务专用临时目录", agents)
        self.assertIn("不得进入", external)
        self.assertIn("C1", external)
        self.assertIn("C5", external)

    def test_sanitized_worker_packet_templates_exist(self) -> None:
        review_packet = self.read(SYSTEM_DIR / "templates" / "ps_content_review_input.md")
        revision_packet = self.read(
            SYSTEM_DIR / "templates" / "ps_isolated_revision_packet.md"
        )

        self.assertIn("禁止读取或接收", review_packet)
        self.assertIn("上一轮得分", review_packet)
        self.assertIn("最小事实包", revision_packet)
        self.assertIn("不读取完整审稿报告", revision_packet)
        self.assertIn("问题核销表", revision_packet)

    def test_isolated_modifier_cannot_publish_or_read_portfolio_history(self) -> None:
        revision = self.read(SKILLS_DIR / "application-revision" / "SKILL.md")

        self.assertIn("完全跳过下方“默认流程”", revision)
        self.assertIn("不负责版本号、正式文件", revision)
        self.assertIn("禁止直接读取叙事矩阵和其他正式 PS", revision)
        self.assertIn("不得创建或修改正式版本", revision)
        self.assertIn("Personal Statement 无论修改来源是什么", revision)
        self.assertIn("正式发布后才生成", revision)

    def test_fact_gate_does_not_auto_fix_content_quality(self) -> None:
        factual_review = self.read(SKILLS_DIR / "application-review" / "SKILL.md")
        five_dim = self.read(
            SKILLS_DIR
            / "external-application-review"
            / "references"
            / "个人陈述五维质量标准.md"
        )

        self.assertIn("content_review_required", factual_review)
        self.assertIn("纯内容质量问题不得进入本事实修订循环", factual_review)
        self.assertIn("对 PS 而言不等于可以交付", factual_review)
        self.assertIn("不参与 `application-review` 的事实门禁状态判断", five_dim)

    def test_ps_length_default_is_hard_700_to_1000_word_gate(self) -> None:
        agents = self.read(VAULT_ROOT / "AGENTS.md")
        writer = self.read(SKILLS_DIR / "personal-statement-writer" / "SKILL.md")
        factual_review = self.read(SKILLS_DIR / "application-review" / "SKILL.md")
        task_template = self.read(SYSTEM_DIR / "templates" / "task_request_personal_statement.md")

        for text in [agents, writer, factual_review, task_template]:
            self.assertIn("700-1000", text)
            self.assertNotIn("500-1000", text)
        self.assertIn("不得通过事实与格式门禁", agents)
        self.assertIn("属于 `Needs Fix`", factual_review)
        self.assertIn("字数门禁", task_template)

    def review_counter_contract(self) -> str:
        external = self.read(SKILLS_DIR / "external-application-review" / "SKILL.md")
        return external.split("## 单篇、组合与补充复核的独立计数", 1)[1].split(
            "\n## ", 1
        )[0]

    def test_review_counters_are_independent_bounded_and_cannot_reset(self) -> None:
        contract = self.review_counter_contract()

        for counter in ("C", "P", "S"):
            with self.subTest(counter=counter):
                self.assertRegex(contract, rf"`{counter}1`\s*至\s*`{counter}5`")
        self.assertRegex(contract, r"独立使用 `P1` 至 `P5`，不占用 `C` 轮次")
        self.assertRegex(contract, r"`S` 轮[^。]*不占用 `C` 或 `P`")
        self.assertIn("不得把三套计数合并、互相抵扣或重置", contract)
        self.assertIn("正式 `Vn` 始终不变", contract)
        self.assertNotIn("共享同一个 `C1-C5` 计数器", contract)

    def test_c5_pass_and_portfolio_revision_keep_required_review_transitions(self) -> None:
        contract = self.review_counter_contract()

        # Reaching the initial single-draft cap does not consume portfolio rounds.
        self.assertRegex(contract, r"`C5` 通过[^。]*进入必需的组合审稿")
        self.assertRegex(
            contract,
            r"第 `Pn` 轮为 `Revise` 且 `n<5`[^。]*"
            r"该稿通过 `application-review` 后[^。]*"
            r"补充单篇复核 `S1` 至 `S5`",
        )
        self.assertRegex(contract, r"只有 `S` 为 `Pass`[^。]*下一轮 `P\(n\+1\)`")
        self.assertRegex(contract, r"`C5` 仍未通过则停止、不发布")
        self.assertRegex(contract, r"`S5` 或 `P5` 仍未通过则停止、不发布")
        self.assertIn("仅有前两项不得正式发布", contract)

    def test_reviewer_does_not_compare_prior_scores_or_reset_packet_round(self) -> None:
        external = self.read(SKILLS_DIR / "external-application-review" / "SKILL.md")
        rubric = self.read(
            SKILLS_DIR
            / "external-application-review"
            / "references"
            / "个人陈述八维评分与校准标准.md"
        )
        review_packet = self.read(SYSTEM_DIR / "templates" / "ps_content_review_input.md")

        self.assertIn("上一轮得分", external)
        self.assertIn("旧候选稿", external)
        self.assertIn("不接收或解释相邻轮次分数变化", rubric)
        self.assertIn("{{CURRENT_CONTENT_REVIEW_ROUND}}", review_packet)
        self.assertIn("当前未使用的 `C1-C5`", review_packet)
        self.assertIn("当前未使用的 `S1-S5`", review_packet)
        self.assertIn("两套计数独立，不得沿用模板值或重置", review_packet)


if __name__ == "__main__":
    unittest.main()
