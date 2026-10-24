#!/usr/bin/env python3
"""Report Application-MSC student workflow status without generating documents."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = VAULT_ROOT / "Application_System" / "reports"
SCHEMA_PATH = VAULT_ROOT / "Application_System" / "config" / "directory_schema.json"
VERSION_RE = re.compile(r"(?:^|[-_ ])V(\d+)(?=[._ -]|$)", re.IGNORECASE)
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def load_schema() -> dict[str, object]:
    if not SCHEMA_PATH.exists():
        return {
            "source_material_dirs": ["Basic_Info", "Course_Info", "Personalization_Info", "Resume", "Recommender_Info"],
            "output_dirs": {
                "Recommendation_Letters": "Recommendation-Letter",
                "Personal_Statement": "Personal-Statement",
                "Resume": "Resume",
                "Resume_Experience": "Resume-Experience",
            },
            "ignored_root_dirs": ["Application_System", "_Student_Template"],
        }
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


SCHEMA = load_schema()
MATERIAL_DIRS = list(SCHEMA.get("source_material_dirs", []))
SPREADSHEET_MATERIAL_DIRS = list(SCHEMA.get("spreadsheet_material_dirs", []))
MATERIAL_DIRS = list(dict.fromkeys(MATERIAL_DIRS + SPREADSHEET_MATERIAL_DIRS))
OUTPUT_DIRS = list((SCHEMA.get("output_dirs") or {}).keys())


def is_student_dir(path: Path) -> bool:
    if not path.is_dir() or path.name.startswith("."):
        return False
    if path.name in set(SCHEMA.get("ignored_root_dirs", [])):
        return False
    return any((path / rel).is_dir() for rel in MATERIAL_DIRS + OUTPUT_DIRS)


def selected_students(name: str | None, all_students: bool) -> list[Path]:
    if name:
        path = VAULT_ROOT / name
        if not path.is_dir():
            raise SystemExit(f"Student directory not found: {path}")
        return [path]
    if all_students:
        return sorted([p for p in VAULT_ROOT.iterdir() if is_student_dir(p)], key=lambda p: p.name)
    raise SystemExit("Pass --student <name> or --all")


def md_count(folder: Path) -> int:
    return len(list(folder.glob("*.md"))) if folder.exists() else 0


def material_count(folder: Path, rel: str) -> int:
    if not folder.exists():
        return 0
    if rel in SPREADSHEET_MATERIAL_DIRS:
        return len(list(folder.glob("*.xlsx"))) + len(list(folder.glob("*.md")))
    return md_count(folder)


def output_count(folder: Path) -> int:
    return len(versioned_markdown_files(folder)) if folder.exists() else 0


def versioned_markdown_files(folder: Path) -> list[Path]:
    if not folder.exists():
        return []
    return [path for path in folder.glob("*.md") if VERSION_RE.search(path.name)]


def blocked_reviews(student: Path) -> list[str]:
    history = student / "Review_History"
    if not history.exists():
        return []
    blocked: list[str] = []
    for report in sorted(history.glob("*.md")):
        text = report.read_text(encoding="utf-8", errors="replace")
        status = parse_frontmatter(text).get("status", "")
        if status == "Blocked" or (not status and "Blocked" in text):
            blocked.append(str(report.relative_to(VAULT_ROOT)))
    return blocked


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta


def unreviewed_outputs(student: Path) -> list[str]:
    reviewed_text = ""
    history = student / "Review_History"
    if history.exists():
        reviewed_text = "\n".join(
            p.read_text(encoding="utf-8", errors="replace") for p in sorted(history.glob("*.md"))
        )
    missing: list[str] = []
    for rel in OUTPUT_DIRS:
        folder = student / rel
        if not folder.exists():
            continue
        for output in sorted(versioned_markdown_files(folder)):
            output_rel = str(output.relative_to(VAULT_ROOT))
            if output.name not in reviewed_text and output_rel not in reviewed_text:
                missing.append(output_rel)
    return missing


def render(students: list[Path]) -> str:
    lines = [
        "# Batch Status Report",
        "",
        f"- 生成时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 学生概览",
        "",
        "| 学生 | 缺失资料类别 | 文档数 | Blocked 审查 | 未审查文档 |",
        "|---|---|---:|---:|---:|",
    ]
    details: list[str] = []
    for student in students:
        missing_materials = [rel for rel in MATERIAL_DIRS if material_count(student / rel, rel) == 0]
        document_count = sum(output_count(student / rel) for rel in OUTPUT_DIRS)
        blocked = blocked_reviews(student)
        unreviewed = unreviewed_outputs(student)
        lines.append(
            "| "
            + " | ".join(
                [
                    student.name,
                    ", ".join(missing_materials) if missing_materials else "无",
                    str(document_count),
                    str(len(blocked)),
                    str(len(unreviewed)),
                ]
            )
            + " |"
        )
        if missing_materials or blocked or unreviewed:
            details.extend(render_student_detail(student, missing_materials, blocked, unreviewed))
    lines.extend(["", "## 需要关注", ""])
    lines.extend(details if details else ["- 无"])
    lines.append("")
    return "\n".join(lines)


def render_student_detail(student: Path, missing: list[str], blocked: list[str], unreviewed: list[str]) -> list[str]:
    lines = [f"### {student.name}", ""]
    lines.append("缺失资料类别：" + (", ".join(missing) if missing else "无"))
    lines.append("")
    lines.append("Blocked 审查：")
    lines.extend(f"- {item}" for item in blocked) if blocked else lines.append("- 无")
    lines.append("")
    lines.append("未审查文档：")
    lines.extend(f"- {item}" for item in unreviewed) if unreviewed else lines.append("- 无")
    lines.append("")
    return lines


def report_path(report_dir: Path = REPORT_DIR) -> Path:
    return report_dir / "Batch-Status-Report.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student", help="Student directory name")
    parser.add_argument("--all", action="store_true", help="Report all student directories")
    parser.add_argument("--write", action="store_true", help="Write report to Application_System/reports")
    args = parser.parse_args()
    content = render(selected_students(args.student, args.all))
    if args.write:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        path = report_path()
        path.write_text(content, encoding="utf-8")
        print(path)
    else:
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
