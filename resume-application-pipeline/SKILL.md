---
name: resume-application-pipeline
description: Unified Application-MSC resume workflow. Normalize student materials, convert course projects into verified Resume-Experience, tailor a Markdown resume to a target program, review it, and optionally export and visually verify a one-page Word resume.
---

# Resume Application Pipeline

Use this as the single mandatory entry point when a user asks to create, tailor, revise, or export a resume. Do not deliver a resume by calling only a focused writer or Word exporter. It orchestrates the focused skills in this repository:

- `resume-experience-writer`: converts sufficiently documented `Course_Info` projects into reusable English project bullets.
- `resume-writer`: builds the complete factual Markdown resume.
- `targeted-one-page-resume-writer`: applies target-program selection and strict one-page density rules.
- `resume-word-generator`: exports the approved Markdown to Word and performs rendering QA.
- `application-review`: performs the first facts-and-format gate.
- `resume-quality-review`: performs the second scored quality gate.
- `application-revision`: revises failed candidates and sends them back through both gates.

The Markdown resume is always the content source of truth. A DOCX is an optional presentation layer and must never become the place where facts are invented or silently changed. This pipeline has two ordered gates: `application-review` for facts and format, followed by `resume-quality-review` for quality. A candidate cannot enter the second gate until the first gate passes.

## Trigger and deliverable decision

Use this pipeline for any of the following requests:

- create or update an English resume or CV;
- write separate resumes for different programs;
- tailor a resume to a program's characteristics;
- make the resume occupy exactly one page;
- apply a Word reference format or output a `.docx`.

Before drafting, identify:

1. the student;
2. the resume purpose or target program;
3. whether the output is generic, target-specific, one-page, Markdown-only, or Word;
4. any supplied template, transcript, attachment, or user-confirmed fact.

If the target or output constraints are unclear, use the strongest reasonable interpretation from the user's request and record the assumption in the task notes.

## Required source order

Read Markdown sources first and preserve original attachments:

1. `Student_Profile/学生偏好总结.md`
2. `Student_Profile/Task_Board.md`
3. `Student_Profile/资料完整性检查.md`
4. `Basic_Info/*.md`
5. `Resume/*.md`
6. `Course_Info/*.md`
7. the latest passing `Resume_Experience/*.md`
8. relevant `Additional_Documents/*.md`
9. `Major Selected/` and official target-program notes when available
10. user-provided Word or Markdown reference files, as layout references only

When a source names an attachment, read the matching Markdown conversion in `Additional_Documents/`. If the conversion is missing, mark the fact as unavailable instead of using an unverified detail.

## End-to-end workflow (mandatory; no step may be skipped)

### 1. Normalize and establish the evidence boundary

Confirm that the student's source materials are standardized and that `.md` is the working source. Separate every candidate fact into:

- verified and usable;
- verified but too incomplete for a bullet;
- conflicting or awaiting confirmation.

Do not improve the resume by guessing a metric, course title, job title, date, tool, responsibility, or result.

### 2. Build reusable Resume-Experience

If `Course_Info/` contains projects without a latest passing Resume-Experience output, hand off to `resume-experience-writer` first. That skill converts all sufficiently documented projects without target-based deletion and records omitted projects with reasons.

The pipeline may reuse a passing Resume-Experience file, but target selection happens later. Do not delete a course project merely because it is not relevant to the current program.

### 3. Build the target profile and evidence matrix

For a target-specific resume, use `targeted-one-page-resume-writer`'s selection method. Internally record at least:

| Item | Source | Verified fact | Target capability | Value | Decision |
|---|---|---|---|---|---|

The target must materially change at least three of course selection, experience selection, bullet emphasis, evidence order, skill grouping, or capability signal. First write a target-matching judgment for every candidate experience. Then apply `Internship > Competition > Research > Project`, modified by evidence strength, personal contribution, outcome intensity, and target fit. Select optional experience families and entries together; do not add a weaker project merely to preserve a module. Select by evidence strength and space value, not by generic relevance language.

For a generic resume, preserve the strongest verified experiences and chronological clarity. For one-page output, rank content before reducing typography.

### 4. Draft an internal Markdown candidate

Use `resume-writer` for the base resume and add the target-specific constraints when applicable. Draft `R1`, `R2`, etc. in a task-specific temporary directory created with `mktemp -d`; do not place internal candidates in the student's formal output directory.

Every bullet should be concise and action-led, preferably:

`action + object or method + result or decision value`

Keep names, dates, titles, course names, tools, metrics, and roles traceable. A one-page resume should normally use this section order unless the target evidence justifies another order:

1. Education
2. Internship / Work Experience
3. Research Experience
4. Course / Project Experience
5. Skills and honors when supported

### 5. First gate: factual and format review

