from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / 'skills/ps-word-export/scripts/export_ps_docx.py'
SPEC = importlib.util.spec_from_file_location('ps_word_export', SCRIPT)
exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exporter)


class StudentInitialsTest(unittest.TestCase):
    def resolve(self, student, material='', override=None):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            basic = root / 'Basic_Info'
            basic.mkdir()
            (basic / 'profile.md').write_text(material, encoding='utf-8')
            source = root / 'Personal_Statement/statement.md'
            return exporter.verified_student_abbreviation(source, student, override)

    def test_each_chinese_character_has_an_initial(self):
        self.assertEqual(self.resolve('陈欣妍', '拼音：chen xin yan'), 'CXY')

    def test_joined_given_name_must_not_silently_drop_an_initial(self):
        with self.assertRaises(ValueError):
            self.resolve('陈欣妍', '拼音：chen xinyan')

    def test_user_confirmed_full_initials_override_grouped_pinyin(self):
        self.assertEqual(self.resolve('陈欣妍', '拼音：chen xinyan', 'cxy'), 'CXY')

    def test_incomplete_chinese_override_is_rejected(self):
        with self.assertRaises(ValueError):
            self.resolve('陈欣妍', override='CX')

    def test_full_name_initials_in_profile(self):
        self.assertEqual(self.resolve('陈欣妍', '姓名缩写：CXY\n拼音：chen xinyan'), 'CXY')

    def test_english_nickname_is_not_used_for_chinese_name(self):
        with self.assertRaises(ValueError):
            self.resolve('陈欣妍', 'English Name: Chloe')

    def test_compound_surname_keeps_both_characters(self):
        self.assertEqual(self.resolve('欧阳娜娜', '拼音：ou yang na na'), 'OYNN')

    def test_non_chinese_name_keeps_all_name_components(self):
        self.assertEqual(self.resolve('John Michael Smith'), 'JMS')


if __name__ == '__main__':
    unittest.main()
