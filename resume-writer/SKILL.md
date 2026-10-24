---
name: resume-writer
description: Generate a target-specific English resume from an Application-MSC student folder, prioritizing experience type and verified evidence while reproducing a supplied reference Word layout and optionally exporting a verified DOCX.
---

# Resume Writer

Use this skill when the user wants a student's folder converted into a professional resume for a specific application program, especially when a Word resume is supplied as a visual reference. The student's Markdown materials are the factual source of truth. The reference document supplies layout only; never copy its people, employers, dates, metrics, wording, or template residue.

## Required inputs

Identify the student, target program or use, page constraint, and reference file. If the target program is missing, ask before selecting evidence. Read Markdown first in this order:

1. `Student_Profile/学生偏好总结.md`
2. `Student_Profile/Task_Board.md`
3. `Student_Profile/资料完整性检查.md`
4. `Basic_Info/*.md`
5. `Resume/*.md`
6. `Course_Info/*.md`
7. the latest passing `Resume_Experience/*.md`
8. relevant `Additional_Documents/*.md`
9. `Major Selected/` and target-program material

Use `student-material-normalizer` when the source Markdown is missing or stale. If a source names an attachment, read the matching Markdown conversion before using the fact. Preserve all original attachments.

## Storage paths

- Skill instructions and references: `Application_System/skills/resume-writer/`.
- Formal Markdown and, only when Word is explicitly requested, formal DOCX: `<学生目录>/Resume/`.
- Formal filename: `<学生名>-<目标专业或用途>-Resume-Vn.md` and, when requested, the matching `.docx`; do not add date prefixes.
- Internal `R1`, `R2` candidates, fact-review packets, render PNGs, and temporary DOCX files: a task-specific directory created with `mktemp -d`; never place them in the student directory or formal history folders.
- Review report: `<学生目录>/Review_History/`.
- Revision summary: `<学生目录>/Revision_History/`.
- Confirmed resume facts: `<学生目录>/Student_Profile/Resume_Fact_Confirmations.md`.
- Task status: `<学生目录>/Student_Profile/Task_Board.md`.
- Global version index: `Application_System/indexes/Version_Index.md`.

The Markdown file is the factual source of truth. The DOCX is a presentation layer generated from that Markdown and must match it item by item.

## Mandatory one-page Word gate

When a Word resume is generated, it must render as exactly one A4 page and the selected content must fill the page to a professional, readable density, normally reaching the lower 90% of the usable page. A one-page count alone is not sufficient; more than approximately 10% unused usable height or a conspicuous bottom blank area is a hard failure.

- Do not deliver a page with a large unused lower half or conspicuous gaps between a section heading, rule, table, and its content.
- Do not create whitespace with empty paragraphs, empty cells, fixed-height rows, unnecessary page breaks, oversized headings, or decorative elements.
- Every table row must contain real content. Reuse the first paragraph in a cell instead of leaving an empty default paragraph before the first bullet. Experience metadata and bullet cells must use zero or near-zero vertical cell padding, zero paragraph-before/after spacing, and automatic row height.
- A two-column metadata row is permitted only when a verified date exists. If an education or experience item has no date, its metadata must be rendered as one full-width cell; never leave an empty right-hand date cell.
- Education has a fixed two-row contract when the facts exist: the school/location row places attendance dates (`YYYY.MM–Present`) on the right, and the degree/major row places expected graduation (`Expected Month YYYY`) on the right. The degree/major row must use a formal degree-first format such as `Bachelor of Engineering in Computer Science and Technology`; translate a verified undergraduate major into this format when the degree type is established, and ask if it is not. Do not mention the school/department/college in the degree row. Do not include class rank or ranking anywhere in the resume. GPA, coursework, and awards remain full-width rows below; never leave either right-side date cell empty.
- The education date column must be wide enough for `Expected Month YYYY` to remain readable without an artificial line break; adjust the column split before shrinking or dropping verified education facts.
- A section rule must sit directly above its first content row, and an entry title/role row must sit directly above its first bullet. Any visible gap larger than the normal line height is a layout failure.
- If the page is sparse, return to the evidence matrix and add the next strongest verified experience, result, award, or skill, then use modest reference-compatible typography or line-spacing adjustments if needed. Do not accept a document merely because it is one page, and do not leave a large bottom blank area. If it is too dense, shorten repetition or remove the lowest-value item before reducing readability.
- Render the final DOCX and inspect the entire page. If it fails the one-page or density gate, the task remains incomplete and the DOCX must not be delivered.

