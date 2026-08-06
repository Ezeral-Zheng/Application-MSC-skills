---
name: targeted-one-page-resume-writer
description: Build separate, verified one-page resumes tailored to each target program, selecting courses and experiences from student materials and validating Markdown and DOCX pagination.
---

# Targeted One-Page Resume Writer

Use this skill when the user asks for separate resumes for different programs, asks to tailor a resume to a program's characteristics, or requires all selected content to occupy exactly one polished page. Use it with `resume-writer`; this skill adds program-specific selection and strict one-page visual QA.

## Core Rule

Each target program receives an independent resume. Do not create one generic resume and only change the title or skills line. The target must change at least three of: course selection, experience selection, bullet emphasis, evidence order, skill grouping, or capability conclusion.

## Required Inputs

Read these before writing:

1. `Student_Profile/学生偏好总结.md`
2. `Student_Profile/Task_Board.md`
3. `Basic_Info/*.md`
4. `Resume/*.md` and the latest passing `Resume_Experience/*.md`
5. Relevant `Course_Info/*.md`
6. `Major Selected/` and the target program's latest PS or official program notes when available
7. `Application_System/skills/resume-writer/references/resume-review-checklist.md`

If a source names an attachment, read its matching Markdown in `Additional_Documents/`. Do not use an unconverted attachment as the only factual basis for a bullet.

## Workflow

### 1. Reserve the version

- Build a stable key: `学生名-目标专业或用途-Resume`.
- Scan `Resume/` for the highest existing `Vn` for that exact target.
- Reserve one new formal version number for the whole task. Internal candidates use `R1`, `R2`, etc. in a task-specific temporary directory created with `mktemp -d`.
- Never overwrite a formal Markdown or DOCX version.

### 2. Build the target profile

Create a short internal profile with:

- program capabilities and likely selection signals;
- 3-5 relevant courses from the transcript;
- preferred experience families;
- evidence to foreground, compress, or omit;
- the candidate's likely capability gap or next-step rationale.

Use the program's actual focus. Examples:

- **MiM / management**: leadership, coordination, organization, operations, consumer or market decisions, project ownership.
- **Information systems / technology management**: technology-enabled workflows, data governance, systems thinking, digital products, process redesign, cross-functional implementation.
- **Financial technology**: quantitative finance, machine learning, financial data, audit/control, risk, infrastructure, technical implementation.

These are selection lenses, not facts. Never insert a course, tool, responsibility, or result merely because it sounds relevant.

### 3. Build the evidence matrix

For every candidate course or experience, record:

| Item | Source | Verified fact | Target capability | Value | Decision |
|---|---|---|---|---|---|

Rank items by direct relevance, evidence strength, distinctiveness, quantified outcome, and space cost. Prefer a smaller number of strong bullets over generic filler. If the page is sparse, add the next highest-value verified experience from the matrix, not an invented achievement.

### 4. Draft the Markdown first

Write the target-specific `.md` before any Word export. Preserve the existing resume's factual names, dates, metrics, and role titles unless the source clearly supports a correction. Every bullet should follow:

`action + object/method + result or decision value`

Use concise English resume bullets. Keep courses on one line when possible; if the target has five courses, shorten labels only when the transcript supports the shortened English name.

Recommended one-page order:

1. Contact and Education
2. Internship / Work Experience
3. Research Experience
4. Other / Project Experience
5. Computer Skills

Reorder sections if the target profile clearly gives another section higher evidentiary value.

### 5. Control page density

The requirement is not merely “PDF page count equals 1.” The selected content must form a complete, readable one-page resume with balanced use of the page.

- If content overflows: first shorten repetitive wording, then remove low-value bullets or the lowest-ranked experience; only then make modest typography changes.
- If content occupies substantially less than the page: add the next highest-value verified experience or an additional factually supported bullet; do not stretch empty space with decorative elements.
- Keep the final content readable. Do not reduce text to a tiny font just to force pagination.
- Aim for content to reach approximately the lower 80-90% of the usable page while preserving comfortable margins and whitespace.
- The course line must remain one line unless its length makes that impossible at a readable size.

### 6. Export and verify DOCX

When the user asks for Word, export from the approved Markdown using the local document runtime or a bundled template. Never add new facts while editing the Word file.

Verify the DOCX by conversion/rendering:

1. page count is exactly 1;
2. no blank second page, clipping, overlap, or broken bullet;
3. headings, dates, section rules, and contact line are readable;
4. the bottom of the content is not stranded in the upper half of the page unless the source genuinely lacks material;
5. the course line and longest skill line do not create unstable wrapping.

If any check fails, return to the Markdown candidate, revise, and render again. Do not silently deliver a Word-only correction.

### 7. Review and publish

- Run `application-review` against the final candidate for facts, direction match, wording, and layout risk.
- Fix any factual issue before publishing. Do not create a formal version until the review is Pass.
- Save the final Markdown to `Resume/`; save DOCX there only when requested.
- Add a concise `Review_History/` report and `Revision_History/` summary.
- Update `Student_Profile/Task_Board.md` and run `Application_System/tools/build_version_index.py --write`.
- Deliver only the final formal version and the essential conclusion, not internal `Rn` candidates.

## Failure Conditions

Stop or mark the task blocked when:

- the target program cannot be identified;
- the transcript or experience source is unavailable;
- a requested metric, title, date, or responsibility cannot be verified;
- fitting all verified content on one page would require unreadable typography;
- the requested output format cannot be rendered and checked.

In a blocked case, list the missing input rather than filling the page with unsupported content.

## Useful Resources

- [Program-fit and evidence matrix](references/program-fit-and-evidence-matrix.md)
- [One-page DOCX QA checklist](references/one-page-docx-qa.md)
- [Resume writer](../resume-writer/SKILL.md)
