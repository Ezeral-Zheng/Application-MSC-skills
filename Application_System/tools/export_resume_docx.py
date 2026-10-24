#!/usr/bin/env python3
"""Export a structured resume Markdown file to the compact reference DOCX layout.

The Markdown file remains the source of truth. This exporter is intentionally
small and deterministic: it supports the Resume-Experience/Resume conventions
used by Application-MSC and writes a presentation-layer DOCX only.
"""

from __future__ import annotations

import argparse
import os
import os
import re
import subprocess
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


# Candidate-specific density scaling keeps a one-page resume visually filled
# without inserting artificial blank paragraphs or oversized section gaps.
FONT_SCALE = 1.0


ENTRY_RE = re.compile(r"^\*\*(?P<title>.+?)\*\*(?:\s*\|\s*(?P<subtitle>.*))?$")
DATE_RE = re.compile(r"(?:\d{4}[./-]\d{1,2}(?:[./-]\d{1,2})?|Present|至今).*")
DATE_ATOM = (
    r"Expected\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ .]*\d{4}"
    r"|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[ .]*\d{4}"
    r"|\d{4}[./-]\d{1,2}(?:[./-]\d{1,2})?|(?<![A-Za-z0-9])\d{4}(?![A-Za-z0-9])|Present|至今"
)
DATE_FINDER_RE = re.compile(rf"(?:{DATE_ATOM})(?:\s*[–—-]\s*(?:{DATE_ATOM}))?", re.IGNORECASE)


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge in kwargs:
            tag = "w:" + edge
            element = borders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                borders.append(element)
            for key in ["val", "sz", "space", "color"]:
                if key in kwargs[edge]:
                    element.set(qn("w:" + key), str(kwargs[edge][key]))


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=30, start=60, bottom=30, end=60):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    margins = tc_pr.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        tc_pr.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn("w:" + side))
        if node is None:
            node = OxmlElement("w:" + side)
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_font(run, size=11, bold=False, italic=False):
    # The supplied reference resume is a serif, English-first layout. Set all
    # font slots explicitly so Word and LibreOffice do not choose unrelated
    # CJK defaults for ASCII text.
    run.font.name = "Times New Roman"
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.rFonts
    rfonts.set(qn("w:ascii"), "Times New Roman")
    rfonts.set(qn("w:hAnsi"), "Times New Roman")
    rfonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(round(size * FONT_SCALE, 1))
    run.bold = bold
    run.italic = italic


def find_date(text: str) -> str:
    match = DATE_FINDER_RE.search(text)
    return match.group(0).strip() if match else ""


