#!/usr/bin/env python3
"""Update post front matter (dry run by default; --apply to write)."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "posts"

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

SLUG_OVERRIDES: dict[str, list[str]] = {
    "650K-for-R": ["infrastructure", "announcements"],
    "r-universe-bioconductor-collaboration": [
        "top level projects",
        "infrastructure",
        "announcements",
    ],
    "r-consortium-technical-grant-cycle-opens-today": ["isc", "events", "announcements"],
    "contributing-to-base-r-with-coding-equity-and-joy-inside-the-r-contributors-project": [
        "rugs",
        "lgbtq+",
        "software development",
    ],
    "identifying-measles-immunity-gaps-in-the-us": [
        "r/medicine 2025",
        "epidemiology",
        "north america",
    ],
    "applied-epidemiology-in-r-cape-town-r-user-groups-contribution-to-global-immunization": [
        "rugs",
        "software development",
        "epidemiology",
        "africa",
    ],
    "investing-in-the-r-community-our-support-for-global-r-events-in-2026": [
        "events",
        "announcements",
    ],
    "r_plus_ai_call_for_proposals": ["r+ai 2025", "ai", "events"],
}

NLMIXR2_SLUGS = {
    "from-nlmixr2-working-group-nlmixr2-inter-occasion-variability",
    "nlmixr2-is-becoming-an-r-consortium-working-group",
    "survival-analysis-with-nlmixr2",
}

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
MAX_CATS = 5


def split_fm(text: str):
    m = re.match(r"^(---\s*\n)(.*?)(\n---\s*\n)", text, re.DOTALL)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), text[m.end() :]


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
    if (val.startswith('"') and val.endswith('"')) or (
        val.startswith("'") and val.endswith("'")
    ):
        return val[1:-1]
    return val


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


def title_from_fm(fm: str) -> str:
    return field_scalar(fm, "title") or ""


def normalize_categories(cats: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for c in cats:
        n = c.lower().strip()
        if n == "insfrastructure":
            c = "infrastructure"
        elif n == "working group":
            c = "working groups"
        elif n == "r+ai":
            c = "r+ai 2025"
        elif n == "community":
            c = "events"
        elif c in ("RUGS", "LGBTQ+", "Software Development", "Infrastructure"):
            mapping = {
                "RUGS": "rugs",
                "LGBTQ+": "lgbtq+",
                "Software Development": "software development",
                "Infrastructure": "infrastructure",
            }
            c = mapping.get(c, c)
        elif c in ("Bioconductor", "R-universe"):
            continue  # replaced by slug override
        n = c.lower().strip()
        if n in seen:
            continue
        seen.add(n)
        out.append(c if c.startswith("r/medicine") else c.lower() if "/" not in c else c)
    return out[:MAX_CATS]


def infer_region(slug: str, title: str, body: str) -> str | None:
    blob = f"{slug} {title} {body[:8000]}".lower()
    rules = [
        (r"mexico|quer[eé]taro|morelia|mexican\b", "south america"),
        (r"\bisrael\b|haifa\b", "middle east"),
        (r"tunisia|\btunis\b", "africa"),
        (r"pakistan|karachi|india|pune|nepal|kathmandu|philippines|thailand|malaysia|korea|china|brunei|japan|asia\b", "asia"),
        (r"nigeria|kenya|cameroon|botswana|benin|cotonou|malawi|south africa|cape town|africa\b", "africa"),
        (r"argentina|brazil|buenos aires|são paulo|sao paulo|costa rica|chile|peru|colombia|bariloche|queretaro", "south america"),
        (r"\buk\b|united kingdom|london|manchester|sheffield|zurich|europe\b|\beu\b", "eu"),
        (r"usa\b|united states|u\.s\.|cleveland|salt lake|seattle|ann arbor|nebraska|maine|new york|canada|north america", "north america"),
    ]
    for pat, region in rules:
        if re.search(pat, blob):
            return region
    return None


def infer_categories(slug: str, fm: str, body: str) -> list[str]:
    if slug in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[slug][:MAX_CATS]

    title = title_from_fm(fm)
    blob = f"{slug} {title} {body[:12000]}".lower()
    cats: list[str] = []

    if slug in R_AI_SLUGS:
        cats = ["r+ai 2025", "ai", "events"]
        if re.search(r"software|package|shiny", blob):
            cats.append("software development")
        return normalize_categories(cats)[:MAX_CATS]

    existing = normalize_categories(parse_categories(fm))
    if slug in NLMIXR2_SLUGS:
        return normalize_categories(existing)[:MAX_CATS]

    if existing and len(existing) >= 2:
        cats = list(existing)
    else:
        if re.search(r"r/medicine\s*2026|rmedicine\s*2026", blob):
            cats.append("r/medicine 2026")
        elif re.search(r"r/medicine\s*2025|rmedicine\s*2025", blob):
            cats.append("r/medicine 2025")
        elif re.search(r"r/medicine\s*2024|rmedicine\s*2024", blob):
            cats.append("r/medicine 2024")

        if re.search(r"r\+ai\s*2025|r\+ai\s*conference", blob) and slug not in R_AI_SLUGS:
            cats.extend(["r+ai 2025", "ai", "events"])

        if re.search(r"\bisc\b|infrastructure steering|grant cycle|funded project", blob):
            cats.extend(["isc", "announcements"])
        if re.search(r"fda|ectd|submission|submissions working", blob):
            cats.extend(["submissions", "pharma"])
        if re.search(r"pharma|pharmacometric|clinical trial", blob) and "pharma" not in cats:
            cats.append("pharma")
        if re.search(r"insurance|r!sk|risk modeling", blob):
            cats.append("insurance/risk")
        if re.search(r"rugs?\b|r-user group|r user group|r-ladies|r ladies", blob):
            cats.append("rugs")
        if re.search(r"webinar|conference|meetup|event\b", blob):
            cats.append("events")
        if re.search(r"\bai\b|llm|genai|machine learning", blob) and "ai" not in [c.lower() for c in cats]:
            cats.append("ai")
        if re.search(r"infrastructure|maintenance fund|r foundation", blob):
            cats.append("infrastructure")

        region = infer_region(slug, title, body)
        if region and region not in [c.lower() for c in cats]:
            cats.append(region)

        if not cats:
            if re.search(r"announcement|grant|funding", blob):
                cats = ["announcements"]
            elif re.search(r"software|package|shiny", blob):
                cats = ["software development"]
            else:
                cats = ["events"]

    if slug in R_AI_SLUGS:
        for req in ("r+ai 2025", "ai", "events"):
            if req not in [c.lower() for c in cats]:
                cats.insert(0, req)

    return normalize_categories(cats)[:MAX_CATS]


def list_images(post_dir: Path) -> list[Path]:
    return sorted(
        p
        for p in post_dir.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


def body_image_refs(body: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\(([^)]+)\)", body)


def pick_thumbnail(post_dir: Path, fm: str, body: str) -> tuple[str | None, str | None]:
    images = list_images(post_dir)
    if not images:
        return None, None

    names = {p.name: p for p in images}
    for typo, fix in (("unamed.jpg", "unnamed.jpg"),):
        if typo in names and fix not in names:
            names[fix] = names[typo]

    current = field_scalar(fm, "image")
    if current and not re.match(r"^https?://", current, re.I):
        fixed = current.replace("unamed.jpg", "unnamed.jpg")
        if fixed in names:
            alt = field_scalar(fm, "image-alt") or title_from_fm(fm)
            return fixed, alt

    for p in images:
        if re.search(r"thumbnail", p.name, re.I):
            return p.name, field_scalar(fm, "image-alt") or title_from_fm(fm)

    for p in images:
        if re.search(r"main|logo", p.name, re.I):
            return p.name, field_scalar(fm, "image-alt") or title_from_fm(fm)

    if (post_dir / "media.jpg").is_file():
        return "media.jpg", field_scalar(fm, "image-alt") or title_from_fm(fm)

    for ref in body_image_refs(body):
        ref = ref.split("?")[0].split("#")[0]
        base = Path(ref).name
        if base in names:
            return base, field_scalar(fm, "image-alt") or title_from_fm(fm)

    return None, None


def fmt_categories(cats: list[str]) -> str:
    inner = ", ".join(f'"{c}"' for c in cats)
    return f"categories: [{inner}]"


def upsert_fm_line(fm: str, key: str, value: str, quoted: bool = True) -> str:
    line = f'{key}: "{value}"' if quoted else f"{key}: {value}"
    if re.search(rf"^{re.escape(key)}:", fm, re.MULTILINE):
        return re.sub(
            rf"^{re.escape(key)}:.*$",
            line,
            fm,
            count=1,
            flags=re.MULTILINE,
        )
    return fm.rstrip() + "\n" + line + "\n"


def remove_fm_key(fm: str, key: str) -> str:
    return re.sub(rf"^{re.escape(key)}:.*\n?", "", fm, flags=re.MULTILINE)


def set_categories_block(fm: str, cats: list[str]) -> str:
    new_line = fmt_categories(cats)
    if re.search(r"^categories:", fm, re.MULTILINE):
        fm = re.sub(
            r"^categories:\s*\[.*?\]\s*$",
            new_line,
            fm,
            count=1,
            flags=re.MULTILINE | re.DOTALL,
        )
        if "categories:" in fm and fmt_categories(cats) not in fm:
            fm = re.sub(
                r"^categories:\s*\n(?:\s+-\s+.+\n)+",
                new_line + "\n",
                fm,
                count=1,
                flags=re.MULTILINE,
            )
        return fm
    return fm.rstrip() + "\n" + new_line + "\n"


def process_post(path: Path, apply: bool) -> bool:
    slug = path.parent.name
    text = path.read_text(encoding="utf-8", errors="replace")
    parts = split_fm(text)
    if not parts:
        return False
    open_delim, fm, close_delim, body = parts
    orig_fm = fm
    changed = False

    if slug == "r-consortium-technical-grant-cycle-opens-today" and re.search(
        r"^tags:", fm, re.MULTILINE
    ):
        fm = remove_fm_key(fm, "tags")
        changed = True

    expected_url = f"https://r-consortium.org/posts/{slug}/"
    if field_scalar(fm, "url") != expected_url:
        fm = upsert_fm_line(fm, "url", expected_url)
        changed = True

    if "unpublished" not in field_keys(fm):
        fm = upsert_fm_line(fm, "unpublished", "false", quoted=False)
        changed = True

    new_cats = infer_categories(slug, fm, body)
    old_cats = normalize_categories(parse_categories(fm))
    raw_cats = parse_categories(fm)
    if new_cats and (new_cats != old_cats or raw_cats != new_cats):
        fm = set_categories_block(fm, new_cats)
        changed = True

    img_name, img_alt = pick_thumbnail(path.parent, fm, body)
    has_image_key = "image" in field_keys(fm)
    if img_name:
        if field_scalar(fm, "image") != img_name:
            fm = upsert_fm_line(fm, "image", img_name)
            changed = True
        alt = img_alt or title_from_fm(fm) or "Illustration for post"
        if field_scalar(fm, "image-alt") != alt:
            fm = upsert_fm_line(fm, "image-alt", alt)
            changed = True
    elif field_scalar(fm, "image") and re.match(r"^https?://", field_scalar(fm, "image") or "", re.I):
        alt = field_scalar(fm, "image-alt") or title_from_fm(fm) or "Illustration for post"
        if field_scalar(fm, "image-alt") != alt:
            fm = upsert_fm_line(fm, "image-alt", alt)
            changed = True
    else:
        if has_image_key:
            cur = field_scalar(fm, "image") or ""
            if not re.match(r"^https?://", cur, re.I):
                fm = remove_fm_key(fm, "image")
                fm = remove_fm_key(fm, "image-alt")
                changed = True

    if fm != orig_fm:
        if apply:
            path.write_text(open_delim + fm + close_delim + body, encoding="utf-8")
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to index.qmd files",
    )
    args = parser.parse_args()
    paths = sorted(POSTS.glob("*/index.qmd"))
    updated = 0
    for p in paths:
        if process_post(p, apply=args.apply):
            updated += 1
    mode = "updated" if args.apply else "would update"
    print(f"{mode} {updated} of {len(paths)} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
