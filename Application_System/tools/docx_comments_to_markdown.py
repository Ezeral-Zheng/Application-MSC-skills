#!/usr/bin/env python3
"""Convert a DOCX to Markdown while preserving Word comments inline."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
W = f"{{{W_NS}}}"


def text_from_element(element: etree._Element) -> str:
    parts: list[str] = []
    for node in element.iter():
        if node.tag in {W + "t", W + "delText"} and node.text:
            parts.append(node.text)
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return "".join(parts)


def load_comments(archive: ZipFile) -> dict[str, dict[str, str]]:
    if "word/comments.xml" not in archive.namelist():
        return {}

    root = etree.fromstring(archive.read("word/comments.xml"))
    comments: dict[str, dict[str, str]] = {}
    for comment in root.xpath(".//w:comment", namespaces=NS):
        comment_id = comment.get(W + "id", "")
        paragraphs = [
            text_from_element(paragraph).strip()
            for paragraph in comment.xpath("./w:p", namespaces=NS)
        ]
        comments[comment_id] = {
            "author": comment.get(W + "author", "") or "未知",
            "date": comment.get(W + "date", ""),
            "text": "\n".join(text for text in paragraphs if text),
        }
    return comments


def paragraph_text_and_anchors(
    paragraph: etree._Element,
) -> tuple[str, dict[str, tuple[str, str]], list[str]]:
    text_parts: list[str] = []
    anchor_parts: dict[str, list[str]] = {}
    reference_offsets: dict[str, int] = {}
    active: list[str] = []
    referenced: list[str] = []
    current_length = 0

    def visit(node: etree._Element) -> None:
        nonlocal current_length
        if node.tag == W + "commentRangeStart":
            comment_id = node.get(W + "id", "")
            if comment_id:
                active.append(comment_id)
                anchor_parts.setdefault(comment_id, [])
            return

        if node.tag == W + "commentRangeEnd":
            comment_id = node.get(W + "id", "")
            if comment_id in active:
                active.remove(comment_id)
            return

        if node.tag == W + "commentReference":
            comment_id = node.get(W + "id", "")
            if comment_id and comment_id not in referenced:
                referenced.append(comment_id)
                reference_offsets[comment_id] = current_length
            return

        if node.tag in {W + "t", W + "delText"}:
            value = node.text or ""
            text_parts.append(value)
            current_length += len(value)
            for comment_id in active:
                anchor_parts.setdefault(comment_id, []).append(value)
            return

        if node.tag == W + "tab":
            text_parts.append("\t")
            current_length += 1
            for comment_id in active:
                anchor_parts.setdefault(comment_id, []).append("\t")
            return

        if node.tag in {W + "br", W + "cr"}:
            text_parts.append("\n")
            current_length += 1
            for comment_id in active:
                anchor_parts.setdefault(comment_id, []).append("\n")
            return

        for child in node:
            visit(child)

    visit(paragraph)
    paragraph_text = "".join(text_parts).strip()
    locations: dict[str, tuple[str, str]] = {}
    for comment_id, parts in anchor_parts.items():
        anchor = "".join(parts).strip()
        if anchor:
            locations[comment_id] = ("锚定内容", anchor)

    for comment_id, offset in reference_offsets.items():
        if comment_id in locations:
            continue
        start = max(0, offset - 55)
        end = min(len(paragraph_text), offset + 90)
        before = paragraph_text[start:offset]
        after = paragraph_text[offset:end]
        prefix = "..." if start else ""
        suffix = "..." if end < len(paragraph_text) else ""
        locations[comment_id] = (
            "批注位置",
            f"{prefix}{before}〔批注位置〕{after}{suffix}",
        )

    ordered_ids = list(dict.fromkeys([*locations.keys(), *referenced]))
    return paragraph_text, locations, ordered_ids


def format_comment(
    comment_id: str,
    comment: dict[str, str],
    location: tuple[str, str] | None,
) -> list[str]:
    lines = [
        f"> [!comment] Word 批注 {comment_id}",
        f"> **作者：** {comment['author']}",
    ]
    if comment["date"]:
        lines.append(f"> **日期：** {comment['date']}")
    if location:
        label, value = location
        lines.append(f"> **{label}：** {value}")
    lines.append("> **批注内容：**")
    for line in comment["text"].splitlines() or [""]:
        lines.append(f"> {line}")
    return lines


def convert(source: Path, destination: Path) -> int:
    with ZipFile(source) as archive:
        comments = load_comments(archive)
        document = etree.fromstring(archive.read("word/document.xml"))

    output = [
        f"# {source.stem}",
        "",
        f"- 来源文件：`{source}`",
        f"- 转换时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Word 批注数：{len(comments)}",
        "- 说明：批注已转换为对应正文段落后的 Markdown callout。",
        "",
        "## 正文与批注",
        "",
    ]
    seen_comments: set[str] = set()

    body = document.find("w:body", namespaces=NS)
    if body is None:
        raise ValueError("DOCX 中未找到正文。")

    for child in body:
        if child.tag != W + "p":
            continue
        paragraph_text, locations, comment_ids = paragraph_text_and_anchors(child)
        if paragraph_text:
            output.extend([paragraph_text, ""])
        for comment_id in comment_ids:
            comment = comments.get(comment_id)
            if not comment:
                continue
            output.extend(format_comment(comment_id, comment, locations.get(comment_id)))
            output.append("")
            seen_comments.add(comment_id)

    missing = [comment_id for comment_id in comments if comment_id not in seen_comments]
    if missing:
        output.extend(["## 未锚定批注", ""])
        for comment_id in missing:
            output.extend(format_comment(comment_id, comments[comment_id], None))
            output.append("")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
    return len(comments)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    count = convert(args.source.expanduser().resolve(), args.destination.resolve())
    print(f"[OK] wrote {args.destination} with {count} comments")


if __name__ == "__main__":
    main()
