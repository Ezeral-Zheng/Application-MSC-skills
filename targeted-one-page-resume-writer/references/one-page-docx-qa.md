# One-Page DOCX QA

## Hard Checks

- exactly one rendered page;
- no content on a hidden or blank second page;
- no clipped final line, date, bullet, or skill list;
- no overlapping text or section rule;
- course line is stable and readable;
- all selected Markdown content appears in the DOCX.

## Density Check

Page count alone is insufficient. Inspect the rendered page visually. If the final content ends around the middle of the page, return to the evidence matrix and add the next strongest verified experience or result. Do not add a decorative box, oversized heading, or unsupported claim merely to occupy space.

The final page must normally reach the lower 90% of the usable area at readable density; more than approximately 10% unused usable height is a failure. Reject conspicuous gaps between a section heading/rule and its content, or a large unused lower half. Empty paragraphs, empty cells, fixed-height rows, unnecessary page breaks, and decorative spacing are not permitted as layout fixes.

For table-based resume layouts, inspect every entry boundary: the first title line must connect directly to the first bullet, and section rules must connect directly to the first content row. Reusing the first cell paragraph is required; a default empty paragraph before bullets is a defect. Use zero or near-zero vertical cell padding and automatic row heights.

Only entries with a verified date may use a split title/date row. Undated education and project entries must use one full-width metadata cell; an empty date cell is a layout defect.

Education must be checked separately: attendance dates belong on the right of the school row, and expected graduation belongs on the right of the degree/major row. The degree/major row must be degree-first (for example, `Bachelor of Engineering in Computer Science and Technology`) and must not mention a school, department, or college. Class rank/ranking is excluded. Do not leave `Expected ...` as a left-aligned full-width detail when a right-side second-row date can be rendered.

For every `COMPETITION EXPERIENCE` entry, verify that the award level and result are explicitly written in that entry; a competition title without its prize is a format/content failure.

If the page overflows, use this order:

1. remove repeated context and weak adjectives;
2. combine bullets that describe the same action;
3. remove the lowest-value retained item;
4. make modest margin, spacing, or font adjustments;
5. rerender and inspect again.

## Recommended Verification Commands

Use the installed office runtime and PDF tools where available:

```bash
soffice --headless --convert-to pdf --outdir /tmp/qa path/to/resume.docx
pdfinfo /tmp/qa/resume.pdf | awk '/Pages:/ {print $2}'
pdftoppm -png -f 1 -singlefile /tmp/qa/resume.pdf /tmp/qa/page
```

Open the resulting PNG for visual inspection. A successful `Pages: 1` check does not replace the visual inspection.
