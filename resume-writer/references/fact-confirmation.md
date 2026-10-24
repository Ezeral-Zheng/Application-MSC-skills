# Human fact confirmation protocol

Use this reference whenever the evidence matrix contains `Likely`, `Missing`, or `Conflicting` facts.

## Statuses

| Status | Meaning | Resume action |
|---|---|---|
| `Confirmed` | Explicitly supported by a source or the user's answer | Usable |
| `Likely` | Plausible but not sufficiently supported | Ask |
| `Missing` | Required field has no value | Ask or omit |
| `Conflicting` | Sources disagree | Show conflict and ask |
| `Unsupported` | Appears only in a reference/template or has no student source | Do not use |

## When to pause

Pause before drafting if uncertainty affects identity, school/degree, target, internship date, official role/company name, award level, personal contribution, or a numeric result. If an uncertainty is nonessential, omit the detail and continue.

## Question format

Ask a consolidated set after the scan. Each question should include:

- the fact found or missing;
- why it changes the resume;
- the exact answer needed;
- the fallback if the user cannot confirm.

Example:

```text
诚迈科技资料已确认公司、岗位和工作内容，但没有实习时间。日期是经历标题的必要字段，请补充起止年月；如果暂时无法确认，我会暂不把这段经历放入正式简历。
```

Do not ask for information that will not affect selection or wording. Do not present a speculative answer as a choice unless the source supports both alternatives.

## Persistence

After the user confirms facts, append them to a student-local Markdown file such as `Student_Profile/Resume_Fact_Confirmations.md` with:

```yaml
- fact: ""
  value: ""
  source: "user confirmation"
  confirmed_at: "YYYY-MM-DD"
  usable_for: [resume]
```

Preserve earlier entries. A later explicit user correction supersedes an earlier confirmation but does not delete the history.
