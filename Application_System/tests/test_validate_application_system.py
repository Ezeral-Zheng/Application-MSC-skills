#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Application_System.tools import validate_application_system as validator


class SystemNoiseTest(unittest.TestCase):
    def test_registered_skills_submodule_is_not_system_noise(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            vault = Path(temp)
            system = vault / "Application_System"
            skills = system / "skills"
            (skills / ".git").mkdir(parents=True)
            (vault / ".gitmodules").write_text(
                '[submodule "Application_System/skills"]\n'
                "\tpath = Application_System/skills\n"
                "\turl = https://example.com/skills.git\n",
                encoding="utf-8",
            )

            with (
                patch.object(validator, "VAULT_ROOT", vault),
                patch.object(validator, "SYSTEM_DIR", system),
                patch.object(validator, "SKILLS_DIR", skills),
            ):
                findings = validator.check_system_noise()

        self.assertFalse(any(item.path.endswith("skills/.git") for item in findings))


class SkillRegistryTest(unittest.TestCase):
    def test_inline_explanations_and_composed_skills_are_recognized(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            agents = root / 'AGENTS.md'
            agents.write_text('3. 根据任务调用对应专项 skill：\n'
                              '   - 导出：`ps-word-export`（说明）\n'
                              '   - 简历：`resume-application-pipeline`（编排 `resume-writer`）\n'
                              '4. 读取资料。\n')
            for name in ['ps-word-export', 'resume-application-pipeline', 'resume-writer']:
                skill = root / 'skills' / name / 'SKILL.md'
                skill.parent.mkdir(parents=True)
                skill.write_text('# Skill')
            with patch.object(validator, 'AGENTS_PATH', agents), patch.object(validator, 'SKILLS_DIR', root / 'skills'):
                self.assertEqual(validator.check_agent_skill_registry(), [])

    def test_english_contract_headings_are_recognized(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / 'resume-writer' / 'SKILL.md'
            skill.parent.mkdir()
            skill.write_text('Vn application-review Resume/\n## Blocking conditions\n## Output contract\n')
            with patch.object(validator, 'SKILLS_DIR', root):
                self.assertEqual(validator.check_skill_files({'output_dirs': {'Resume': 'Resume'}}), [])


if __name__ == "__main__":
    unittest.main()