## Workflow

The available section architecture is:

`EDUCATION → INTERNSHIP EXPERIENCE → COMPETITION EXPERIENCE → RESEARCH EXPERIENCE → PROJECT EXPERIENCE`

The last four sections are separate optional experience families, not mandatory slots. Select only the families and entries that produce the strongest target-specific one-page resume. If strong internships and competition entries already fill the page, omit `PROJECT EXPERIENCE`; do not add a weaker project merely to preserve the module list. Do not collapse competition or research into `PROJECT EXPERIENCE`, and do not place competition awards only in `SKILLS`.

Every entry under `COMPETITION EXPERIENCE` must explicitly state the verified award level and competition result in the entry title or a bullet (for example, `Second Prize` or `Third Prize`). If the award level cannot be verified, do not classify the entry as Competition Experience; ask for confirmation or move it to the appropriate non-award family.

1. Build a private evidence matrix. For every candidate education item, internship, award, research/project, activity, and skill, record its source, verified facts, dates, role, personal contribution, result, evidence tier, target capability, and decision.
2. Apply the selection order in [selection-policy.md](references/selection-policy.md). First build a target-program matching judgment for every candidate experience, identifying the capability, technical area, and evidence each item contributes. Then apply the family priority—internship first, competition and research next, project last—while allowing strong target fit and evidence strength to determine the final combination. Select optional sections and entries together; omit weaker families when higher-value evidence already fills the page.
3. Classify uncertain facts using [fact-confirmation.md](references/fact-confirmation.md). Ask one consolidated set of human questions after the initial scan. Do not write `Likely`, `Missing`, or `Conflicting` facts into the resume. If an unresolved fact affects a required date, title, award, contribution, or result, pause and wait for confirmation; otherwise omit it and continue.
4. Draft an internal Markdown candidate (`R1`, then `R2` if needed) in a task-specific `mktemp -d` directory. Use concise action-led bullets: `action + object/method + result or value`. Keep each target resume materially differentiated through evidence order, selected experiences, bullet emphasis, course selection, or skills grouping.
5. Run `application-review`. Revise only internal candidates until facts and structure pass. Follow the parent Application-MSC rules for isolated external review when required. Do not place internal candidates or review packets in formal student directories.
6. Export the passing Markdown to Word using `resume-word-generator`, `Application_System/tools/export_resume_docx.py`, or the approved document runtime. Apply [reference-layout.md](references/reference-layout.md). If the user supplied a `.doc`/`.docx`, inspect it before drafting and treat it as a visual contract, not a content template.
7. Render the Word file and inspect every page. Check exact one-page count, lower-page density, font fallback, margins, section headings, date alignment, line wrapping, clipping, blank pages, table borders, and gaps caused by empty paragraphs/cells. Fix content selection or Markdown first; never silently add facts in Word.
8. Reserve exactly one formal `Vn` at task start using `next_version_path.py`. Publish only after review and visual QA. Save the formal Markdown in `Resume/`; save the formal `.docx` there only when Word output is requested. Update `Task_Board.md`, `Review_History/`, `Revision_History/`, and `Application_System/indexes/Version_Index.md` according to the parent instructions.

## Fact confirmation interaction

Questions must be concrete and grouped. For each question state the discovered conflict or gap, why it affects the resume, and what will happen without an answer. Typical questions concern internship dates, official company names, award level, whether a result is team-level or personal, and whether the student led or supported a task. Record confirmed answers in a student-local Markdown fact-confirmation file so later target resumes do not ask again.

## Output contract

The user-facing deliverable is the formal Word resume and the essential confirmation/blocking note. The formal Markdown remains the hidden factual source and must match the Word item by item. Never expose internal `Rn` candidates, review packets, scoring, or handoff material unless the user explicitly asks about the process.

## Blocking conditions

Block rather than guess when the student, target, education, required date, role, award, personal contribution, or requested result cannot be established. Also block if the reference layout cannot be rendered reliably or a one-page requirement would require unreadable typography.

## Composition

Compose with:

- `resume-writer` for factual resume writing;
- `targeted-one-page-resume-writer` for target selection and one-page QA;
- `resume-experience-writer` for incomplete course-project evidence;
- `application-review` and, where required, `external-application-review`;
- `resume-word-generator` and the documents skill for Word generation and rendering.
