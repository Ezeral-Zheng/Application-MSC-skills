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
