#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


TOOL_PATH = (
    Path(__file__).resolve().parents[1]
    / "tools"
    / "check_ps_portfolio_similarity.py"
)


def load_tool():
    spec = importlib.util.spec_from_file_location("check_ps_portfolio_similarity", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load tool: {TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PortfolioSimilarityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tool = load_tool()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_ps(self, name: str, paragraphs: list[str]) -> Path:
        path = self.root / name
        path.write_text(
            "# Personal Statement\n\n## English Version\n"
            + "\n".join(paragraphs)
            + "\n\n## 中文版本\n中文对照稿。\n",
            encoding="utf-8",
        )
        return path

    def test_flags_same_opening_and_reused_early_narrative(self) -> None:
        base = self.write_ps(
            "student-program-a-Personal-Statement-V1.md",
            [
                "I chose Financial Management because I wanted to understand how business value is measured, tested and sustained. My academic training built a quantitative foundation for this goal.",
                "My first step beyond classroom finance was a tax risk competition. It taught me to evaluate business decisions under policy and operational constraints.",
                "I then developed a smart wardrobe business plan. The project taught me to translate consumer needs into a commercially testable model.",
                "Programme A will help me connect financial analysis with digital operations.",
            ],
        )
        target = self.write_ps(
            "student-program-b-Personal-Statement-V1.md",
            [
                "I chose Financial Management because I wanted to understand how business value is measured, tested and sustained. My academic training built a quantitative foundation for this goal.",
                "My first step beyond classroom finance was a tax risk competition. It taught me to evaluate business decisions under policy and operational constraints.",
                "I then developed a smart wardrobe business plan. The project taught me to translate consumer needs into a commercially testable model.",
                "Programme B will help me connect financial analysis with sustainable management.",
            ],
        )

        report = self.tool.compare_target(target, [base])

        self.assertEqual(report["status"], "Needs Differentiation")
        self.assertGreaterEqual(report["comparisons"][0]["opening_similarity"], 0.9)
        self.assertGreaterEqual(report["comparisons"][0]["early_narrative_similarity"], 0.8)
        self.assertGreaterEqual(report["comparisons"][0]["reused_sentence_count"], 3)

    def test_passes_when_program_changes_the_narrative_design(self) -> None:
        base = self.write_ps(
            "student-program-a-Personal-Statement-V1.md",
            [
                "A tax risk competition first showed me how regulation can reshape the economics of cross-border retail.",
                "Studying finance gave me the tools to test those constraints through valuation and risk analysis.",
                "I now want to strengthen my understanding of international compliance and institutional strategy.",
            ],
        )
        target = self.write_ps(
            "student-program-b-Personal-Statement-V1.md",
            [
                "While testing a smart wardrobe concept, I learned that an impressive technology has little value until users trust it and operations can support it.",
                "I used consumer research and financial modelling to turn product functions into a viable commercial proposition.",
                "That experience now draws me toward technology leadership and product development.",
            ],
        )

        report = self.tool.compare_target(target, [base])

        self.assertEqual(report["status"], "Pass")
        self.assertLess(report["comparisons"][0]["opening_similarity"], 0.65)
        self.assertEqual(report["comparisons"][0]["reused_sentence_count"], 0)

    def test_flags_same_rhetorical_structure_despite_different_wording(self) -> None:
        base = self.write_ps(
            "student-program-a-Personal-Statement-V1.md",
            [
                "A delayed supplier handoff first made me question how an online promise becomes a reliable customer experience.",
                "My Financial Management degree at Example University gave me grounding in accounting, valuation and quantitative analysis, where I maintained a strong GPA.",
                "In a herbal food venture, I mapped purchasing and delivery decisions to identify where operational uncertainty entered the customer journey.",
                "A smart wardrobe proposal later let me examine a different service system through user research, pricing and adoption constraints.",
                "I plan to begin in digital operations and eventually lead cross-border service networks that connect commercial decisions with fulfilment.",
                "This master's programme is the next step because its training in logistics systems and electronic commerce will help me close that capability gap.",
            ],
        )
        target = self.write_ps(
            "student-program-b-Personal-Statement-V1.md",
            [
                "Watching customers explain their preferences in person led me to ask how those signals could inform an internet product.",
                "At Another University, studying corporate finance and statistics while earning a high academic ranking taught me to test business claims with evidence.",
                "While building a community brand, I organised interview findings and translated recurring concerns into decisions about channels and product presentation.",
                "Designing an intelligent wardrobe concept then exposed questions about privacy, interface trust and willingness to pay.",
                "After graduation I hope to work in digital product strategy before taking responsibility for platforms serving users across markets.",
                "The programme will equip me with the internet computing and product design knowledge needed to move from informal feedback to scalable digital services.",
            ],
        )

        report = self.tool.compare_target(target, [base])
        comparison = report["comparisons"][0]

        self.assertEqual(report["status"], "Needs Differentiation")
        self.assertLess(comparison["opening_similarity"], 0.2)
        self.assertEqual(comparison["reused_sentence_count"], 0)
        self.assertEqual(
            comparison["rhetorical_signature"],
            [
                "opening",
                "academic-background",
                "experience",
                "experience",
                "career-goal",
                "program-fit",
            ],
        )
        self.assertGreaterEqual(comparison["structural_similarity"], 0.95)

    def test_does_not_flag_long_drafts_with_different_rhetorical_structures(self) -> None:
        base = self.write_ps(
            "student-program-a-Personal-Statement-V1.md",
            [
                "A customer complaint made me reconsider how service promises are designed.",
                "My undergraduate degree and strong GPA prepared me to analyse that question.",
                "I tested the issue through a retail project focused on delivery reliability.",
                "A second case helped me compare operational and financial constraints.",
                "After graduation I hope to work in service operations and later lead regional teams.",
                "This master's programme will equip me with the systems knowledge I still lack.",
            ],
        )
        target = self.write_ps(
            "student-program-b-Personal-Statement-V1.md",
            [
                "A high product price forced our team to decide which assumptions actually mattered.",
                "The project became a single extended test of demand, privacy and commercial adoption.",
                "My career goal emerged from the limits of that model rather than from its forecast.",
                "My academic training and coursework explain how I could test the financial case but not the technology.",
                "That boundary now defines the decisions I want to make as an AI product manager.",
                "The programme offers the technical and governance perspective required for those decisions.",
            ],
        )

        report = self.tool.compare_target(target, [base])
        comparison = report["comparisons"][0]

        self.assertEqual(report["status"], "Pass")
        self.assertLess(comparison["structural_similarity"], 0.8)
        self.assertEqual(comparison["reused_sentence_count"], 0)

    def test_flags_reused_experience_passage_inside_different_structures(self) -> None:
        base = self.write_ps(
            "student-program-a-Personal-Statement-V1.md",
            [
                "A customer conversation made me question how service promises become repeatable operations.",
                "My academic training gave me the quantitative foundation to investigate that question.",
                "For the Heyunxin herbal food venture, I analysed 601 questionnaires and 569 valid responses, organised three tasting sessions, and used customer feedback to refine product positioning, channel choices and membership ideas. The work taught me that consumer insight matters only when it can be translated into a commercially sustainable system.",
                "After graduation I hope to work in digital operations and later lead regional service networks.",
                "This programme will help me connect customer insight with logistics and platform design.",
            ],
        )
        target = self.write_ps(
            "student-program-b-Personal-Statement-V1.md",
            [
                "My goal of managing cross-functional teams grew from seeing good ideas stall between specialist groups.",
                "In one project, I coordinated a herbal food venture that collected 601 questionnaires with 569 valid responses and ran three tasting sessions. I drew on customer feedback to adjust positioning, channels and a membership concept, learning that market insight creates value only when converted into a sustainable business system.",
                "That limitation now shapes the managerial questions I want to pursue.",
                "My strong GPA demonstrates that I am prepared for rigorous graduate study.",
                "The programme offers the organisational and strategic training required for that transition.",
                "I hope to apply this perspective in consumer businesses operating across markets.",
            ],
        )

        report = self.tool.compare_target(target, [base])
        comparison = report["comparisons"][0]

        self.assertEqual(report["status"], "Needs Differentiation")
        self.assertLess(comparison["structural_similarity"], 0.8)
        self.assertGreaterEqual(comparison["experience_passage_similarity"], 0.45)
        self.assertEqual(comparison["experience_passage_match"]["target_paragraph"], 2)
        self.assertEqual(comparison["experience_passage_match"]["prior_paragraph"], 3)

    def test_allows_minimal_hard_fact_reuse_with_new_experience_meaning(self) -> None:
        base = self.write_ps(
            "student-program-a-Personal-Statement-V1.md",
            [
                "A tasting session made me question how fragmented feedback could become product data.",
                "The Heyunxin survey produced 601 questionnaires and 569 valid responses, which I grouped to identify recurring preferences and gaps in our proposed membership loop. I use this evidence here to examine why one-off research could not support continuous product learning.",
                "That exercise exposed the limits of one-off research for a digital service.",
                "My academic training supports the transition toward internet computing.",
                "The programme offers the systems training needed to build continuous feedback mechanisms.",
            ],
        )
        target = self.write_ps(
            "student-program-b-Personal-Statement-V1.md",
            [
                "Cross-functional disagreement, rather than data scarcity, shaped my interest in management.",
                "The programme offers the organisational perspective needed for that transition.",
                "In Heyunxin, 601 questionnaires yielded 569 valid responses, but my focus here is how finance, design and marketing members interpreted the same evidence differently and had to agree on a viable decision. The shared dataset therefore serves as evidence of a coordination problem rather than a research-method problem.",
                "After graduation I hope to take responsibility for decisions that require specialist teams to reach a common commercial position.",
                "My undergraduate degree and academic foundation demonstrate readiness for graduate study.",
                "I hope to manage consumer projects across specialist and cultural boundaries.",
            ],
        )

        report = self.tool.compare_target(target, [base])
        comparison = report["comparisons"][0]

        self.assertEqual(report["status"], "Pass")
        self.assertLess(comparison["structural_similarity"], 0.8)
        self.assertLess(comparison["experience_passage_similarity"], 0.45)

    def test_only_compares_latest_version_per_application_key(self) -> None:
        files = [
            self.write_ps("student-program-a-Personal-Statement-V1.md", ["Old version."]),
            self.write_ps("student-program-a-Personal-Statement-V3.md", ["Latest version."]),
            self.write_ps("student-program-b-Personal-Statement-V2.md", ["Other programme."]),
        ]

        latest = self.tool.select_latest_versions(files)

        self.assertEqual(
            [path.name for path in latest],
            [
                "student-program-a-Personal-Statement-V3.md",
                "student-program-b-Personal-Statement-V2.md",
            ],
        )


if __name__ == "__main__":
    unittest.main()