def remove_date_from_text(text: str, date: str) -> str:
    if not date:
        return text
    cleaned = text.replace(date, "")
    cleaned = re.sub(r"\s*\|\s*\|\s*", " | ", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned.strip(" |")


def paragraph(cell_or_doc, text="", align=None, before=0, after=0, line=1.0):
    p = cell_or_doc.add_paragraph() if hasattr(cell_or_doc, "add_paragraph") else cell_or_doc.paragraphs[0]
    if p.text:
        p = cell_or_doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if text:
        r = p.add_run(text)
        set_font(r)
    return p


def add_rule(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = Pt(1)
    p.paragraph_format.line_spacing_rule = None
    p.paragraph_format.keep_with_next = True
    p_pr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "666666")
    borders.append(bottom)
    p_pr.append(borders)


def parse_markdown(path: Path):
    lines = path.read_text(encoding="utf-8").splitlines()
    name = ""
    contact = ""
    sections = []
    current = None
    entry = None
    pagebreak_before_next = False
    in_frontmatter = False
    frontmatter_checked = False
    for raw in lines:
        line = raw.strip()
        if line == "---" and not frontmatter_checked:
            in_frontmatter = True
            frontmatter_checked = True
            continue
        if in_frontmatter:
            if line == "---":
                in_frontmatter = False
            continue
        if line == "<!-- pagebreak-before -->":
            pagebreak_before_next = True
            continue
        if not line or line.startswith("---") or line.startswith("<!--"):
            continue
        if line.startswith("# "):
            name = line[2:].strip()
            continue
        if line.startswith("Contact:") or line.startswith("联系方式:"):
            contact = line.split(":", 1)[1].strip()
            continue
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "items": [], "bullets": [], "pagebreak_before": pagebreak_before_next}
            sections.append(current)
            entry = None
            pagebreak_before_next = False
            continue
        if current is None:
            if not contact and not line.startswith("-"):
                contact = line
            continue
        if line.startswith("### "):
            # Targeted resume Markdown uses level-three headings for entries.
            # Preserve them as distinct employer/project rows in Word.
            content = line[4:].strip()
            parts = [part.strip() for part in content.split("|")]
            title = parts.pop(0) if parts else content
            subtitle = " | ".join(parts)
            date = ""
            if parts and DATE_RE.match(parts[-1].strip("* ")):
                date = parts.pop().strip()
                subtitle = " | ".join(parts)
            if not date:
                inline_date = find_date(subtitle)
                if inline_date:
                    date = inline_date
                    subtitle = remove_date_from_text(subtitle, inline_date)
            entry = {"title": title, "subtitle": subtitle, "date": date, "bullets": [], "details": []}
            current["items"].append(entry)
            continue
        m = ENTRY_RE.match(line)
        if m:
            # Education commonly uses a school line followed by a bold degree
            # line. Keep those as one two-row entry instead of creating a
            # second empty table with a large artificial gap.
            if current["title"].upper() == "EDUCATION" and entry and not entry["bullets"] and not entry.get("details"):
                detail = line
                date = find_date(detail)
                if date and not entry["date"]:
                    entry["date"] = date
                # Preserve an expected-graduation date in the education detail
                # so it can be placed in the degree row's right-hand column.
                entry.setdefault("details", []).append(detail)
                continue
            subtitle = m.group("subtitle") or ""
            date = ""
            # Accept both the canonical three-line form and compact entries
            # such as `**Company** | *Role* | 2026.03 - 2026.06`.
            parts = [part.strip() for part in subtitle.split("|")]
            if len(parts) > 1 and DATE_RE.match(parts[-1].strip("* ")):
                date = parts.pop().strip()
                subtitle = " | ".join(parts)
            if not date:
                inline_date = find_date(subtitle)
                if inline_date:
                    date = inline_date
                    subtitle = remove_date_from_text(subtitle, inline_date)
            entry = {"title": m.group("title"), "subtitle": subtitle, "date": date, "bullets": [], "details": []}
            current["items"].append(entry)
            continue
        if entry and line.startswith("*") and line.endswith("*"):
            entry["subtitle"] = line.strip("*")
            continue
        if entry:
            inline_date = find_date(line)
            if inline_date and (DATE_RE.match(line) or line.strip("* ") == inline_date):
                entry["date"] = inline_date
                continue
        if entry and line.startswith("-"):
            if current["title"].upper() == "EDUCATION":
                entry.setdefault("details", []).append(line[1:].strip())
            else:
                entry["bullets"].append(line[1:].strip())
        elif entry and line:
            entry.setdefault("details", []).append(line)
        elif line.startswith("-"):
            current["bullets"].append(line[1:].strip())
        elif normalized_section_title(current["title"]) in {"SKILLS", "OTHER"} and line:
            current["bullets"].append(line)
    return name, contact, sections


def normalized_section_title(title: str) -> str:
    value = title.lower()
    if "education" in value or "教育" in value:
        return "EDUCATION"
    if "intern" in value or "实习" in value or "work experience" in value:
        return "INTERNSHIP EXPERIENCE"
    if "research" in value or "科研" in value:
        return "RESEARCH EXPERIENCE"
    if "competition" in value or "竞赛" in value:
        return "COMPETITION EXPERIENCE"
    if "course" in value or "academic" in value or "课程" in value:
        return "COURSE EXPERIENCE"
    if "skill" in value or "computer" in value or "技能" in value:
        return "SKILLS"
    if "other" in value:
        return "OTHER"
    if "project" in value or "项目" in value:
        return "PROJECT EXPERIENCE"
    return title.upper()


