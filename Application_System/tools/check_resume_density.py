#!/usr/bin/env python3
"""Hard QA gate for rendered one-page resume density."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def measure(path: Path, threshold: int = 235, min_ratio: float = 0.90) -> dict:
    image = Image.open(path).convert("L")
    width, height = image.size
    left, right = int(width * 0.08), int(width * 0.92)
    top, bottom = int(height * 0.04), int(height * 0.96)
    pixels = image.load()
    rows = [y for y in range(top, bottom) if any(pixels[x, y] < threshold for x in range(left, right))]
    content_bottom = max(rows) if rows else None
    ratio = content_bottom / height if content_bottom is not None else 0.0
    usable_top, usable_bottom = top / height, bottom / height
    required_ratio = usable_top + min_ratio * (usable_bottom - usable_top)
    return {
        "image": str(path),
        "width": width,
        "height": height,
        "content_bottom_px": content_bottom,
        "content_bottom_ratio": round(ratio, 4),
        "required_ratio": round(required_ratio, 4),
        "status": "Pass" if content_bottom is not None and ratio >= required_ratio else "Fail",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("render_dir", type=Path)
    ap.add_argument("--min-ratio", type=float, default=0.90)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    pages = sorted(args.render_dir.glob("page-*.png"))
    results = [measure(page, min_ratio=args.min_ratio) for page in pages]
    payload = {"page_count": len(pages), "pages": results}
    payload["status"] = "Pass" if len(pages) == 1 and all(r["status"] == "Pass" for r in results) else "Fail"
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.json else payload)
    raise SystemExit(0 if payload["status"] == "Pass" else 1)


if __name__ == "__main__":
    main()