Run `application-review` on the current internal Markdown candidate. This gate checks source traceability, names, dates, roles, contributions, metrics, awards, section classification, education rules, version rules, and Markdown structure. If it is not `Pass`, prepare a clean issue list and generate the next internal `Rn` through `application-revision`; never increment the formal version for internal revisions. A `Blocked` result requires user confirmation. Do not start quality scoring before this gate passes.

### 6. Second gate: quality review and revision loop

After the factual and format gate passes, run `resume-quality-review`. Score target fit, selection and priority, evidence density, personal contribution and distinctiveness, language and structure, and one-page composition. The quality gate passes only when the average is at least `8.5`, no dimension is below `7.5`, and no P0/P1 issue remains.

If quality returns `Revise`, accept or reject each issue, create a clean revision handoff, and use `application-revision` to generate the next internal candidate. The new candidate must return to `application-review`, then `resume-quality-review`. Do not pass scores, old candidates, or reviewer reasoning to the modifier. Count quality rounds Q1-Q5; after Q5 failure, do not publish. For resume quality, this loop replaces the PS-specific external content review; do not apply PS scoring rules to a resume.

For target-specific resumes, confirm that the selection is genuinely differentiated from other target versions. For one-page resumes, confirm that the page is readable and content-balanced rather than merely compressed.

### 7. Export Word only after both gates pass

When Word is requested, hand off to `resume-word-generator` after the Markdown candidate passes review. Use the shared exporter and a task-specific temporary directory for intermediates:

```bash
python3 Application_System/tools/export_resume_docx.py \
  '<学生>/Resume/<稳定key>-Resume-Vn.md' \
  '<学生>/Resume/<稳定key>-Resume-Vn.docx' \
  --render
```

Inspect every rendered page for:

- exactly one page when one-page output is required;
- no blank trailing page, clipping, overlap, or broken bullet;
- stable dates, headings, rules, and contact line;
- readable font size and balanced lower-page density;
- a course line that stays on one line when required.

Then run the hard density gate on the rendered PNG directory:

```bash
python3 Application_System/tools/check_resume_density.py '<render-dir>' --min-ratio 0.90 --json
```

The gate passes only when there is exactly one page and dark content pixels
reach at least 90% of the rendered page height in the central page area. A
failure is a quality `Revise` result: return to target selection and Markdown
revision, then rerun both review gates and Word rendering. Do not publish a
one-page document that merely avoids overflow while leaving a conspicuous
bottom blank area.

If rendering fails or the visual density check fails, return to the Markdown candidate through the quality revision loop first. Formatting-only fixes do not add facts or change the formal version; after any change, rerun both gates.

### 8. Publish one formal version

At the beginning of the task, scan the exact student + purpose key and reserve one next `Vn`. Publish only after all required reviews and, if requested, Word QA pass:

- `Resume/<稳定key>-Resume-Vn.md`
- `Resume/<稳定key>-Resume-Vn.docx` only when requested

Then update the task board, revision history, review history, and version index according to the parent Application-MSC instructions. Deliver only the formal version and essential conclusions, never internal `Rn` files or review handoff packets.

## Branch rules by request

### Generic resume

Use `resume-writer` with the strongest verified experiences. Keep the content broad enough for general use, but do not pad it with unsupported details.

### Target-specific resume

Use `resume-writer` plus `targeted-one-page-resume-writer`. Read the target program's actual focus and make the evidence matrix drive selection. Do not make separate target versions by changing only the title, skills line, or final bullet.

### One-page resume

Use the targeted one-page rules even when the user calls it a general resume. First shorten repetition and remove low-value content, then make modest layout adjustments. Never use unreadably small typography or decorative blank space to force pagination.

### Word resume

Use `resume-word-generator` after Markdown approval. Treat the reference Word file as a visual contract only; never copy its facts, sentences, employers, metrics, or project content.

## Blocking conditions

Stop and report the missing input when:

- the student's identity, education, or resume purpose cannot be established;
- a required source is empty, only a template, or unavailable;
- dates, titles, responsibilities, or metrics conflict and cannot be resolved;
- the target program is unknown for a requested tailored resume;
- one-page output would require unreadable typography;
- Word rendering cannot be completed or verified.

When blocked, list the exact missing facts or files. Do not fill the gap with plausible resume language.

## Completion checklist

- [ ] Source Markdown was read before original attachments.
- [ ] Course projects were converted or a documented reason was recorded for not doing so.
- [ ] Target-specific selection is supported by an evidence matrix.
- [ ] Markdown is the factual source of truth.
- [ ] Internal candidates use `Rn` in a task temporary directory.
- [ ] First gate `application-review` passed for the final candidate.
- [ ] Second gate `resume-quality-review` passed with average `>= 8.5`, no dimension below `7.5`, and no P0/P1.
- [ ] Any quality revision returned through `application-revision` and passed both gates again.
- [ ] DOCX was rendered and inspected when requested.
- [ ] Exactly one formal `Vn` was published.
- [ ] Task board, review history, revision history, and version index were updated as required.
