# Reference Word layout contract

Use the supplied reference document as a visual contract. Inspect it first; do not assume its text is factual or that its empty fields are required.

## Default visual mapping

- A4 portrait with the reference's measured margins; use approximately 1.27 cm only when measurement is unavailable.
- Centered, bold name at the top.
- Black-and-white English-first typography, normally Times New Roman unless the reference proves otherwise.
- Uppercase section headings with the same underline/rule treatment as the reference.
- School, company, and project names bold; roles and project types italic where the reference does so.
- Dates in a stable right-aligned column, implemented with real Word tables rather than spaces or tabs.
- Body bullets and wrapped lines use the reference's indentation and spacing.
- Preserve natural page breaks. Do not force one page by using unreadable text or deleting high-tier evidence without recording the decision.

## Content mapping

Typical mapping from the supplied two-page reference:

```text
EDUCATION
INTERNSHIP EXPERIENCE
COMPETITION EXPERIENCE
RESEARCH EXPERIENCE
PROJECT EXPERIENCE or PROGRAM EXPERIENCE
SKILLS
```

Rename or omit modules when the student's evidence requires it. Competition awards belong in `COMPETITION EXPERIENCE` and must not be represented only as an `Awards` line under `SKILLS`. Template residue such as blank GPA fields, placeholder award text, unsupported companies, or copied sentences must never appear in the output.

## QA requirements

After export, render every page and check:

- page count and intended density;
- no clipped, overlapped, or missing text;
- no blank trailing page;
- dates remain aligned after wrapping;
- headings, underlines/rules, bold/italic emphasis, and bullet indentation match the reference;
- fonts have not silently substituted into an unreadable or visually different fallback;
- Markdown and Word text match item by item.

If a visual mismatch is caused by content length, revise the Markdown selection or wording first. Formatting-only changes may adjust spacing, column widths, and typography but must not add facts or alter approved content.
