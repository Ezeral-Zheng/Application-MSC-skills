#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from Application_System.tools import batch_status_report
from Application_System.tools import next_version_path
from Application_System.tools import validate_application_system


class OutputNamingTest(unittest.TestCase):
    def test_next_version_path_has_no_date_prefix_and_reads_legacy_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "2026-07-23-Student-Program-Personal-Statement-V2.md").touch()

            path = next_version_path.next_path(
                folder,
                "Student-Program-Personal-Statement",
                "md",
            )

        self.assertEqual(
            path.name,
            "Student-Program-Personal-Statement-V3.md",
        )

    def test_system_reports_use_stable_names_without_date_prefixes(self) -> None:
        report_dir = Path("/tmp/reports")

        self.assertEqual(
            batch_status_report.report_path(report_dir).name,
            "Batch-Status-Report.md",
        )
        self.assertEqual(
            validate_application_system.report_path(report_dir).name,
            "System-Validation.md",
        )


if __name__ == "__main__":
    unittest.main()
