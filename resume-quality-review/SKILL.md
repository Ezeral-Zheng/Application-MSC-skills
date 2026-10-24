---
name: resume-quality-review
description: Score a target-specific resume after factual and format approval, checking professional quality, target-program fit, evidence selection, clarity, and one-page composition before Word delivery.
---

# Resume Quality Review

Use this skill only after `application-review` has returned `Pass` for the current resume candidate. It is the second gate in the resume pipeline. It evaluates quality and selection, not whether facts are true; every factual concern must be returned to the first gate.

## Review input

Read only:

1. the current internal resume candidate;
2. the target program or resume purpose;
3. the target-matching evidence matrix;
4. the approved factual boundary or first-gate report;
5. the rendered DOCX when Word output is requested.

Do not invent facts while scoring. Do not directly edit the resume.

## Six scoring dimensions

Score each dimension from 0 to 10 and provide evidence-based comments:

1. **Target fit** — selected experiences and bullets support the target program's technical capabilities and address its evidence needs.
2. **Selection and priority** — the resume applies `Internship > Competition > Research > Project` while allowing materially stronger fit or evidence to override a weaker item; optional sections are used deliberately.
3. **Evidence density** — bullets contain concrete actions, methods, tools, responsibilities, metrics, awards, or outcomes rather than generic claims.
4. **Personal contribution and distinctiveness** — the resume clearly separates individual work from team results and presents a recognizable capability profile without repeated project wording.
5. **Language and structure** — headings, entry order, action verbs, bullet length, tense, grammar, and section architecture are concise and professional.
6. **One-page composition** — the selected evidence forms a balanced, readable page with no large bottom blank area, no crowded block, stable dates, and a layout consistent with the reference Word file.

For Word output, this dimension is also a hard technical gate: the rendered
output must have exactly one page and pass
`Application_System/tools/check_resume_density.py --min-ratio 0.90`. A
single-page result that fails the density script is `Revise`, regardless of
the subjective score.

## Pass threshold

`Pass` requires:

- average score `>= 8.5`;
- no dimension below `7.5`;
- no `P0` or `P1` quality issue;
- no required factual or format correction left unresolved.

Otherwise return `Revise`. If a missing fact prevents a quality judgment, return `Needs Confirmation` for the specific item and send it to the first gate; do not silently assume it.

## Quality issue format

Return a concise report with:

```text
status: Pass | Revise | Needs Confirmation
round: Q1-Q5
scores:
  target_fit: n.n
  selection_priority: n.n
  evidence_density: n.n
  contribution_distinctiveness: n.n
  language_structure: n.n
  one_page_composition: n.n
average: n.n
issues:
  - id: RQ-001
    priority: P0 | P1 | P2
    location: section / entry / bullet
    problem: ...
    impact: ...
    requested_action: ...
    acceptance_test: ...
```

P0 means the resume cannot be delivered; P1 means a substantial selection, target-fit, or composition problem; P2 means a useful but non-blocking refinement. A `Pass` cannot contain unresolved P0/P1 issues.

## Revision handoff

When status is `Revise`, the main pipeline converts accepted issues into a clean handoff for `application-revision`. The handoff contains only the current candidate, issue IDs and actions, the minimum approved facts, and acceptance tests. It must not include scores, reviewer reasoning, old candidates, or unrelated history. The revised candidate must pass `application-review` again before the next quality review.

Quality review is limited to five rounds (`Q1` through `Q5`) for one requested deliverable. If Q5 still fails, do not publish the reserved formal version; report the unresolved quality issues and any required user decision.