def education_detail_rows(details):
    """Normalize education lines while excluding class-rank details."""
    degree, performance, coursework, extras = [], [], [], []
    for detail in details:
        parts = [part.strip() for part in detail.split("|") if part.strip()]
        for part in parts:
            lower = part.lower()
            if "rank" in lower or "ranking" in lower:
                # Ranking is intentionally excluded from all resumes.
                continue
            if "gpa" in lower:
                performance.append(part)
            elif "coursework" in lower or "relevant course" in lower or "课程" in lower:
                coursework.append(part)
            elif any(token in lower for token in ("undergraduate", "bachelor", "b.eng", "master", "degree", "学士", "硕士")):
                degree.append(part)
            else:
                extras.append(part)
    expected = [part for part in extras if "expected" in part.lower() or "毕业" in part]
    extras = [part for part in extras if part not in expected]
    if degree and expected:
        # Keep expected graduation attached to the degree row so the
        # exporter can place it in that row's right-hand date column.
        degree[-1] = degree[-1] + " | " + expected[0]
    return degree + performance + coursework + extras


def add_rich_text(p, text, size=10):
    # Markdown emphasis is intentionally limited to bold/italic, matching the template.
    token_re = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")
    pos = 0
    for match in token_re.finditer(text):
        if match.start() > pos:
            r = p.add_run(text[pos:match.start()]); set_font(r, size)
        token = match.group(0)
        r = p.add_run(token.strip("*"))
        set_font(r, size, bold=token.startswith("**"), italic=not token.startswith("**"))
        pos = match.end()
    if pos < len(text):
        r = p.add_run(text[pos:]); set_font(r, size)


