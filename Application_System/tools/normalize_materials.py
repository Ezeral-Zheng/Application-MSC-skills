#!/usr/bin/env python3
"""Normalize Application-MSC student materials into Markdown."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


VAULT_ROOT = Path(__file__).resolve().parents[2]
SYSTEM_DIR = VAULT_ROOT / "Application_System"
TEMPLATE_DIR = SYSTEM_DIR / "templates"
SCHEMA_PATH = SYSTEM_DIR / "config" / "directory_schema.json"


def load_schema() -> dict[str, object]:
    if not SCHEMA_PATH.exists():
        return {
            "source_material_dirs": ["Basic_Info", "Course_Info", "Personalization_Info", "Resume", "Recommender_Info"],
            "attachment_dirs": ["Additional_Documents"],
            "output_dirs": {"Recommendation_Letters": "Recommendation-Letter", "Personal_Statement": "Personal-Statement"},
            "memory_dirs": ["Student_Profile", "Revision_History", "Review_Memory", "Review_History", "External_Review_History"],
            "ignored_root_dirs": [".git", ".obsidian", "Application_System", "_Student_Template"],
        }
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


SCHEMA = load_schema()
SPREADSHEET_MATERIAL_DIRS = list(SCHEMA.get("spreadsheet_material_dirs", []))
STUDENT_SUPPORT_DIRS = list(
    dict.fromkeys(
        list(SCHEMA.get("attachment_dirs", []))
        + SPREADSHEET_MATERIAL_DIRS
        + list(SCHEMA.get("memory_dirs", []))
    )
)
MATERIAL_DIRS = list(
    dict.fromkeys(
        list(SCHEMA.get("attachment_dirs", []))
        + list(SCHEMA.get("source_material_dirs", []))
        + SPREADSHEET_MATERIAL_DIRS
        + list((SCHEMA.get("output_dirs") or {}).keys())
    )
)
CONVERTIBLE_SUFFIXES = {".docx", ".doc", ".pdf", ".pptx"}
IGNORED_DIRS = set(SCHEMA.get("ignored_root_dirs", []))
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
PPTX_NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def filename_timestamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def is_student_dir(path: Path) -> bool:
    if not path.is_dir() or path.name in IGNORED_DIRS or path.name.startswith("."):
        return False
    return any((path / name).is_dir() for name in MATERIAL_DIRS)


def student_dirs(selected: str | None, all_students: bool) -> list[Path]:
    if selected:
        path = VAULT_ROOT / selected
        if not path.is_dir():
            raise SystemExit(f"Student directory not found: {path}")
        return [path]
    if all_students:
        return sorted([p for p in VAULT_ROOT.iterdir() if is_student_dir(p)], key=lambda p: p.name)
    raise SystemExit("Pass --student <name> or --all")


def ensure_support_dirs(student: Path) -> None:
    for rel in STUDENT_SUPPORT_DIRS:
        (student / rel).mkdir(parents=True, exist_ok=True)


def text_from_node(node: ET.Element) -> str:
    parts: list[str] = []
    for text_node in node.findall(".//w:t", NS):
        if text_node.text:
            parts.append(text_node.text)
    return "".join(parts).strip()


def docx_to_markdown(path: Path) -> tuple[str, list[str]]:
    issues: list[str] = []
    try:
        with zipfile.ZipFile(path) as zf:
            xml_data = zf.read("word/document.xml")
    except Exception as exc:
        return "", [f"无法读取 docx：{exc}"]

    root = ET.fromstring(xml_data)
    body = root.find("w:body", NS)
    if body is None:
        return "", ["docx 缺少正文 body"]

    blocks: list[str] = []
    for child in list(body):
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            text = text_from_node(child)
            if text:
                blocks.append(text)
        elif tag == "tbl":
            rows: list[list[str]] = []
            for tr in child.findall("w:tr", NS):
                cells = [text_from_node(tc).replace("\n", " ") for tc in tr.findall("w:tc", NS)]
                if any(cells):
                    rows.append(cells)
            if rows:
                width = max(len(row) for row in rows)
                normalized = [row + [""] * (width - len(row)) for row in rows]
                header = normalized[0]
                blocks.append("| " + " | ".join(escape_table_cell(c) for c in header) + " |")
                blocks.append("| " + " | ".join(["---"] * width) + " |")
                for row in normalized[1:]:
                    blocks.append("| " + " | ".join(escape_table_cell(c) for c in row) + " |")
                blocks.append("")

    content = "\n\n".join(blocks).strip()
    if not content:
        issues.append("docx 提取结果为空，可能需要人工检查")
    return content, issues


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def doc_to_markdown(path: Path) -> tuple[str, list[str]]:
    textutil = shutil.which("textutil")
    if not textutil:
        return "", ["缺少 textutil，无法处理 .doc 文件"]
    try:
        result = subprocess.run(
            [textutil, "-convert", "txt", "-stdout", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        return "", [f"textutil 转换失败：{exc.stderr.strip() or exc}"]
    content = result.stdout.strip()
    return content, ([] if content else ["doc 提取结果为空，可能需要人工检查"])


def pdf_to_markdown(path: Path) -> tuple[str, list[str]]:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        return "", ["缺少 pdftotext；PDF 第一版按 best-effort 标记为待人工处理"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.txt"
        try:
            subprocess.run([pdftotext, str(path), str(out)], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            return "", [f"pdftotext 转换失败：{exc.stderr.strip() or exc}"]
        content = out.read_text(encoding="utf-8", errors="replace").strip()
    return content, ([] if content else ["PDF 提取结果为空，可能是扫描件"])


def pptx_to_markdown(path: Path) -> tuple[str, list[str]]:
    issues: list[str] = []
    slides: list[tuple[int, str]] = []
    try:
        with zipfile.ZipFile(path) as zf:
            slide_names = sorted(
                (
                    name
                    for name in zf.namelist()
                    if name.startswith("ppt/slides/slide") and name.endswith(".xml")
                ),
                key=lambda name: int(Path(name).stem.replace("slide", "")),
            )
            for index, name in enumerate(slide_names, start=1):
                root = ET.fromstring(zf.read(name))
                texts = [
                    text_node.text.strip()
                    for text_node in root.findall(".//a:t", PPTX_NS)
                    if text_node.text and text_node.text.strip()
                ]
                if texts:
                    slides.append((index, "\n".join(texts)))
    except Exception as exc:
        return "", [f"无法读取 pptx：{exc}"]

    if not slides:
        issues.append("pptx 提取结果为空，可能主要由图片或扫描内容构成")
        return "", issues

    content = "\n\n".join(f"## Slide {index}\n\n{text}" for index, text in slides)
    return content, issues


def convert_file(path: Path) -> tuple[str, list[str]]:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return docx_to_markdown(path)
    if suffix == ".doc":
        return doc_to_markdown(path)
    if suffix == ".pdf":
        return pdf_to_markdown(path)
    if suffix == ".pptx":
        return pptx_to_markdown(path)
    return "", [f"不支持的文件类型：{suffix}"]


def wrap_markdown(source: Path, content: str, issues: list[str]) -> str:
    title = source.stem
    rel = source.relative_to(VAULT_ROOT)
    issue_block = "\n".join(f"- {issue}" for issue in issues) if issues else "- 无"
    body = content.strip() if content.strip() else "[待人工补充：未能从源文件提取可用文本]"
    return (
        f"# {title}\n\n"
        "## 文件信息\n\n"
        f"- 来源文件：`{rel}`\n"
        f"- 标准化时间：{timestamp()}\n"
        f"- 主要资料源：是\n\n"
        "## 转换问题\n\n"
        f"{issue_block}\n\n"
        "## 正文\n\n"
        f"{body}\n"
    )


def should_update(source: Path, target: Path) -> bool:
    if not target.exists():
        return True
    return source.stat().st_mtime > target.stat().st_mtime


def backup_existing(target: Path) -> Path:
    backup_dir = target.parent / ".backups"
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / f"{target.stem}.{filename_timestamp()}{target.suffix}"
    shutil.copy2(target, backup)
    return backup


def normalize_student(student: Path, dry_run: bool = False) -> dict[str, object]:
    if not dry_run:
        ensure_support_dirs(student)
    converted: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []
    backups: list[str] = []

    for source in sorted(student.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in CONVERTIBLE_SUFFIXES:
            continue
        if ".backups" in source.parts:
            continue
        target = source.with_suffix(".md")
        rel_source = str(source.relative_to(VAULT_ROOT))
        if not should_update(source, target):
            skipped.append(rel_source)
            continue

        content, issues = convert_file(source)
        rendered = wrap_markdown(source, content, issues)
        if dry_run:
            converted.append(rel_source)
            continue

        if target.exists():
            backups.append(str(backup_existing(target).relative_to(VAULT_ROOT)))
        target.write_text(rendered, encoding="utf-8")
        converted.append(rel_source)
        if issues:
            failed.extend(f"{rel_source}: {issue}" for issue in issues)

    write_completeness_report(student, converted, skipped, failed, dry_run=dry_run)
    return {"converted": converted, "skipped": skipped, "failed": failed, "backups": backups}


def md_has_content(path: Path) -> bool:
    try:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return False
    return len(text) > 40 and "[待人工补充" not in text


def write_completeness_report(
    student: Path, converted: list[str], skipped: list[str], failed: list[str], dry_run: bool = False
) -> None:
    existing_categories: list[str] = []
    missing_categories: list[str] = []
    sparse_files: list[str] = []

    for rel in MATERIAL_DIRS:
        folder = student / rel
        material_files = list_material_files(folder, rel) if folder.exists() else []
        if material_files:
            existing_categories.append(rel)
            for md in [path for path in material_files if path.suffix.lower() == ".md"]:
                if not md_has_content(md):
                    sparse_files.append(str(md.relative_to(VAULT_ROOT)))
        else:
            missing_categories.append(rel)

    report = (
        "# 资料完整性检查\n\n"
        f"- 学生：{student.name}\n"
        f"- 检查时间：{timestamp()}\n"
        f"- Dry run：{'是' if dry_run else '否'}\n\n"
        "## 已有资料类别\n\n"
        + lines_or_none(existing_categories)
        + "\n## 缺失资料类别\n\n"
        + lines_or_none(missing_categories)
        + "\n## 本次转换或更新\n\n"
        + lines_or_none(converted)
        + "\n## 本次跳过（已有较新 Markdown）\n\n"
        + lines_or_none(skipped)
        + "\n## 转换失败或待人工处理\n\n"
        + lines_or_none(failed)
        + "\n## 可能为空或仍需补充的 Markdown\n\n"
        + lines_or_none(sparse_files)
    )
    if not dry_run:
        (student / "Student_Profile" / "资料完整性检查.md").write_text(report, encoding="utf-8")


def list_material_files(folder: Path, rel: str) -> list[Path]:
    if rel in SPREADSHEET_MATERIAL_DIRS:
        return list(folder.glob("*.xlsx")) + list(folder.glob("*.md"))
    return list(folder.glob("*.md"))


def lines_or_none(items: list[str]) -> str:
    if not items:
        return "- 无\n\n"
    return "".join(f"- {item}\n" for item in items) + "\n"


def ensure_memory_file(student: Path, dry_run: bool = False) -> None:
    path = student / "Student_Profile" / "学生偏好总结.md"
    if path.exists() or dry_run:
        return
    path.write_text(
        "# 学生偏好总结\n\n"
        f"- 学生：{student.name}\n"
        f"- 创建时间：{timestamp()}\n\n"
        "## 稳定偏好\n\n- 暂无\n\n"
        "## 待观察偏好\n\n- 暂无\n\n"
        "## 推荐信偏好\n\n- 暂无\n\n"
        "## 个人陈述偏好\n\n- 暂无\n\n"
        "## 简历偏好\n\n- 暂无\n\n"
        "## 禁用或慎用表达\n\n- 暂无\n\n"
        "## 常用核心素材\n\n- 暂无\n\n"
        "## 历次修改摘要\n\n- 暂无\n",
        encoding="utf-8",
    )


def ensure_task_board_file(student: Path, dry_run: bool = False) -> None:
    path = student / "Student_Profile" / "Task_Board.md"
    if path.exists() or dry_run:
        return
    template = TEMPLATE_DIR / "student_task_board.md"
    if template.exists():
        content = template.read_text(encoding="utf-8")
        content = content.replace("- 学生：", f"- 学生：{student.name}")
        content = content.replace("- 更新时间：", f"- 更新时间：{timestamp()}")
    else:
        content = f"# 学生任务看板\n\n- 学生：{student.name}\n- 更新时间：{timestamp()}\n"
    path.write_text(content, encoding="utf-8")


def ensure_ps_narrative_matrix_file(student: Path, dry_run: bool = False) -> None:
    path = student / "Student_Profile" / "PS_申请组合叙事矩阵.md"
    if path.exists() or dry_run:
        return
    template = TEMPLATE_DIR / "ps_narrative_matrix.md"
    if template.exists():
        content = template.read_text(encoding="utf-8")
        content = content.replace("- 学生：", f"- 学生：{student.name}", 1)
        content = content.replace("- 最近更新：", f"- 最近更新：{timestamp()}", 1)
    else:
        content = (
            "# PS 申请组合叙事矩阵\n\n"
            f"- 学生：{student.name}\n"
            f"- 最近更新：{timestamp()}\n"
        )
    path.write_text(content, encoding="utf-8")


def ensure_review_memory_file(student: Path, dry_run: bool = False) -> None:
    path = student / "Review_Memory" / "审查问题记忆.md"
    if path.exists() or dry_run:
        return
    path.write_text(
        "# 审查问题记忆\n\n"
        f"- 学生：{student.name}\n"
        f"- 创建时间：{timestamp()}\n\n"
        "## 稳定错误模式\n\n- 暂无\n\n"
        "## 待观察问题\n\n- 暂无\n\n"
        "## 推荐信审查记忆\n\n- 暂无\n\n"
        "## 个人陈述审查记忆\n\n- 暂无\n\n"
        "## 简历审查记忆\n\n- 暂无\n\n"
        "## 已解决问题\n\n- 暂无\n\n"
        "## 历次审查摘要\n\n- 暂无\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student", help="Student directory name to normalize")
    parser.add_argument("--all", action="store_true", help="Normalize all student directories")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without writing files")
    parser.add_argument(
        "--initialize-only",
        action="store_true",
        help="Create standard directories and support files without converting materials.",
    )
    args = parser.parse_args()

    students = student_dirs(args.student, args.all)
    overall_failed = 0
    for student in students:
        if not args.dry_run:
            ensure_support_dirs(student)
            ensure_memory_file(student, dry_run=args.dry_run)
            ensure_task_board_file(student, dry_run=args.dry_run)
            ensure_ps_narrative_matrix_file(student, dry_run=args.dry_run)
            ensure_review_memory_file(student, dry_run=args.dry_run)
        if args.initialize_only:
            print(f"== {student.name} ==")
            print("support directories/files initialized")
            continue
        result = normalize_student(student, dry_run=args.dry_run)
        overall_failed += len(result["failed"])
        print(f"== {student.name} ==")
        print(f"converted/updated: {len(result['converted'])}")
        print(f"skipped: {len(result['skipped'])}")
        print(f"issues: {len(result['failed'])}")
        if result["backups"]:
            print("backups:")
            for item in result["backups"]:
                print(f"  - {item}")
    if overall_failed:
        print(f"completed with {overall_failed} conversion issue(s); see 资料完整性检查.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
