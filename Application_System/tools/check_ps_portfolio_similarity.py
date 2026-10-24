#!/usr/bin/env python3
"""Check one PS against the student's latest formal PS portfolio."""

from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
import re
from pathlib import Path
from typing import Iterable


VERSION_RE = re.compile(r"(?i)(?:^|[-_ ])V(\d+)(?=[._ -]|$)")
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
ACADEMIC_BACKGROUND_RE = re.compile(
    r"\b(?:gpa|grade|ranking|ranked|undergraduate degree|bachelor'?s degree|"
    r"academic training|academic foundation|coursework|major(?:ed|ing)? in)\b",
    re.IGNORECASE,
)
CAREER_GOAL_RE = re.compile(
    r"\b(?:short[- ]term|long[- ]term|career|after graduation|professional goal|"
    r"aspire|hope to work|plan to (?:begin|work|pursue|become|join)|eventually)\b",
    re.IGNORECASE,
)
PROGRAM_FIT_RE = re.compile(
    r"\b(?:this (?:master'?s |msc )?program(?:me)?|the program(?:me)?|"
    r"program(?:me)? (?:offers|provides)|at (?:hku|cuhk|hkust)|curriculum|"
    r"will equip me|next step|master'?s study|graduate study)\b",
    re.IGNORECASE,
)
OPENING_TEMPLATE_PATTERNS = (
    ("interest-origin", re.compile(
        r"^(?:my|i\s+first)\s+(?:interest|curiosity|motivation|fascination)\b.*\bbegan\s+with\b",
        re.IGNORECASE,
    )),
    ("question-led", re.compile(r"\b(?:question|how|what)\b[^.!?]{0,180}\?", re.IGNORECASE)),
    ("anomaly-led", re.compile(
        r"\b(?:anomal(?:y|ies)|discrepanc(?:y|ies)|inflated|unexpected|inconsistent|abnormal)\b",
        re.IGNORECASE,
    )),
    ("scene-led", re.compile(
        r"^(?:during|at|while|when|halfway|after|before|the first time|in my)\b",
        re.IGNORECASE,
    )),
)
CONTENT_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "by",
    "for",
    "from",
    "i",
    "in",
    "into",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "one",
    "or",
    "our",
    "project",
    "that",
    "the",
    "this",
    "through",
    "to",
    "was",
    "we",
    "were",
    "when",
    "with",
    "work",
}


def version_number(path: Path) -> int:
    matches = VERSION_RE.findall(path.stem)
    return int(matches[-1]) if matches else -1


def application_key(path: Path) -> str:
    stem = DATE_PREFIX_RE.sub("", path.stem)
    stem = VERSION_RE.sub("", stem)
    return re.sub(r"[-_ ]+", "-", stem).strip("-").lower()


def target_identity(path: Path) -> str:
    """Prefer the document's target metadata so a draft is not compared with its own history."""
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^target:\s*(.+?)\s*$", text)
    if match:
        return re.sub(r"\s+", " ", match.group(1).strip()).casefold()
    return application_key(path)


def select_latest_versions(paths: Iterable[Path]) -> list[Path]:
    latest: dict[str, Path] = {}
    for path in sorted(paths, key=lambda item: item.name):
        if path.suffix.lower() != ".md" or version_number(path) < 0:
            continue
        key = application_key(path)
        current = latest.get(key)
        if current is None or version_number(path) > version_number(current):
            latest[key] = path
    return sorted(latest.values(), key=lambda item: item.name)


