---
name: resume-word-generator
description: Turn a student's Application-MSC materials into a verified, structured English resume Markdown source and a polished reference-style Word (.docx) output. Use when the user asks to generate a resume in Word, convert profile information into resume bullets, apply a resume template, or create a target-specific resume from existing materials.
---

# Resume Word Generator

## Purpose

Use this skill when the requested deliverable is a structured resume plus a Word document. The Markdown resume is the factual source of truth; the DOCX is a presentation layer generated from that approved Markdown. Never invent a metric, title, date, course, tool, responsibility, award, or project result to improve the layout.

This skill composes with:

- `student-material-normalizer` for converting source files to Markdown;
- `resume-experience-writer` for turning `Course_Info/` projects into reusable English project bullets;
- `resume-writer` or `targeted-one-page-resume-writer` for content selection and tailoring;
- `application-review` for fact and structure review;
- the documents skill and `Application_System/tools/export_resume_docx.py` for DOCX generation and rendering QA.

## Required workflow

1. Identify the student, resume purpose/target, and output location. If the user provides a Word example, inspect it before drafting. Use `Resume.doc` as a layout reference only; never copy its facts or wording.
2. Run or confirm material normalization. Read `.md` sources first: `Student_Profile/学生偏好总结.md`, `Student_Profile/Task_Board.md`, `Basic_Info/`, `Resume/`, `Course_Info/`, and relevant `Additional_Documents/*.md`. Preserve original attachments.
3. If project bullets are needed and there is no latest passing `Resume_Experience/*.md`, run `resume-experience-writer` first. It must convert all sufficiently documented Course_Info projects without target-based deletion; target selection happens later.
4. Build a private evidence matrix for candidate education, internships, research, projects, awards, and skills. Each item must record source file, verified facts, intended resume section, target capability, and keep/compress/omit decision.
5. Draft the complete English resume in Markdown. Use action-led bullets with the pattern `action + object/method + result or decision value`. Prefer 2–4 bullets per selected experience, retain supported numbers and tools, and omit unsupported filler. Keep dates, titles, organization names, and course names traceable to source materials.
6. Review the Markdown with `application-review`. If it is not `Pass`, revise an internal `Rn` candidate and review again; do not publish a formal version until facts and structure pass.
7. Export the passing Markdown to DOCX with the shared exporter:

   ```bash
   python3 Application_System/tools/export_resume_docx.py \
     '<学生>/Resume/<学生>-<用途>-Resume-Vn.md' \
     '<学生>/Resume/<学生>-<用途>-Resume-Vn.docx' \
     --render
   ```

   Use a task-specific `mktemp -d` directory for intermediate Rn files, render PNGs, and PDFs. Only copy the final DOCX to the formal `Resume/` directory when the user requested Word output.
8. Inspect every rendered page. If there is overflow, a blank page, clipped text, unstable date alignment, or an unreadable density, return to the Markdown candidate first. Adjust content selection or wording before modest typography/spacing changes; never fix DOCX layout by silently adding or changing facts.
9. After all checks pass, save exactly one new formal `Vn` Markdown version and the requested DOCX. Update the task board, `Review_History/`, `Revision_History/`, and `Application_System/indexes/Version_Index.md` according to the parent Application-MSC instructions.

## Word layout contract

The default style is the supplied reference resume: A4 portrait with approximately 1.27 cm margins; centered name; optional centered contact line; uppercase section headings; body text in a readable serif font; organization/school/project names bold; roles and project types italic; dates in a stable right column; and no decorative blank rows.

The header and Education block follow this order when the facts exist:

1. Name
2. Phone and email, omitted entirely if both are unavailable
3. `EDUCATION`
4. Horizontal rule
5. School, location/country on the left; expected graduation on the right
6. Degree/major
7. GPA and ranking
8. Relevant coursework

For each available experience module, use `MODULE TITLE → horizontal rule → entries`. The supported module titles are `INTERNSHIP EXPERIENCE`, `RESEARCH EXPERIENCE`, `COURSE EXPERIENCE`, and `PROJECT EXPERIENCE`; omit a module when it has no verified entries. Each entry has a split first row (name and role on the left, date on the right) followed by a full-width content row. Course entries should use the latest passing `Resume_Experience` bullets where available. Use real Word tables for alignment, not runs of spaces or tabs. See `references/reference-layout.md` for the tokens and QA thresholds.

The reference is a visual contract, not a content template. Do not copy its sentences, projects, employers, metrics, or section contents into a student's resume.

## Content decisions

- For a generic resume, select the strongest verified experiences and preserve chronological clarity.
- For a target-specific resume, use the program's actual requirements and change at least three of evidence order, selected experiences, bullet emphasis, course selection, skills grouping, or capability signal.
- Education should include only confirmed degree, institution, dates, GPA/ranking, relevant coursework, and awards. Do not infer formal course names from project topics.
- If a source mentions an attachment, read its matching Markdown conversion before using the fact.
- If critical identity, education, target, dates, or responsibilities are missing or contradictory, mark the task `Blocked` and list the missing facts rather than guessing.

## Version and output rules

- Reserve the next formal version once by scanning the exact student + purpose key with `next_version_path.py`.
- Internal candidates use `R1`, `R2`, etc. only in the task temp directory. They are not formal outputs or user-facing links.
- Formal output: `Resume/<稳定key>-Resume-Vn.md`; optional Word output uses the same stable key and `Vn`.
- Never overwrite an existing formal Markdown or DOCX.
- The DOCX must contain the same approved content as Markdown. Formatting-only iteration does not increment `Vn`.

## Final acceptance checklist

- Markdown and DOCX text match item by item.
- All facts trace to student materials or the user's current message.
- `application-review` is `Pass`.
- DOCX renders successfully; every page is inspected.
- No clipped text, overlapping elements, blank trailing page, broken date column, or leftover placeholder.
- The final response links only the formal Markdown and requested DOCX, not internal candidates or review artifacts.
