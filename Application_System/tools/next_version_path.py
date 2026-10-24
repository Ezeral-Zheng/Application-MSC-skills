#!/usr/bin/env python3
"""Return the next V-numbered path without a date prefix."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VERSION_RE = re.compile(r"(?:^|[-_ ])V(\d+)(?=[._ -]|$)", re.IGNORECASE)


def slug(value: str) -> str:
    value = value.strip().replace("/", "-").replace(":", "-")
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def highest_version(folder: Path, key: str) -> int:
    if not folder.exists():
        return 0
    key_lower = key.lower()
    highest = 0
    for path in folder.iterdir():
        if not path.is_file():
            continue
        if key_lower not in path.stem.lower():
            continue
        for match in VERSION_RE.finditer(path.name):
            highest = max(highest, int(match.group(1)))
    return highest


def next_path(folder: Path, key: str, ext: str) -> Path:
    clean_key = slug(key)
    clean_ext = ext if ext.startswith(".") else f".{ext}"
    next_version = highest_version(folder, clean_key) + 1
    return folder / f"{clean_key}-V{next_version}{clean_ext}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", required=True, help="Target output directory")
    parser.add_argument("--key", required=True, help="Stable document key, e.g. 刑雷-MSc-EE-Personal-Statement")
    parser.add_argument("--ext", default="md", help="Output extension, default: md")
    args = parser.parse_args()

    folder = Path(args.dir).resolve()
    md_path = next_path(folder, args.key, args.ext)
    print(md_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