def extract_english_paragraphs(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    english_start = None
    for index, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+English(?:\s+Version)?\s*$", line.strip(), re.IGNORECASE):
            english_start = index + 1
            break
    if english_start is None:
        english_start = 0

    paragraphs: list[str] = []
    buffer: list[str] = []
    for line in lines[english_start:]:
        stripped = line.strip()
        if re.match(r"^#{1,6}\s+(?:中文|Chinese)", stripped, re.IGNORECASE):
            break
        if stripped.startswith("#"):
            continue
        if not stripped:
            if buffer:
                paragraphs.append(" ".join(buffer))
                buffer = []
            continue
        # Existing PS files commonly use one paragraph per line without blank lines.
        if buffer:
            paragraphs.append(" ".join(buffer))
            buffer = []
        paragraphs.append(stripped)
    if buffer:
        paragraphs.append(" ".join(buffer))
    return paragraphs


def tokens(text: str) -> list[str]:
    return [token.lower() for token in WORD_RE.findall(text)]


def shingles(text: str, size: int = 3) -> set[tuple[str, ...]]:
    words = tokens(text)
    if not words:
        return set()
    if len(words) < size:
        return {tuple(words)}
    return {tuple(words[index : index + size]) for index in range(len(words) - size + 1)}


def jaccard_similarity(left: str, right: str) -> float:
    left_set = shingles(left)
    right_set = shingles(right)
    if not left_set and not right_set:
        return 1.0
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / len(left_set | right_set)


def normalized_sentences(paragraphs: list[str]) -> set[str]:
    sentences: set[str] = set()
    for paragraph in paragraphs:
        for sentence in SENTENCE_RE.split(paragraph):
            normalized = " ".join(tokens(sentence))
            if len(normalized.split()) >= 8:
                sentences.add(normalized)
    return sentences


def paragraph_role(paragraph: str, index: int, total: int) -> str:
    """Return a coarse rhetorical role for portfolio-level structure warnings."""
    if index == 0:
        return "opening"
    if PROGRAM_FIT_RE.search(paragraph) and index >= max(1, total - 2):
        return "program-fit"
    if CAREER_GOAL_RE.search(paragraph):
        return "career-goal"
    if ACADEMIC_BACKGROUND_RE.search(paragraph):
        return "academic-background"
    return "experience"


def rhetorical_signature(paragraphs: list[str]) -> list[str]:
    return [
        paragraph_role(paragraph, index, len(paragraphs))
        for index, paragraph in enumerate(paragraphs)
    ]


def opening_template_family(opening: str) -> str:
    """Classify reusable opening rhetoric, not just shared vocabulary."""
    for family, pattern in OPENING_TEMPLATE_PATTERNS:
        if pattern.search(opening.strip()):
            return family
    return "event-or-claim-led"


def structural_similarity(left: list[str], right: list[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return SequenceMatcher(a=left, b=right, autojunk=False).ratio()


def content_tokens(text: str) -> set[str]:
    return {
        token
        for token in tokens(text)
        if token not in CONTENT_STOPWORDS and len(token) > 1
    }


def content_overlap(left: str, right: str) -> float:
    """Measure how much the shorter passage reuses the longer passage's content."""
    left_set = content_tokens(left)
    right_set = content_tokens(right)
    if not left_set or not right_set:
        return 0.0
    return len(left_set & right_set) / min(len(left_set), len(right_set))


def experience_candidates(paragraphs: list[str]) -> list[tuple[int, str]]:
    candidates: list[tuple[int, str]] = []
    for index, paragraph in enumerate(paragraphs):
        role = paragraph_role(paragraph, index, len(paragraphs))
        if role not in {"opening", "experience"} or len(tokens(paragraph)) < 35:
            continue
        candidates.append((index + 1, paragraph))
    return candidates


def best_experience_passage_match(
    target_paragraphs: list[str], previous_paragraphs: list[str]
) -> dict[str, object]:
    best: dict[str, object] = {
        "similarity": 0.0,
        "target_paragraph": None,
        "prior_paragraph": None,
    }
    for target_index, target_paragraph in experience_candidates(target_paragraphs):
        for prior_index, prior_paragraph in experience_candidates(previous_paragraphs):
            similarity = content_overlap(target_paragraph, prior_paragraph)
            if similarity > best["similarity"]:
                best = {
                    "similarity": round(similarity, 4),
                    "target_paragraph": target_index,
                    "prior_paragraph": prior_index,
                }
    return best


def structural_risk_reasons(item: dict[str, object]) -> list[str]:
    """Explain which full-text structural signals triggered the eighth dimension."""
    reasons: list[str] = []
    if item["opening_template_family_overlap"]:
        reasons.append("shared-non-neutral-opening-template-family")
    if (
        item["paragraph_count"] >= 5
        and item["prior_paragraph_count"] >= 5
        and item["structural_similarity"] >= 0.80
    ):
        reasons.append("same-paragraph-function-signature")
    if item["experience_passage_similarity"] >= 0.35:
        reasons.append("reused-experience-action-chain-signal")
    if item["reused_sentence_count"] >= 2:
        reasons.append("reused-non-factual-sentences")
    if item["early_narrative_similarity"] >= 0.55:
        reasons.append("same-early-narrative-skeleton")
    return reasons


def compare_pair(target: Path, previous: Path) -> dict[str, object]:
    target_paragraphs = extract_english_paragraphs(target)
    previous_paragraphs = extract_english_paragraphs(previous)
    target_opening = target_paragraphs[0] if target_paragraphs else ""
    previous_opening = previous_paragraphs[0] if previous_paragraphs else ""
    target_early = " ".join(target_paragraphs[:3])
    previous_early = " ".join(previous_paragraphs[:3])
    reused = normalized_sentences(target_paragraphs) & normalized_sentences(previous_paragraphs)
    target_signature = rhetorical_signature(target_paragraphs)
    previous_signature = rhetorical_signature(previous_paragraphs)
    target_opening_family = opening_template_family(target_opening)
    previous_opening_family = opening_template_family(previous_opening)
    experience_match = best_experience_passage_match(
        target_paragraphs, previous_paragraphs
    )
    result = {
        "path": str(previous),
        "opening_similarity": round(jaccard_similarity(target_opening, previous_opening), 4),
        "opening_template_family": target_opening_family,
        "prior_opening_template_family": previous_opening_family,
        "opening_template_family_overlap": (
            target_opening_family == previous_opening_family
            and target_opening_family != "event-or-claim-led"
        ),
        "early_narrative_similarity": round(jaccard_similarity(target_early, previous_early), 4),
        "reused_sentence_count": len(reused),
        "reused_sentences": sorted(reused),
        "paragraph_count": len(target_paragraphs),
        "prior_paragraph_count": len(previous_paragraphs),
        "rhetorical_signature": target_signature,
        "prior_rhetorical_signature": previous_signature,
        "structural_similarity": round(
            structural_similarity(target_signature, previous_signature), 4
        ),
        "experience_passage_similarity": experience_match["similarity"],
        "experience_passage_match": experience_match,
    }
    result["structural_risk_reasons"] = structural_risk_reasons(result)
    return result


def compare_target(
    target: Path,
    previous_files: Iterable[Path],
    opening_threshold: float = 0.65,
    early_threshold: float = 0.55,
    reused_sentence_threshold: int = 2,
    structural_threshold: float = 0.80,
    experience_passage_threshold: float = 0.35,
) -> dict[str, object]:
    target = target.resolve()
    target_identity_value = target_identity(target)
    comparisons = [
        compare_pair(target, previous.resolve())
        for previous in previous_files
        if previous.resolve() != target
        and target_identity(previous.resolve()) != target_identity_value
    ]
    flagged = [
        item
        for item in comparisons
        if item["opening_similarity"] >= opening_threshold
        or item["early_narrative_similarity"] >= early_threshold
        or item["reused_sentence_count"] >= reused_sentence_threshold
        or (
            item["paragraph_count"] >= 5
            and item["prior_paragraph_count"] >= 5
            and item["structural_similarity"] >= structural_threshold
        )
        or item["experience_passage_similarity"] >= experience_passage_threshold
        or item["opening_template_family_overlap"]
    ]
    dimension_8_status = "Revise" if flagged else "Pass"
    return {
        "target": str(target),
        "status": "Needs Differentiation" if flagged else "Pass",
        "dimension_8": {
            "name": "跨申请结构独立性与相似度",
            "status": dimension_8_status,
            "score": None,
            "evidence": [
                {
                    "prior_path": item["path"],
                    "reasons": item["structural_risk_reasons"],
                    "structural_similarity": item["structural_similarity"],
                    "rhetorical_signature": item["rhetorical_signature"],
                    "prior_rhetorical_signature": item["prior_rhetorical_signature"],
                }
                for item in flagged
            ],
            "note": "工具提供全文结构证据；最终分数由隔离组合审稿人依据叙事矩阵判定。",
        },
        "thresholds": {
            "opening_similarity": opening_threshold,
            "early_narrative_similarity": early_threshold,
            "reused_sentence_count": reused_sentence_threshold,
            "structural_similarity": structural_threshold,
            "experience_passage_similarity": experience_passage_threshold,
            "opening_template_family_overlap": True,
        },
        "comparison_count": len(comparisons),
        "flagged_count": len(flagged),
        "comparisons": comparisons,
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# PS Portfolio Similarity Check",
        "",
        f"- Target: `{report['target']}`",
        f"- Status: `{report['status']}`",
        f"- Compared documents: {report['comparison_count']}",
        f"- Flagged documents: {report['flagged_count']}",
        "",
        "| Prior PS | Opening | Template family | Early narrative | Structure | Experience passage | Reused sentences | Structure risks | Signatures |",
        "|---|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for item in report["comparisons"]:
        lines.append(
            f"| `{item['path']}` | {item['opening_similarity']:.2f} | "
            f"`{item['opening_template_family']}` / `{item['prior_opening_template_family']}` | "
            f"{item['early_narrative_similarity']:.2f} | "
            f"{item['structural_similarity']:.2f} | "
            f"{item['experience_passage_similarity']:.2f} "
            f"(P{item['experience_passage_match']['target_paragraph']}/"
            f"P{item['experience_passage_match']['prior_paragraph']}) | "
            f"{item['reused_sentence_count']} | "
            f"{', '.join(item['structural_risk_reasons']) or '—'} | "
            f"`{' -> '.join(item['rhetorical_signature'])}` / "
            f"`{' -> '.join(item['prior_rhetorical_signature'])}` |"
        )
    lines.extend(
        [
            "",
            f"Dimension 8 status: `{report['dimension_8']['status']}`; score is assigned by isolated portfolio review.",
            "Structural similarity compares coarse paragraph functions, not merely wording.",
            "A shared non-neutral opening template family is a differentiation warning even when lexical similarity is low.",
            "This tool supplies full-text structural evidence; it does not replace the isolated portfolio review or the narrative matrix.",
            "A flagged draft must be reviewed against the student's PS narrative matrix and cannot receive an automatic eighth-dimension Pass.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="PS draft to check.")
    parser.add_argument(
        "--portfolio-dir",
        type=Path,
        help="Directory containing the student's formal PS files. Defaults to target parent.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = args.target.resolve()
    if not target.exists():
        raise SystemExit(f"Target does not exist: {target}")
    portfolio_dir = (args.portfolio_dir or target.parent).resolve()
    formal_files = select_latest_versions(portfolio_dir.glob("*Personal-Statement*.md"))
    report = compare_target(target, formal_files)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
