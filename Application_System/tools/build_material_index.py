#!/usr/bin/env python3
"""Build category-level material indexes with linked attachment inputs."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CATEGORY_ALIASES = {
    "Courses": "Course_Info",
    "Course": "Course_Info",
    "Resume": "Resume",
    "Personalization": "Personalization_Info",
    "Basic": "Basic_Info",
    "Recommender": "Recommender_Info",
}


def relative_link_target(value: str) -> str | None:
    match = re.search(r"\(([^)]+Additional_Documents/[^)]+\.md)\)", value)
    return match.group(1) if match else None


def normalized_attachment_name(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".md":
        return filename
    if suffix in {".docx", ".doc", ".pdf", ".pptx"}:
        return filename[: -len(suffix)] + ".md"
    return filename + ".md"


def build(student: str, category: str) -> Path:
    student_dir = ROOT / student
    source_dir_name = CATEGORY_ALIASES.get(category, category)
    source_dir = student_dir / source_dir_name
    if not source_dir.is_dir():
        raise SystemExit(f"Category directory not found: {source_dir}")

    sources = sorted(p for p in source_dir.glob("*.md") if "资料索引" not in p.name)
    attachment_paths: dict[str, set[str]] = {}
    all_attachments = sorted((student_dir / "Additional_Documents").glob("*.md"))
    for source in sources:
        text = source.read_text(encoding="utf-8", errors="replace")
        refs = set()
        for line in text.splitlines():
            target = relative_link_target(line)
            if target:
                refs.add(target)
        for attachment in all_attachments:
            if attachment.name in text:
                refs.add(f"../Additional_Documents/{attachment.name}")
        for attachment in all_attachments:
            original_name = attachment.name
            if normalized_attachment_name(original_name) in text:
                refs.add(f"../Additional_Documents/{original_name}")
        attachment_paths[source.name] = refs

    output = student_dir / "Student_Profile" / f"资料索引-{category}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {student}-{category}资料索引",
        "",
        f"- 资料类别：`{category}`（目录：`{source_dir_name}`）",
        f"- 学生：{student}",
        f"- 生成时间：{dt.datetime.now():%Y-%m-%d %H:%M:%S}",
        "",
        "## 读取规则",
        "",
        "读取此类别时，先读取下方正文 Markdown，再读取正文明确关联的 `Additional_Documents/*.md`。附件内容是该类别的补充输入，不是只供人工查看的孤立文件。没有明确关联的附件不自动并入，避免跨类别素材混用。",
        "",
        "## 正文输入",
        "",
    ]
    if not sources:
        lines.append("- 当前类别没有 Markdown 正文输入。")
    for source in sources:
        lines.append(f"- [{source.name}](../{source_dir_name}/{source.name})")
        refs = sorted(attachment_paths[source.name])
        if refs:
            lines.append("  - 关联附件输入：")
            for ref in refs:
                name = Path(ref).name
                markdown_name = normalized_attachment_name(name)
                lines.append(f"    - [{markdown_name}](../Additional_Documents/{markdown_name})")
        else:
            lines.append("  - 关联附件输入：无")
    lines.extend([
        "",
        "## 附件使用边界",
        "",
        "附件只能补充正文中已经出现或明确指向的事实。写作或审查时必须保留附件 Markdown 的可追溯路径；原始 DOCX/PDF 仅用于回看和核验。",
        "",
    ])
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student", required=True)
    parser.add_argument("--category", required=True)
    args = parser.parse_args()
    print(build(args.student, args.category))


if __name__ == "__main__":
    main()
