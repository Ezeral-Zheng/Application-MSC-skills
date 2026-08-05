---
name: personal-statement-workflow
description: Orchestrate a fact-safe, differentiated, independently reviewed personal statement workflow for a student and target programme. Use when generating, substantially revising, or quality-gating an application PS/SOP, especially when the student has multiple target programmes or prior statements.
---

# Personal Statement Workflow

Use this skill as the process controller around writing and revising a PS/SOP. Keep internal candidates and review packets in one task-specific temporary directory; expose only the final validated version.

## Required sequence

1. Identify the student, target school/programme, prompt, word limit, language, and task type. Scan the target output directory and reserve exactly one next formal `Vn`; never increment `Vn` for internal revisions.
2. Normalize source materials so Markdown is authoritative. Read the student preference summary, task board, narrative matrix, personalization materials, basic/course/resume materials, target-programme information, relevant attachment Markdown, and each other target's latest formal PS. If personalization materials are empty, create a clearly labeled candidate/confirmation file before drafting; never upgrade an unconfirmed detail into fact.
3. Update the narrative matrix before prose. Define one core proposition, current problem, causal path, evidence duties, required/optional/discarded evidence, capability gap, career direction, programme-fit function, structure signature, and semantic-delta cards for reused experiences.
4. Draft internal `R1`: English first and Chinese second in one Markdown file, normally 500–1000 English words, as continuous prose. Do not force a six-paragraph template, equal-length experience sections, a fixed GPA paragraph, or a resume dump. The target programme must change the problem, evidence function, and capability conclusion—not only the final programme-fit paragraph.
5. Run the five-dimension writing self-check, then run the factual/compliance gate. `Pass` proceeds; `Needs Fix` creates another internal `Rn` using only traceable facts; `Blocked` stops for missing or conflicting facts. Factual repair may add at most three internal rounds.
6. After factual `Pass`, start a brand-new context-isolated reviewer in `single-draft` mode. It scores seven dimensions: logic, experience/programme fit, language, distinctiveness, motivation, school/programme fit, and career plan. It must output a report, not edit the draft.
7. Publish only when the average is at least 8.5, there is no P0/Must Fix or actionable P1/Should Fix, the course-listing check passes, and factual review is `Pass`. Otherwise, the controller selects actionable issues, converts them into a sanitized handoff plus minimum fact packet, and starts a different isolated revision worker. The worker sees only the current draft, accepted issues, minimum facts, and output requirements; it returns the next `Rn` and a disposition table.
8. Re-run factual review after every revision, then use a new isolated reviewer for the next `Cn`. Allow at most `C1`–`C5`; content and factual counters are independent. Do not pass prior scores, reports, old drafts, or reasoning to the next reviewer.
9. If other target PSs exist, run a separate isolated `portfolio-differentiation` review using only the current draft, narrative matrix, latest PS per other target, and similarity report. Any substantive rewrite returns to factual review and a new single-draft review without resetting the `C` counter.
10. When all gates pass, copy the last internal candidate once to the reserved formal `Vn` Markdown path. Only then write formal review/history/memory/summary records, update the task board and preference memory when justified, and refresh the version index.

## Hard stops

- Do not invent facts, programme resources, courses, people, dates, results, or career claims.
- Do not publish drafts containing `[待确认]`, `[待补充]`, or equivalent placeholders.
- Do not expose or store `Rn`, `Cn`, scores, review packets, or internal reasoning in formal student directories.
- If isolation cannot be created, facts conflict, critical inputs are missing, or `C5` still fails, stop as `Blocked` and report the exact missing decision or evidence.

For detailed gates, isolation rules, issue handoff fields, and output contracts, read [references/workflow-contract.md](references/workflow-contract.md).
