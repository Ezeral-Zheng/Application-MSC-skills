# Reference Resume Layout

Use this when the user provides the supplied `Resume.doc` or asks for the same style.

## Tokens

- Page: A4 portrait; margins about 1.27 cm on all sides.
- Header: name centered, bold, about 22 pt; contact line centered, about 10 pt.
- Section heading: uppercase, bold, about 12 pt, with one short rule immediately below it.
- Body: readable serif font, normally 9.5–10 pt; do not shrink below 8.5 pt merely to force one page.
- Entry line: left column contains bold organization/project name and italic role/type; right column contains right-aligned date.
- Entry body: compact action-led paragraphs or bullets with natural wrapping and no fixed row height.
- Skills: final `OTHER` or `SKILLS` section with concise, source-supported tools.

## Content order

The first block is always name, optional contact, `EDUCATION`, a rule, then education facts in this order: school/location/date, degree, GPA/ranking, coursework. Missing fields are omitted without placeholder rows.

Experience is grouped flexibly into `INTERNSHIP EXPERIENCE`, `RESEARCH EXPERIENCE`, `COURSE EXPERIENCE`, and `PROJECT EXPERIENCE`. A group is omitted when empty. Each group starts with its heading and rule, followed by entries. Each entry has a split metadata/date row and a merged full-width content row.

## Structural implementation

Use a two-column Word table with exactly two rows for each dated entry: row 1 has metadata/name on the left and the date on the right; row 2 merges both columns into one full-width cell for the concrete experience content. Education may use additional merged detail rows for degree, GPA/ranking, and coursework. Set explicit widths and hidden cell borders. Use real paragraph formatting for bullets and real paragraph borders for section rules. Set `keep_with_next` for headings and entry titles where appropriate. Do not use spaces, tabs, text boxes, floating shapes, or fixed-height rows to fake alignment.

## Visual QA

Render with the documents skill's `render_docx.py` and inspect every PNG. Check page count, section headings, left/right alignment, date wrapping, font substitution, long bullets, bottom margin, and whether the final section is stranded on a new page. For a one-page request, page count must equal one; if readability would be compromised, stop and report the constraint instead of reducing the type below the minimum.
