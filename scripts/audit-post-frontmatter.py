#!/usr/bin/env python3
"""Validate front matter for posts/*/index.qmd."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"

APPROVED_CATEGORIES = {
    "r/medicine 2026",
    "r/medicine 2025",
    "r/medicine 2024",
    "r+ai 2025",
    "ai",
    "software development",
    "insurance/risk",
    "finance",
    "pharma",
    "clinical research",
    "healthcare",
    "epidemiology",
    "environment",
    "geomapping",
    "lgbtq+",
    "women in tech",
    "isc",
    "working groups",
    "top level projects",
    "submissions",
    "rugs",
    "announcements",
    "events",
    "members",
    "asia",
    "africa",
    "eu",
    "south america",
    "north america",
    "middle east",
    "infrastructure",
}
APPROVED_LOWER = {c.lower() for c in APPROVED_CATEGORIES}

R_AI_SLUGS = {
    "brand-your-docs-apps-and-ggplots-using-llms",
    "gradient-boosting-machines-gbms-in-the-age-of-llms-and-chatgpt",
    "introducing-geodl-an-r-package-for-geospatial-semantic-segmentation",
    "keeping-llms-in-their-lane-focused-ai-for-data-science-and-research",
    "kuzco-computer-vision-made-easy",
    "me-myself-claude",
    "mini007-a-lightweight-framework-for-multi-agent-orchestration-in-r",
    "rplusai-use-rag-from-your-database-to-gain-insights-into-the-r-consortium",
    "tracking-the-evolution-of-r-and-python-tools-for-genai",
}

REQUIRED_FIELDS = ("title", "description", "author", "categories", "date")
MAX_CATEGORIES = 5
R_AI_REQUIRED = {"r+ai 2025", "ai", "events"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}


def split_front_matter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None, None, text
    return m.group(1), m.end(), text[m.end() :]


def field_keys(fm: str) -> set[str]:
    return set(re.findall(r"^([a-zA-Z0-9_-]+):", fm, re.MULTILINE))


def field_scalar(fm: str, key: str) -> str | None:
    m = re.search(
        rf"^{re.escape(key)}:\s*(.+?)(?:\n(?![\s#-])|\Z)",
        fm,
        re.MULTILINE | re.DOTALL,
    )
    if not m:
        return None
    val = m.group(1).strip()
    if val.startswith('"') and val.endswith('"'):
        return val[1:-1]
    if val.startswith("'") and val.endswith("'"):
        return val[1:-1]
    return val.strip('"')


def parse_categories(fm: str) -> list[str]:
    m = re.search(r"categories:\s*\[(.*?)\]", fm, re.DOTALL)
    if m:
        inner = m.group(1)
        parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', inner)
        return [p.strip().strip('"').strip("'") for p in parts if p.strip()]
    block = re.search(r"categories:\s*\n((?:\s+-\s+.+\n)+)", fm)
    if block:
        return [
            re.sub(r"^\s+-\s+", "", line).strip().strip('"').strip("'")
            for line in block.group(1).splitlines()
            if line.strip()
        ]
    return []


def norm_cat(c: str) -> str:
    return c.lower().strip()


def audit_post(path: Path) -> list[str]:
    slug = path.parent.name
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    fm, _, body = split_front_matter(text)
    if fm is None:
        return [f"{slug}: missing front matter delimiters"]

    keys = field_keys(fm)
    for req in REQUIRED_FIELDS:
        if req not in keys and req != "categories":
            errors.append(f"{slug}: missing required field '{req}'")

    cats = parse_categories(fm)
    if "categories" not in keys and not cats:
        errors.append(f"{slug}: missing required field 'categories'")

    if len(cats) > MAX_CATEGORIES:
        errors.append(f"{slug}: more than {MAX_CATEGORIES} categories ({len(cats)})")

    for c in cats:
        n = norm_cat(c)
        if n == "insfrastructure":
            errors.append(f"{slug}: typo category '{c}' (use infrastructure)")
        elif n == "working group":
            errors.append(f"{slug}: use 'working groups' not '{c}'")
        elif n == "r+ai":
            errors.append(f"{slug}: legacy category 'r+ai' (use r+ai 2025)")
        elif n not in APPROVED_LOWER:
            errors.append(f"{slug}: unapproved category '{c}'")

    if slug in R_AI_SLUGS:
        have = {norm_cat(c) for c in cats}
        missing_trio = R_AI_REQUIRED - have
        if missing_trio:
            errors.append(
                f"{slug}: R+AI post missing categories {sorted(missing_trio)}"
            )

    image = field_scalar(fm, "image")
    if image:
        if image.strip() in ("thumbnail.webp", "thumbnail.png") and not (
            path.parent / image
        ).exists():
            errors.append(f"{slug}: placeholder image '{image}'")
        if not re.match(r"^https?://", image, re.I):
            img_path = path.parent / image
            if not img_path.is_file():
                errors.append(f"{slug}: image file not found: {image}")
        if "image-alt" not in keys:
            errors.append(f"{slug}: image set but missing image-alt")

    expected_url = f"https://r-consortium.org/posts/{slug}/"
    url = field_scalar(fm, "url")
    if url and url.rstrip("/") + "/" != expected_url:
        errors.append(f"{slug}: url mismatch (got {url!r}, want {expected_url})")
    elif "url" in keys and not url:
        errors.append(f"{slug}: empty url")

    return errors


def main() -> int:
    paths = sorted(POSTS.glob("*/index.qmd"))
    all_errors: list[str] = []
    for p in paths:
        all_errors.extend(audit_post(p))

    if all_errors:
        print(f"Found {len(all_errors)} error(s) in {len(paths)} posts:\n")
        for e in all_errors:
            print(e)
        return 1

    print(f"OK: {len(paths)} posts passed audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
