#!/usr/bin/env python3
"""Export the English portion of an approved Personal Statement Markdown file to DOCX."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Pt


SCHOOL_ALIASES = {
    "the chinese university of hong kong, shenzhen": "CUHKSZ",
    "the chinese university of hong kong": "CUHK",
    "the university of hong kong": "HKU",
    "the hong kong university of science and technology": "HKUST",
    "nanyang technological university": "NTU",
    "national university of singapore": "NUS",
}

DEGREE_WORDS = {
    "master", "science", "of", "program", "programme", "in", "the",
    "arts", "business", "engineering", "degree", "msc", "m", "sc",
}


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            result[key.strip()] = value.strip().strip("'\"")
    return result


def body_text(text: str) -> str:
    return re.sub(r"^---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)


def english_body_text(text: str) -> str:
    """Return source content before the first Chinese section heading."""
    body = body_text(text)
    lines = []
    for line in body.splitlines():
        stripped = line.strip()
        if re.match(r"^#{1,2}\s+", stripped):
            heading = re.sub(r"^#{1,2}\s+", "", stripped)
            if re.search(r"[\u3400-\u9fff]", heading):
                break
        lines.append(line)
    return "\n".join(lines)


def words(value: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", value)


def acronym(value: str) -> str:
    kept = [word for word in words(value) if word.lower() not in DEGREE_WORDS]
    return "".join(word[0].upper() for word in kept) or "PS"


def school_abbreviation(target: str, override: str | None) -> str:
    if override:
        return override.upper()
    lowered = target.lower()
    for name, alias in sorted(SCHOOL_ALIASES.items(), key=lambda item: -len(item[0])):
        if name in lowered:
            return alias
    match = re.search(r"\b(CUHK|HKU|HKUST|NTU|NUS|CUHKSZ)\b", target, re.I)
    if match:
        return match.group(1).upper()
    raise ValueError("Cannot determine school abbreviation; pass --school-abbr.")


def programme_abbreviation(target: str, override: str | None) -> str:
    if override:
        return override.upper()
    cleaned = re.sub(
        r"\b(the chinese university of hong kong(?:, shenzhen)?|the university of hong kong|"
        r"the hong kong university of science and technology|nanyang technological university|"
        r"national university of singapore|cuhk|hku|hkust|ntu|nus)\b",
        " ", target, flags=re.I,
    )
    result = acronym(cleaned)
    if result == "PS":
        raise ValueError("Cannot determine programme abbreviation; pass --program-abbr.")
    return result


def verified_student_abbreviation(source: Path, student: str, override: str | None) -> str:
    character_count = len(re.findall(r"[\u3400-\u9fff]", student))

    def validate_initials(value: str) -> str:
        value = value.strip().upper()
        if not re.fullmatch(r"[A-Z]+", value):
            raise ValueError("Student initials must contain only Latin letters.")
        if character_count and len(value) != character_count:
            raise ValueError("Chinese name initials must include one initial per name character.")
        return value

    if override:
        return validate_initials(override)
    if re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", student):
        return "".join(part[0] for part in student.split() if part).upper()
    basic_dir = source.parent.parent / "Basic_Info"
    for path in sorted(basic_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if character_count:
            explicit = re.search(r"(?:姓名缩写|Name Initials)\s*[：:][ \t]*([A-Za-z]+)", text, re.I)
            if explicit:
                return validate_initials(explicit.group(1))
            for match in re.finditer(r"拼音\s*[：:][ \t]*([A-Za-z]+(?:[ \t'-]+[A-Za-z]+)*)", text):
                syllables = re.split(r"[ \t'-]+", match.group(1).strip())
                if len(syllables) == character_count:
                    return validate_initials("".join(part[0] for part in syllables))
            continue
        for pattern in (
            r"拼音\s*[：:]\s*([A-Za-z]+(?:\s+[A-Za-z]+)+)",
            r"English Name\s*[：:]\s*([A-Za-z .'-]+)",
        ):
            match = re.search(pattern, text, re.I)
            if match:
                value = match.group(1).strip()
                return "".join(part[0] for part in re.split(r"\s+", value) if part).upper()
    raise ValueError("Cannot determine full student initials; provide per-character pinyin or verified --student-abbr.")


def next_word_version(folder: Path, identity: str) -> int:
    pattern = re.compile(rf"^{re.escape(identity)}-V(\d+)\.docx$", re.I)
    versions = [
        int(match.group(1))
        for path in folder.glob("*.docx")
        if (match := pattern.match(path.name))
    ]
    return max(versions, default=0) + 1


def match_student_folder(output_root: Path, student: str) -> Path:
    if not output_root.is_dir():
        raise ValueError(f"Student output folder does not exist: {output_root}")
    exact = output_root / student
    if exact.is_dir():
        return exact
    folded = [path for path in output_root.iterdir() if path.is_dir() and path.name.casefold() == student.casefold()]
    if len(folded) == 1:
        return folded[0]
    available = ", ".join(sorted(path.name for path in output_root.iterdir() if path.is_dir()))
    if not folded:
        raise ValueError(f"No matching student folder for {student!r} under {output_root}. Available: {available or '(none)'}")
    raise ValueError(f"Multiple matching student folders for {student!r} under {output_root}.")


def add_paragraph(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = Pt(0)
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    paragraph.paragraph_format.space_after = Pt(12)
    run = paragraph.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(12)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "STSong")


def build_docx(source: Path, output: Path) -> None:
    text = source.read_text(encoding="utf-8")
    document = Document()
    normal = document.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(12)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "STSong")
    normal.paragraph_format.first_line_indent = Pt(0)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    normal.paragraph_format.space_after = Pt(12)

    for line in english_body_text(text).splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^#{1,2}\s+", stripped):
            continue
        add_paragraph(document, stripped)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-root", type=Path, default=Path.home() / "Desktop" / "26Fall申请")
    parser.add_argument("--target", help="Target school/program text when source Markdown has no target frontmatter")
    parser.add_argument("--school-abbr")
    parser.add_argument("--program-abbr")
    parser.add_argument("--student-abbr")
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.is_file() or source.suffix.lower() != ".md":
        raise SystemExit("Source must be an existing Markdown file.")
    if "Personal_Statement" not in source.parts:
        raise SystemExit("Source must be inside a student's Personal_Statement directory.")
    raw = source.read_text(encoding="utf-8")
    if re.search(r"\[待(?:补充|确认)", raw):
        raise SystemExit("Source contains unresolved placeholders.")

    meta = parse_frontmatter(raw)
    ps_index = source.parts.index("Personal_Statement")
    student = meta.get("student") or source.parts[ps_index - 1]
    target = meta.get("target", "") or args.target or ""
    if not target:
        raise SystemExit("Missing target in frontmatter; pass --school-abbr and --program-abbr.")

    school = school_abbreviation(target, args.school_abbr)
    program = programme_abbreviation(target, args.program_abbr)
    student_key = verified_student_abbreviation(source, student, args.student_abbr)
    identity = f"PS-{school}-{program}-{student_key}"
    folder = match_student_folder(args.output_root.expanduser().resolve(), student)
    version = next_word_version(folder, identity)
    output = folder / f"{identity}-V{version}.docx"
    build_docx(source, output)
    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        raise SystemExit(str(exc))