def export(input_path: Path, output_path: Path):
    global FONT_SCALE
    name, contact, sections = parse_markdown(input_path)
    content_chars = sum(
        len(item.get("title", "")) + len(item.get("subtitle", ""))
        + sum(len(b) for b in item.get("bullets", []))
        + sum(len(d) for d in item.get("details", []))
        for sec in sections for item in sec.get("items", [])
    )
    # Increase type slightly only for genuinely sparse candidates; denser
    # candidates stay at the reference size to preserve a single page.
    # Keep a readable compact base size; the higher line spacing gives the
    # selected evidence vertical presence without inserting blank gaps.
    FONT_SCALE = float(os.environ.get("RESUME_FONT_SCALE", 1.08 if content_chars < 2400 else 1.0))
    # A pipeline run may apply a modest, reviewable scale adjustment after
    # content selection to keep a long, fully evidenced resume on one A4 page.
    # The caller remains responsible for render and density QA.
    requested_scale = os.environ.get("RESUME_FONT_SCALE")
    if requested_scale:
        FONT_SCALE = float(requested_scale)
    doc = Document()
    normal = doc.styles["Normal"]
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    line_spacing = float(os.environ.get("RESUME_LINE_SPACING", 1.36 if content_chars < 2400 else 1.22))
    normal.paragraph_format.line_spacing = line_spacing
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    for attr in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(section, attr, Cm(1.0 if attr in ("top_margin", "bottom_margin") else 1.27))
    # Let Word/LibreOffice distribute modest vertical whitespace across a
    # genuinely short one-page resume instead of leaving the content stranded
    # at the top. This is presentation-only; the Markdown remains the source.
    sect_pr = section._sectPr
    v_align = sect_pr.find(qn("w:vAlign"))
    if v_align is None:
        v_align = OxmlElement("w:vAlign")
        sect_pr.append(v_align)
    v_align.set(qn("w:val"), "both")

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run(name or input_path.stem); set_font(r, 22, bold=True)
    if contact:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(contact); set_font(r, 10)
    for sec in sections:
        section_title = normalized_section_title(sec["title"])
        if sec.get("pagebreak_before"):
            doc.add_page_break()
        heading = doc.add_paragraph(); heading.paragraph_format.space_before = Pt(1); heading.paragraph_format.space_after = Pt(0); heading.paragraph_format.keep_with_next = True
        r = heading.add_run(section_title); set_font(r, 12, bold=True)
        # Reference structure: section title sits above its divider line.
        add_rule(doc)
        if section_title == "EDUCATION":
            for item in sec["items"]:
                details = education_detail_rows(item.get("details", []))
                education_rows = []
                for detail in details:
                    detail_date = find_date(detail)
                    detail_text = remove_date_from_text(detail, detail_date) if detail_date else detail
                    if detail_date and ("expected" in detail.lower() or "毕业" in detail):
                        if detail_text.strip():
                            # A degree row may carry its expected graduation
                            # date inline: keep both parts on the same row.
                            education_rows.append([detail_text, detail_date])
                        elif education_rows:
                            education_rows[-1][1] = detail_date
                    else:
                        education_rows.append([detail_text, ""])
                table = doc.add_table(rows=1 + len(education_rows), cols=2 if item["date"] else 1)
                table.alignment = WD_TABLE_ALIGNMENT.LEFT
                table.autofit = False
                # Education needs a slightly wider right column so the
                # expected-graduation label stays readable on one line.
                table.columns[0].width = Cm(14.7 if item["date"] else 18.7)
                if item["date"]:
                    table.columns[1].width = Cm(4.0)
                left = table.rows[0].cells[0]
                right = table.rows[0].cells[1] if item["date"] else None
                for cell in ([left, right] if right is not None else [left]):
                    set_cell_margins(cell, top=0, bottom=0); set_cell_border(cell, top={"val":"nil"}, left={"val":"nil"}, bottom={"val":"nil"}, right={"val":"nil"})
                    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                p = left.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
                r = p.add_run(item["title"]); set_font(r, 10.5, bold=True)
                if item["subtitle"]:
                    add_rich_text(p, " | " + item["subtitle"], size=10.5)
                if right is not None:
                    p = right.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; p.paragraph_format.space_after = Pt(0)
                    r = p.add_run(item["date"]); set_font(r, 10.5)
                for row, (detail_text, detail_date) in zip(table.rows[1:], education_rows):
                    if item["date"] and detail_date:
                        left_detail, right_detail = row.cells
                        for cell in (left_detail, right_detail):
                            set_cell_margins(cell, top=0, bottom=0); set_cell_border(cell, top={"val":"nil"}, left={"val":"nil"}, bottom={"val":"nil"}, right={"val":"nil"})
                            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                        p = left_detail.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
                        add_rich_text(p, detail_text, size=10.5)
                        p = right_detail.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; p.paragraph_format.space_after = Pt(0)
                        r = p.add_run(detail_date); set_font(r, 10.5)
                    else:
                        cell = row.cells[0].merge(row.cells[1]) if item["date"] else row.cells[0]
                        set_cell_margins(cell, top=0, bottom=0); set_cell_border(cell, top={"val":"nil"}, left={"val":"nil"}, bottom={"val":"nil"}, right={"val":"nil"})
                        p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
                        add_rich_text(p, detail_text, size=11)
            continue
        if section_title == "OTHER":
            # The reference layout uses a single full-width cell for compact
            # skills/other content; there is no date column in this module.
            for item in sec["items"]:
                table = doc.add_table(rows=1, cols=1)
                table.alignment = WD_TABLE_ALIGNMENT.LEFT
                table.autofit = False
                table.columns[0].width = Cm(18.7)
                cell = table.cell(0, 0)
                set_cell_margins(cell, top=0, bottom=0, start=45, end=45)
                set_cell_border(cell, top={"val":"nil"}, left={"val":"nil"}, bottom={"val":"nil"}, right={"val":"nil"})
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
                r = p.add_run(item["title"]); set_font(r, 10.5, bold=True)
                if item["subtitle"]:
                    add_rich_text(p, " | " + item["subtitle"], size=10.5)
                for detail in item.get("details", []):
                    p = cell.add_paragraph(); p.paragraph_format.space_after = Pt(0)
                    add_rich_text(p, detail, size=10.5)
            continue
        for item in sec["items"]:
            # Each experience is a two-row table:
            # row 1 = left metadata / right date; row 2 = one merged content cell.
            table = doc.add_table(rows=2, cols=2 if item["date"] else 1)
            table.alignment = WD_TABLE_ALIGNMENT.LEFT
            table.autofit = False
            table.columns[0].width = Cm(14.0 if item["date"] else 18.7)
            if item["date"]:
                # Keep month-range dates on one line; the wider right column
                # is more readable than forcing a second-line year.
                table.columns[1].width = Cm(4.7)
            left = table.rows[0].cells[0]
            right = table.rows[0].cells[1] if item["date"] else None
            content = table.rows[1].cells[0].merge(table.rows[1].cells[1]) if item["date"] else table.rows[1].cells[0]
            for cell in ([left, right, content] if right is not None else [left, content]):
                set_cell_margins(cell, top=0, bottom=0, start=45, end=45); set_cell_border(cell, top={"val":"nil"}, left={"val":"nil"}, bottom={"val":"nil"}, right={"val":"nil"})
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            p = left.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            r = p.add_run(item["title"]); set_font(r, 10.5, bold=True)
            if item["subtitle"]:
                add_rich_text(p, " | " + item["subtitle"], size=10.5)
            if right is not None:
                p = right.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; p.paragraph_format.space_after = Pt(0)
                r = p.add_run(item["date"]); set_font(r, 11)
            for index, bullet in enumerate(item["bullets"]):
                p = content.paragraphs[0] if index == 0 else content.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.2); p.paragraph_format.first_line_indent = Cm(-0.2); p.paragraph_format.space_after = Pt(0)
                add_rich_text(p, "· " + bullet)
            for detail in item.get("details", []):
                p = content.paragraphs[0] if not item["bullets"] and not content.paragraphs[0].text else content.add_paragraph()
                p.paragraph_format.space_after = Pt(0)
                add_rich_text(p, detail, size=10.5)
        if sec["bullets"]:
            table = doc.add_table(rows=1, cols=1)
            table.autofit = False
            table.columns[0].width = Cm(18.7)
            cell = table.cell(0, 0)
            set_cell_margins(cell)
            set_cell_border(cell, top={"val":"nil"}, left={"val":"nil"}, bottom={"val":"nil"}, right={"val":"nil"})
            for index, bullet in enumerate(sec["bullets"]):
                p = cell.paragraphs[0] if index == 0 else cell.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.2); p.paragraph_format.first_line_indent = Cm(-0.2); p.paragraph_format.space_after = Pt(0)
                add_rich_text(p, "· " + bullet)
    # Tables carry their own paragraphs and do not always inherit the Normal
    # style in LibreOffice, so apply the same density rule to every rendered
    # paragraph before saving.
    all_paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)
    for p in all_paragraphs:
        p.paragraph_format.line_spacing = line_spacing
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path, help="Resume Markdown source")
    ap.add_argument("output", type=Path, help="DOCX output path")
    ap.add_argument("--render", action="store_true", help="Render DOCX to PNGs with the bundled document renderer")
    args = ap.parse_args()
    export(args.input, args.output)
    if args.render:
        render_candidates = sorted(
            (Path.home() / ".codex/plugins/cache/openai-primary-runtime/documents").glob("*/skills/documents/render_docx.py"),
            reverse=True,
        )
        render = render_candidates[0] if render_candidates else None
        python = (Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3")
        if render is None or not render.is_file():
            raise FileNotFoundError(f"document renderer not found: {render}")
        out_dir = Path(tempfile.mkdtemp(prefix="resume-docx-qa-"))
        subprocess.run([str(python), str(render), str(args.output), "--output_dir", str(out_dir)], check=True)
        print(out_dir)


if __name__ == "__main__":
    main()
