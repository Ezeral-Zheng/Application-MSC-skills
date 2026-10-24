#!/usr/bin/env python3
"""Build a Markdown index of V-numbered Application-MSC output files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


VAULT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = VAULT_ROOT / "Application_System" / "config" / "directory_schema.json"
INDEX_PATH = VAULT_ROOT / "Application_System" / "indexes" / "Version_Index.md"
VERSION_RE = re.compile(r"(?:^|[-_ ])V(\d+)(?=[._ -]|$)", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def load_output_types() -> dict[str, str]:
    if not SCHEMA_PATH.exists():
        return {
            "Recommendation_Letters": "Recommendation-Letter",
            "Personal_Statement": "Personal-Statement",
            "Resume": "Resume",
            "Resume_Experience": "Resume-Experience",
        }
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return dict(schema.get("output_dirs", {}))


OUTPUT_TYPES = load_output_types()


def is_student_dir(path: Path) -> bool:
    if not path.is_dir() or path.name.startswith("."):
        return False
    if path.name in {"Application_System", "_Student_Template"}:
        return False
    return any((path / rel).is_dir() for rel in OUTPUT_TYPES)


def version_from_name(path: Path) -> str:
    matches = list(VERSION_RE.finditer(path.name))
    if not matches:
        return ""
    return f"V{matches[-1].group(1)}"


def date_from_name(path: Path) -> str:
    match = DATE_RE.match(path.name)
    return match.group(0) if match else ""


def key_from_stem(path: Path, version: str) -> str:
    stem = path.stem
    stem = DATE_RE.sub("", stem).lstrip("-_ ")
    if version:
        stem = re.sub(rf"[-_ ]?{re.escape(version)}$", "", stem, flags=re.IGNORECASE)
    return stem.strip("-_ ")


def review_status(student: Path, doc_type: str, version: str, key: str, output_path: str) -> tuple[str, str]:
    history = student / "Review_History"
    if not history.exists() or not version:
        return "", ""
    candidates = sorted(history.glob(f"*{doc_type}*{version}*审查报告.md"))
    if not candidates:
        return "", ""
    # Prefer an exact frontmatter path match; shared school/program tokens are
    # too broad to safely associate reports by filename alone.
    exact_candidates = []
    for report in candidates:
        meta = parse_frontmatter(report.read_text(encoding="utf-8", errors="replace"))
        if meta.get("draft_path", "") == output_path:
            exact_candidates.append(report)
    if exact_candidates:
        candidates = exact_candidates

    generic_tokens = {student.name, doc_type, *re.split(r"[-_ ]+", doc_type)}
    key_tokens = [
        token
        for token in re.split(r"[-_ ]+", key)
        if token and token not in generic_tokens
    ]
    keyed_candidates = [report for report in candidates if any(token in report.name for token in key_tokens)]
    if keyed_candidates:
        candidates = keyed_candidates
    report = candidates[-1]
    text = report.read_text(encoding="utf-8", errors="replace")
    meta = parse_frontmatter(text)
    status_value = meta.get("status", "")
    if status_value in {"Blocked", "Needs Fix", "Pass"}:
        return status_value, str(report.relative_to(VAULT_ROOT))
    for status in ["Blocked", "Needs Fix", "Pass"]:
        if status in text:
            return status, str(report.relative_to(VAULT_ROOT))
    return "Unknown", str(report.relative_to(VAULT_ROOT))


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


def collect_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for student in sorted([p for p in VAULT_ROOT.iterdir() if is_student_dir(p)], key=lambda p: p.name):
        for folder_name, doc_type in OUTPUT_TYPES.items():
            folder = student / folder_name
            outputs = sorted(folder.glob("*.md")) if folder.exists() else []
            for output in outputs:
                version = version_from_name(output)
                if not version:
                    continue
                key = key_from_stem(output, version)
                status, report = review_status(
                    student,
                    doc_type,
                    version,
                    key,
                    str(output.relative_to(VAULT_ROOT)),
                )
                rows.append(
                    [
                        student.name,
                        doc_type,
                        key,
                        version,
                        str(output.relative_to(VAULT_ROOT)),
                        status,
                        report,
                        "",
                        date_from_name(output),
                    ]
                )
    return rows


def render(rows: list[list[str]]) -> str:
    header = (
        "# Version Index\n\n"
        f"- 更新时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "- 生成方式：`python3 Application_System/tools/build_version_index.py --write`\n"
        "- 扫描范围：学生目录下的 `Recommendation_Letters/`、`Personal_Statement/`、`Resume/`、`Resume_Experience/`\n\n"
        "| 学生 | 文书类型 | Key | 版本 | 路径 | 审查状态 | 审查报告 | 是否最终版 | 日期 |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
    )
    if not rows:
        return header + "|  |  |  |  |  |  |  |  |  |\n"
    body = "".join("| " + " | ".join(escape_cell(cell) for cell in row) + " |\n" for row in rows)
    return header + body


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write Application_System/indexes/Version_Index.md")
    args = parser.parse_args()
    content = render(collect_rows())
    if args.write:
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        INDEX_PATH.write_text(content, encoding="utf-8")
        print(INDEX_PATH)
    else:
        print(content)
    return 0


if __name__ == "__main__":
    sys.exit(main())
