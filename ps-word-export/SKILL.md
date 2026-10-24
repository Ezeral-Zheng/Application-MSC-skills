---
name: ps-word-export
description: Export the English portion of an already-generated, approved Personal Statement Markdown file to a versioned Word document in the Desktop 26Fall申请 folder matched to the student's name. Use only for Personal Statement Word output, never for writing or revising the PS, resumes, or recommendation letters.
---

# Personal Statement Word Export

## Scope

This skill only converts an existing formal Personal Statement `.md` into a `.docx`. It does not draft, revise, fact-check, or publish the Markdown PS. The Markdown remains the source of truth.

## Required input and preconditions

1. Identify the student and the exact formal PS Markdown source. Use the latest formal `Vn` for the requested target; do not use an internal `Rn` candidate, review packet, or a file containing unresolved placeholders.
2. Confirm that the source is in the student's `Personal_Statement/` directory and has passed the Application-MSC review gates. If the source, student, target, or final review status cannot be established, stop and report the missing input.
3. Read the source frontmatter and filename. The target school and programme must be available from the frontmatter, filename, or the user's explicit input. Do not invent an abbreviation when the target is ambiguous.
4. For Chinese student names, read `Basic_Info/*.md` for verified pinyin or an explicit `姓名缩写` / `Name Initials` field. Construct one initial for every character in the applicant's full Chinese name, including every character of a compound surname. Do not substitute an English nickname or take initials only from whitespace-separated pinyin words. If grouped pinyin cannot be reliably separated into one syllable per character, use a verified `--student-abbr` or ask; do not guess or emit incomplete initials.

## Output location

Use this exact directory structure:

```text
~/Desktop/26Fall申请/<学生姓名>/<Word 文件>
```

Read the student name from the source Markdown frontmatter when available; otherwise use the student directory immediately above `Personal_Statement/`. Match that name to an existing student directory directly under `~/Desktop/26Fall申请/`. Do not silently create a new student directory or save into a similarly named folder. The Word file must not be saved into the student's Vault `Personal_Statement/` directory. Do not delete or overwrite any existing Word file.

## Filename and abbreviation contract

Use the readable compact form:

```text
PS-<学校缩写>-<专业缩写>-<学生姓名缩写>-V<n>.docx
```

Examples: `PS-CUHK-IC-XL-V1.docx`, `PS-HKU-ECLT-ZXT-V2.docx`.

- `PS` is fixed.
- School abbreviations should use the official/common abbreviation: CUHK, HKU, HKUST, NTU, NUS, CUHKSZ, etc.
- Programme abbreviations should use the supplied or established programme abbreviation; otherwise use the meaningful-word initials after removing degree boilerplate such as `Master`, `MSc`, `Master of Science`, `Program`, `in`, and `of`.
- Student initials are the uppercase initials of the applicant's complete name, in name order. For Chinese names, take the initial of each character's verified pinyin syllable: 陈星雨 = Chen Xing Yu = `CXY`, never `CX`; 欧阳娜娜 = Ou Yang Na Na = `OYNN`. A spelling such as `chen xingyu` has a joined given name, so whitespace-token initials are incomplete. The script accepts verified per-character pinyin, an explicit full-name initials field, or `--student-abbr CXY`; it rejects a Chinese abbreviation whose length does not match the name's character count. For a non-Chinese name, include every name component's initial.
- The Word version is independent of the Markdown `Vn`. Scan only the selected student's desktop folder for matching `.docx` files with the same `PS-school-program-student` identity key. If none exists, use `V1`; otherwise use the highest matching Word version plus one.
- If a filename collision remains after scanning, increment the Word version rather than overwriting.

## Word formatting contract

The generated document must contain only the approved English PS body paragraphs. Do not add a title, section heading, student name, school name, programme name, metadata, signature, or any other content. Use:

- Body font: Calibri.
- Body size: 小四, 12 pt.
- Paragraph first-line indent: none.
- Paragraph spacing: one blank-line equivalent after each body paragraph.
- Line spacing: 1.5 lines.
- Paragraph alignment: Word “Justified” alignment (`两端对齐`), using `WD_ALIGN_PARAGRAPH.JUSTIFY` (OOXML `w:jc="both"`). Ordinary lines align to both margins; the paragraph's final line stays naturally left aligned. Do not use `DISTRIBUTE` (`分散对齐`) or stretch the final line.
- Stop at the Chinese section heading (normally `# 个人陈述｜中文对照`) and exclude the Chinese text and heading.
- No invented title, facts, headings, or paragraph content beyond light document formatting.

Use `scripts/export_ps_docx.py` for deterministic conversion. Resolve the bundled workspace Python runtime through `load_workspace_dependencies`; do not rely on a system Python or repo-local package installation.

## Execution sequence

1. Create a task-specific temporary directory for QA artifacts.
2. Immediately before the first DOCX creation command, run the documents skill's artifact-operation marker once:

```bash
<bundled-node> container_tools/mark_artifact_operation_started.mjs \
  --operation-kind create --expected-output-count 1 --output-format docx
```

3. Run the exporter with the exact source Markdown and the desktop output root. Pass explicit abbreviations when automatic derivation is ambiguous.
4. Render the generated DOCX using the bundled documents skill `render_docx.py`, inspect every rendered page image, and fix/re-export if there is clipping, missing glyphs, broken paragraph spacing, wrong font, stretched paragraph-final lines, or accidental Chinese-section content. Verify normal two-margin alignment and naturally left-aligned final lines; also confirm paragraph alignment is `JUSTIFY`, not `DISTRIBUTE`, in the DOCX.
5. Verify that the final file exists at `~/Desktop/26Fall申请/<学生姓名>/`, that its filename follows the contract, and that an existing Word file was not overwritten.
6. Report only the final Word path and the Word version. Do not expose QA intermediates unless the user asks.

## Command

```bash
<bundled-python> Application_System/skills/ps-word-export/scripts/export_ps_docx.py \
  --source '<学生>/Personal_Statement/<正式PS>.md' \
  --output-root "$HOME/Desktop/26Fall申请" \
  [--target '学校与专业全称'] [--school-abbr HKUST] [--program-abbr IC] [--student-abbr CXY]
```

The optional overrides are preferred when the programme has a non-obvious abbreviation or the source materials contain multiple names.

## Blocking conditions

- The source is not a formal approved PS Markdown file.
- The source contains `[待补充]`, `[待确认]`, or unresolved review placeholders.
- Student, school, programme, or verified student initials cannot be determined.
- The bundled DOCX runtime or renderer is unavailable.
- The output cannot be written to the requested Desktop folder.
