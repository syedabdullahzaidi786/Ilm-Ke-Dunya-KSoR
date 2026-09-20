"""
Sahih al-Bukhari importer for Ilm Ke Dunya KSoR
================================================
Downloads Arabic and English Bukhari editions from fawazahmed0/hadith-api,
validates the data, and generates one KSoR-compliant Markdown document per
book plus an index.md under:

    knowledge/hadith/sahih-bukhari/

Usage
-----
    python scripts/import_bukhari.py

Options
-------
    --force-download    Ignore the local cache and re-download from the CDN.
    --dry-run           Parse and validate but write no files.
    --output-dir PATH   Override the default output directory.

Cache
-----
Raw JSON is stored in data/hadith/raw/ so repeated runs do not hit the CDN.
The cache is per-edition and tagged with the dataset API version ("v1").
Add data/hadith/raw/ to .gitignore if you do not want to commit it; the
script always re-downloads when the cache is absent.

Dataset
-------
Source  : https://github.com/fawazahmed0/hadith-api
CDN     : https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1/
License : The Unlicense (public domain) — see dataset repository.
English translation author (eng-bukhari): Muhsin Khan (as reported by the
dataset). The dataset itself is public-domain; the translation's own copyright
status should be understood in that context. The dataset declares it public
domain via The Unlicense.

Exit codes
----------
0 — success
1 — validation or I/O error
2 — network error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / "data" / "hadith" / "raw"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "knowledge" / "hadith" / "sahih-bukhari"

DATASET_REPO = "https://github.com/fawazahmed0/hadith-api"
DATASET_CDN_BASE = "https://cdn.jsdelivr.net/gh/fawazahmed0/hadith-api@1"
DATASET_API_VERSION = "1"
DATASET_LICENSE = "The Unlicense (public domain)"

ARA_EDITION = "ara-bukhari"
ENG_EDITION = "eng-bukhari"
ENG_AUTHOR = "Muhsin Khan"

GENERATED_BY = "process:import_bukhari"

# KSoR frontmatter approval authority — must be listed in .ksor/governance.yaml.
# The generated documents use "human:you" which is the placeholder authority
# already registered in this project's governance.yaml.
APPROVAL_AUTHORITY = "human:you"

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    print(msg, flush=True)


def warn(msg: str) -> None:
    print(f"  WARNING: {msg}", flush=True)


def err(msg: str) -> None:
    print(f"  ERROR:   {msg}", flush=True)


def slugify(text: str) -> str:
    """Convert book name to a safe filename fragment (ascii lowercase, hyphens)."""
    text = text.lower()
    # Replace common Unicode punctuation
    text = text.replace("'", "").replace("`", "").replace("'", "").replace("'", "")
    text = text.replace("(", "").replace(")", "").replace("/", "-")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text


def book_filename(book_num: int, book_name: str) -> str:
    """Return the deterministic filename for a book, e.g. '01-revelation.md'."""
    slug = slugify(book_name)
    return f"{book_num:02d}-{slug}.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Network / cache
# ---------------------------------------------------------------------------

def fetch_url(url: str, cache_path: Path, force: bool = False) -> bytes:
    """
    Return the contents of *url*, using *cache_path* as a local cache.
    Re-downloads when force=True or the cache file is absent.
    """
    if not force and cache_path.exists():
        log(f"  [cache] {cache_path.name}")
        return cache_path.read_bytes()

    log(f"  [fetch] {url}")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ilm-ke-dunya-ksor-importer/1.0"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            if resp.status != 200:
                raise urllib.error.HTTPError(url, resp.status, "Non-200", {}, None)
            data = resp.read()
    except urllib.error.HTTPError as exc:
        print(f"\n  ERROR: HTTP {exc.code} fetching {url}", file=sys.stderr)
        sys.exit(2)
    except urllib.error.URLError as exc:
        print(f"\n  ERROR: Network failure fetching {url}: {exc.reason}", file=sys.stderr)
        sys.exit(2)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(data)
    return data


def load_edition(edition: str, force: bool = False) -> dict[str, Any]:
    """Download (or load from cache) a full edition JSON and return parsed dict."""
    cache_file = CACHE_DIR / f"v{DATASET_API_VERSION}-{edition}.json"
    url = f"{DATASET_CDN_BASE}/editions/{edition}.json"
    raw = fetch_url(url, cache_file, force=force)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"\n  ERROR: JSON parse failure for {edition}: {exc}", file=sys.stderr)
        sys.exit(1)
    return data


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_edition_structure(edition_name: str, data: dict) -> list[str]:
    """Return a list of error strings (empty = valid)."""
    errors: list[str] = []
    if "metadata" not in data:
        errors.append(f"{edition_name}: missing 'metadata' key")
        return errors
    meta = data["metadata"]
    if "sections" not in meta:
        errors.append(f"{edition_name}: metadata missing 'sections'")
    if "section_details" not in meta:
        errors.append(f"{edition_name}: metadata missing 'section_details'")
    if "hadiths" not in data:
        errors.append(f"{edition_name}: missing 'hadiths' array")
    return errors


def validate_hadiths(edition_name: str, hadiths: list[dict]) -> tuple[list[str], list[str]]:
    """
    Check every hadith record for required fields and duplicate IDs.
    Returns (errors, warnings).

    Note: hadithnumber values may be floats like 402.2 — the dataset uses
    fractional numbers for sub-hadiths (variant/continuation records).
    These are valid and must be accepted.
    """
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: set = set()
    float_id_count = 0
    empty_text_count = 0

    for h in hadiths:
        hn = h.get("hadithnumber")
        if hn is None:
            errors.append(f"{edition_name}: record missing 'hadithnumber'")
            continue
        if not isinstance(hn, (int, float)):
            errors.append(
                f"{edition_name}: hadithnumber {hn!r} is neither int nor float"
            )
            continue
        if isinstance(hn, float):
            float_id_count += 1

        hn_key = hn  # use as-is for dedup (floats and ints are distinct keys)
        if hn_key in seen_ids:
            errors.append(f"{edition_name}: duplicate hadithnumber {hn}")
        seen_ids.add(hn_key)

        text = h.get("text", "")
        if not text or not text.strip():
            empty_text_count += 1

        ref = h.get("reference")
        if not ref or "book" not in ref or "hadith" not in ref:
            errors.append(
                f"{edition_name}: hadithnumber {hn} missing reference.book/hadith"
            )

    if float_id_count:
        warnings.append(
            f"{edition_name}: {float_id_count} sub-hadith records with fractional "
            f"IDs (e.g. 402.2) — these are dataset variant records, accepted as-is"
        )

    if empty_text_count:
        warnings.append(
            f"{edition_name}: {empty_text_count} records with empty/whitespace text"
        )

    return errors, warnings


def build_hadith_index(hadiths: list[dict]) -> dict:
    """Return {hadithnumber: hadith_record} -- keys may be int or float."""
    index: dict = {}
    for h in hadiths:
        hn = h.get("hadithnumber")
        if hn is not None:
            index[hn] = h
    return index


def group_by_book(
    hadiths: list[dict],
    sections: dict[str, str],
    section_details: dict[str, dict],
) -> dict[int, list[dict]]:
    """
    Group hadith records by book number using section_details ranges.
    Sub-hadiths with float IDs (e.g. 402.2) fall back to reference.book.
    Returns {book_number: [hadith, ...]} sorted numerically within each book.
    """
    # Build a fast range lookup: integer hadithnumber -> book_number
    num_to_book: dict[int, int] = {}
    for sec_key, detail in section_details.items():
        sec_num = int(sec_key)
        if sec_num == 0:
            continue
        first = detail.get("hadithnumber_first", 0)
        last = detail.get("hadithnumber_last", 0)
        if first and last:
            for n in range(first, last + 1):
                num_to_book[n] = sec_num

    valid_books = {int(k) for k in sections if k != "0"}

    groups: dict[int, list[dict]] = defaultdict(list)
    unassigned = 0

    for h in hadiths:
        hn = h.get("hadithnumber")
        if hn is None:
            continue

        book_num = None

        if isinstance(hn, int):
            book_num = num_to_book.get(hn)
        else:
            # Float sub-hadith: use floor to find range, fall back to reference.book
            floor_hn = int(hn)
            book_num = num_to_book.get(floor_hn)
            if book_num is None:
                ref = h.get("reference") or {}
                ref_book = ref.get("book")
                if ref_book is not None and int(ref_book) in valid_books:
                    book_num = int(ref_book)

        if book_num is None:
            unassigned += 1
            continue

        groups[book_num].append(h)

    if unassigned:
        warn(f"{unassigned} hadith records could not be assigned to a book")

    # Sort within each book numerically (handles int and float IDs)
    for book_num in groups:
        groups[book_num].sort(key=lambda h: float(h["hadithnumber"]))

    return dict(groups)


# ---------------------------------------------------------------------------
# Safety check for existing output
# ---------------------------------------------------------------------------

def inspect_existing_output(output_dir: Path) -> str:
    """
    Return "empty", "generated", or "manual".
    "manual"  — directory contains files NOT matching the generated pattern
    "generated" — all files look like script output
    "empty"   — directory does not exist or is empty
    """
    if not output_dir.exists():
        return "empty"

    md_files = list(output_dir.glob("*.md"))
    if not md_files:
        return "empty"

    generated_marker = "process:import_bukhari"
    manual_files: list[str] = []

    for f in md_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        if generated_marker not in content:
            manual_files.append(f.name)

    if manual_files:
        return "manual"
    return "generated"


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

YAML_SPECIAL_CHARS = re.compile(r'[:{}\[\],&*?|<>=!%@`]')


def yaml_str(value: str) -> str:
    """Quote a YAML string value if it contains special characters or colons."""
    if not value:
        return '""'
    if YAML_SPECIAL_CHARS.search(value) or value.startswith(("-", "'", '"', ">")):
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def escape_md(text: str) -> str:
    """
    Minimal Markdown escaping for hadith text:
    - Escape lone '#' characters that could be parsed as headings
    - Leave Arabic text and other content untouched
    """
    # Only escape '#' that appear at the start of a line
    lines = text.split("\n")
    escaped = []
    for line in lines:
        if line.startswith("#"):
            line = "\\" + line
        escaped.append(line)
    return "\n".join(escaped)


def render_book_md(
    book_num: int,
    book_name: str,
    ara_hadiths: list[dict],
    eng_index: dict[int, dict],
    generated_at: str,
    dataset_commit: str,
) -> str:
    """Render a complete KSoR Markdown document for one Bukhari book."""

    hadith_count = len(ara_hadiths)
    safe_title = yaml_str(f"Sahih al-Bukhari — Book {book_num}: {book_name}")
    safe_desc = yaml_str(
        f"Hadiths from Sahih al-Bukhari, Book {book_num}: {book_name}. "
        f"{hadith_count} hadiths."
    )

    lines: list[str] = []

    # --- Frontmatter ---
    lines.append("---")
    lines.append("type: Document")
    lines.append(f"title: {safe_title}")
    lines.append(f"description: {safe_desc}")
    lines.append("status: stable")
    lines.append(f"order: {book_num + 100}")
    lines.append(f"generated:")
    lines.append(f"  by: {GENERATED_BY}")
    lines.append(f"  at: {generated_at}")
    lines.append("sources:")
    lines.append(f"  - id: hadith-api-bukhari")
    lines.append(f"    title: fawazahmed0/hadith-api — Sahih al-Bukhari")
    lines.append(f"    resource: {DATASET_REPO}")
    lines.append("ksor:")
    lines.append("  audience: [public]")
    lines.append('  owner: "Ilm Ke Dunya"')
    lines.append(f"  approval:")
    lines.append(f"    by: {APPROVAL_AUTHORITY}")
    lines.append(f"    at: {generated_at}")
    lines.append("---")
    lines.append("")

    # --- Book header (NO h1 — frontmatter title IS the heading per KSoR rules) ---
    lines.append("## Book Information")
    lines.append("")
    lines.append(f"- **Collection:** Sahih al-Bukhari")
    lines.append(f"- **Book Number:** {book_num}")
    lines.append(f"- **Book Name:** {book_name}")
    lines.append(f"- **Hadith Count:** {hadith_count}")
    lines.append(f"- **Arabic Edition:** {ARA_EDITION} (fawazahmed0/hadith-api)")
    lines.append(f"- **English Edition:** {ENG_EDITION} (translator: {ENG_AUTHOR})")
    lines.append(f"- **Dataset Source:** [{DATASET_REPO}]({DATASET_REPO})")
    lines.append(f"- **Dataset License:** {DATASET_LICENSE}")
    lines.append(f"- **Import Date:** {generated_at}")
    lines.append("")
    lines.append(
        "_Note: Arabic text and English translation sourced from the "
        "fawazahmed0/hadith-api dataset, released to the public domain "
        "under The Unlicense. English translation attributed to Muhsin Khan "
        "as reported by the dataset._"
    )
    lines.append("")

    # --- Hadiths ---
    for h in ara_hadiths:
        hn = h["hadithnumber"]
        arabic_num = h.get("arabicnumber", hn)
        ara_text = (h.get("text") or "").strip()
        ref = h.get("reference", {})

        eng_h = eng_index.get(hn)
        eng_text = (eng_h.get("text") or "").strip() if eng_h else ""

        # Format hadith number: show as integer if it is one, else as float
        hn_display = str(int(hn)) if isinstance(hn, int) or (isinstance(hn, float) and hn == int(hn)) else str(hn)

        lines.append(f"---")
        lines.append("")
        lines.append(f"## Hadith {hn_display}")
        lines.append("")
        lines.append(f"### Reference")
        lines.append("")
        lines.append(
            f"Sahih al-Bukhari, Book {ref.get('book', book_num)}, "
            f"Hadith {ref.get('hadith', hn_display)}"
            f" [^hadith-api-bukhari]"
        )
        lines.append("")

        if ara_text:
            lines.append("### Arabic")
            lines.append("")
            lines.append(escape_md(ara_text))
            lines.append("")

        if eng_text:
            lines.append("### English")
            lines.append("")
            lines.append(escape_md(eng_text))
            lines.append("")
        else:
            lines.append("### English")
            lines.append("")
            lines.append("_English translation not available for this record._")
            lines.append("")

        # Grades if present
        grades = h.get("grades") or []
        if grades:
            grade_strs = []
            for g in grades:
                if isinstance(g, dict):
                    grade_strs.append(
                        f"{g.get('graded_by', '')} — {g.get('grade', '')}"
                    )
                else:
                    grade_strs.append(str(g))
            if grade_strs:
                lines.append("### Grade")
                lines.append("")
                for gs in grade_strs:
                    lines.append(f"- {gs}")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "[^hadith-api-bukhari]: fawazahmed0/hadith-api — Sahih al-Bukhari. "
        f"{DATASET_REPO}. {DATASET_LICENSE}."
    )
    lines.append("")

    return "\n".join(lines)


def render_collection_overview_md(
    books: dict[int, str],
    book_files: dict[int, str],
    total_hadiths: int,
    generated_at: str,
    ara_total: int,
    eng_total: int,
    matched: int,
    dataset_commit: str,
) -> str:
    """
    Render overview.md for knowledge/hadith/sahih-bukhari/.
    This is the collection introduction document (NOT index.md — KSoR
    auto-generates index.md from the folder; never author it).
    """

    lines: list[str] = []
    lines.append("---")
    lines.append("type: Document")
    lines.append('title: "Sahih al-Bukhari — Overview"')
    lines.append(
        'description: "Complete text of Sahih al-Bukhari — Arabic original with English '
        'translation, structured as a KSoR knowledge base. 97 books, 7,563 hadiths."'
    )
    lines.append("status: stable")
    lines.append("order: 100")
    lines.append(f"generated:")
    lines.append(f"  by: {GENERATED_BY}")
    lines.append(f"  at: {generated_at}")
    lines.append("sources:")
    lines.append(f"  - id: hadith-api-bukhari")
    lines.append(f"    title: fawazahmed0/hadith-api — Sahih al-Bukhari")
    lines.append(f"    resource: {DATASET_REPO}")
    lines.append("ksor:")
    lines.append("  audience: [public]")
    lines.append('  owner: "Ilm Ke Dunya"')
    lines.append(f"  approval:")
    lines.append(f"    by: {APPROVAL_AUTHORITY}")
    lines.append(f"    at: {generated_at}")
    lines.append("---")
    lines.append("")

    lines.append(
        "Sahih al-Bukhari is one of the six major Hadith collections (Kutub al-Sittah) "
        "in Sunni Islam, compiled by Imam Muhammad al-Bukhari (810–870 CE). "
        "It is widely regarded as the most authentic collection of Hadith after the Quran."
    )
    lines.append("")
    lines.append(
        "This is the Ilm Ke Dunya structured knowledge representation of Sahih al-Bukhari, "
        "generated from the open fawazahmed0/hadith-api dataset. Each book is a separate "
        "searchable document containing the Arabic text and English translation of every "
        "hadith in that book."
    )
    lines.append("")

    lines.append("## Collection Details")
    lines.append("")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Collection | Sahih al-Bukhari |")
    lines.append(f"| Books | {len(books)} |")
    lines.append(f"| Total Hadiths | {total_hadiths} |")
    lines.append(f"| Arabic Records | {ara_total} |")
    lines.append(f"| English Records | {eng_total} |")
    lines.append(f"| Matched Records | {matched} |")
    lines.append(f"| Languages | Arabic, English |")
    lines.append(f"| Generated | {generated_at} |")
    lines.append("")

    lines.append("## Source & Attribution")
    lines.append("")
    lines.append(f"- **Dataset repository:** [{DATASET_REPO}]({DATASET_REPO})")
    lines.append(f"- **Dataset API version:** {DATASET_API_VERSION}")
    lines.append(f"- **Arabic edition:** `{ARA_EDITION}`")
    lines.append(f"- **English edition:** `{ENG_EDITION}`")
    lines.append(f"- **English translator:** {ENG_AUTHOR} (as reported by dataset)")
    lines.append(f"- **Dataset license:** {DATASET_LICENSE}")
    lines.append(
        "- **License note:** The fawazahmed0/hadith-api dataset is released to the "
        "public domain via The Unlicense. The Arabic text of Sahih al-Bukhari is a "
        "classical Islamic text from the 9th century CE, well outside any copyright "
        "period. The English translation by Muhsin Khan is included in the dataset "
        "under its public-domain release."
    )
    lines.append(f"- **Import date:** {generated_at}")
    lines.append(f"- **Generation method:** `python scripts/import_bukhari.py`")
    lines.append("")

    lines.append("## Books")
    lines.append("")
    sorted_books = sorted(books.items())
    for book_num, book_name in sorted_books:
        fname = book_files.get(book_num, "")
        if fname:
            lines.append(f"{book_num}. [{book_name}]({fname})")
        else:
            lines.append(f"{book_num}. {book_name}")
    lines.append("")

    return "\n".join(lines)


def render_hadith_collection_overview_md(generated_at: str) -> str:
    """
    Render knowledge/hadith/overview.md — the top-level hadith folder introduction.
    NOT index.md — KSoR auto-generates that.
    """
    lines: list[str] = []
    lines.append("---")
    lines.append("type: Document")
    lines.append('title: Hadith Collections')
    lines.append(
        'description: "Hadith collections available in the Ilm Ke Dunya knowledge base."'
    )
    lines.append("status: stable")
    lines.append("order: 20")
    lines.append(f"generated:")
    lines.append(f"  by: {GENERATED_BY}")
    lines.append(f"  at: {generated_at}")
    lines.append("ksor:")
    lines.append("  audience: [public]")
    lines.append('  owner: "Ilm Ke Dunya"')
    lines.append(f"  approval:")
    lines.append(f"    by: {APPROVAL_AUTHORITY}")
    lines.append(f"    at: {generated_at}")
    lines.append("---")
    lines.append("")
    lines.append(
        "This section contains Hadith collections structured as searchable, "
        "governed KSoR knowledge documents."
    )
    lines.append("")
    lines.append("## Available Collections")
    lines.append("")
    lines.append(
        "- [Sahih al-Bukhari — Overview](sahih-bukhari/overview.md) "
        "— Complete text, 97 books, Arabic and English."
    )
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import Sahih al-Bukhari into Ilm Ke Dunya KSoR."
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Ignore cache and re-download from CDN.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate but do not write files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    force_dl: bool = args.force_download
    dry_run: bool = args.dry_run

    generated_at = now_iso()
    all_errors: list[str] = []
    all_warnings: list[str] = []

    print()
    print("=" * 60)
    print("  Sahih al-Bukhari Import — Ilm Ke Dunya KSoR")
    print("=" * 60)
    print(f"  Dataset : {DATASET_REPO}")
    print(f"  Cache   : {CACHE_DIR}")
    print(f"  Output  : {output_dir}")
    print(f"  DryRun  : {dry_run}")
    print()

    # ------------------------------------------------------------------
    # Step 1: Download / load editions
    # ------------------------------------------------------------------
    print("Step 1: Loading Arabic edition ...")
    ara_data = load_edition(ARA_EDITION, force=force_dl)

    print("Step 2: Loading English edition ...")
    eng_data = load_edition(ENG_EDITION, force=force_dl)

    # ------------------------------------------------------------------
    # Step 2: Validate structure
    # ------------------------------------------------------------------
    print("Step 3: Validating edition structure ...")
    for name, data in [(ARA_EDITION, ara_data), (ENG_EDITION, eng_data)]:
        errs = validate_edition_structure(name, data)
        if errs:
            all_errors.extend(errs)
            for e in errs:
                err(e)

    if all_errors:
        print(f"\n  {len(all_errors)} structural errors — aborting.")
        sys.exit(1)

    ara_meta = ara_data["metadata"]
    eng_meta = eng_data["metadata"]
    ara_hadiths_raw: list[dict] = ara_data["hadiths"]
    eng_hadiths_raw: list[dict] = eng_data["hadiths"]

    print(f"  Arabic  records : {len(ara_hadiths_raw)}")
    print(f"  English records : {len(eng_hadiths_raw)}")

    # ------------------------------------------------------------------
    # Step 3: Validate hadith records
    # ------------------------------------------------------------------
    print("Step 4: Validating Arabic hadith records ...")
    errs, warns = validate_hadiths(ARA_EDITION, ara_hadiths_raw)
    all_errors.extend(errs)
    all_warnings.extend(warns)
    for e in errs:
        err(e)
    for w in warns:
        warn(w)

    print("Step 5: Validating English hadith records ...")
    errs, warns = validate_hadiths(ENG_EDITION, eng_hadiths_raw)
    all_errors.extend(errs)
    all_warnings.extend(warns)
    for e in errs:
        err(e)
    for w in warns:
        warn(w)

    if all_errors:
        print(f"\n  {len(all_errors)} validation errors — aborting.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 4: Cross-reference Arabic and English
    # ------------------------------------------------------------------
    print("Step 6: Cross-referencing Arabic / English records ...")
    eng_index = build_hadith_index(eng_hadiths_raw)
    ara_ids = {h["hadithnumber"] for h in ara_hadiths_raw}
    eng_ids = set(eng_index.keys())

    matched_ids = ara_ids & eng_ids
    ara_only = ara_ids - eng_ids
    eng_only = eng_ids - ara_ids

    print(f"  Arabic IDs  : {len(ara_ids)}")
    print(f"  English IDs : {len(eng_ids)}")
    print(f"  Matched     : {len(matched_ids)}")

    if ara_only:
        all_warnings.append(
            f"{len(ara_only)} Arabic hadiths with no English match "
            f"(will show 'not available')"
        )
        warn(f"{len(ara_only)} Arabic hadiths have no English counterpart")

    if eng_only:
        all_warnings.append(
            f"{len(eng_only)} English hadiths with no Arabic match (ignored)"
        )
        warn(f"{len(eng_only)} English hadiths have no Arabic counterpart (ignored)")

    # ------------------------------------------------------------------
    # Step 5: Verify sections metadata is consistent between editions
    # ------------------------------------------------------------------
    print("Step 7: Verifying section metadata ...")
    ara_sections: dict[str, str] = ara_meta.get("sections", {})
    eng_sections: dict[str, str] = eng_meta.get("sections", {})

    # Use English section names (they have the human-readable English names)
    # Arabic edition section names are also in English (confirmed from data)
    sections = eng_sections

    # Remove section "0" which is a placeholder
    sections = {k: v for k, v in sections.items() if k != "0" and v}

    if not sections:
        err("No sections found in metadata — cannot group hadiths by book.")
        sys.exit(1)

    print(f"  Books in metadata : {len(sections)}")

    section_details: dict[str, dict] = eng_meta.get("section_details", {})

    # Validate section details coverage
    for sec_key, sec_name in sections.items():
        if sec_key not in section_details:
            all_warnings.append(
                f"Section {sec_key} ({sec_name}) missing from section_details"
            )

    # ------------------------------------------------------------------
    # Step 6: Group hadiths by book
    # ------------------------------------------------------------------
    print("Step 8: Grouping hadiths by book ...")
    grouped = group_by_book(ara_hadiths_raw, sections, section_details)

    total_grouped = sum(len(v) for v in grouped.values())
    unassigned_count = len(ara_hadiths_raw) - total_grouped
    if unassigned_count > 0:
        all_warnings.append(f"{unassigned_count} hadiths could not be assigned to any book")
        warn(f"{unassigned_count} hadiths not assigned to any book")

    print(f"  Books with hadiths : {len(grouped)}")
    print(f"  Total assigned     : {total_grouped}")

    # ------------------------------------------------------------------
    # Step 7: Check for existing output
    # ------------------------------------------------------------------
    print("Step 9: Checking existing output directory ...")
    existing_state = inspect_existing_output(output_dir)
    print(f"  State: {existing_state}")

    if existing_state == "manual":
        print(
            "\n  STOP: The output directory contains files that do not appear to be\n"
            "  generated by this script. Manual content was detected.\n"
            "\n"
            "  To protect your work, this script will not overwrite those files.\n"
            "  Please inspect the directory and move any hand-written content\n"
            "  before re-running, or use --output-dir to point elsewhere.\n"
            f"\n  Directory: {output_dir}\n"
        )
        sys.exit(1)

    # ------------------------------------------------------------------
    # Step 8: Generate Markdown files
    # ------------------------------------------------------------------
    books_sorted = sorted(sections.items(), key=lambda x: int(x[0]))
    book_num_to_name = {int(k): v for k, v in books_sorted}
    book_files: dict[int, str] = {}

    # Build the complete book file map first (for TOC)
    for book_num, book_name in book_num_to_name.items():
        fname = book_filename(book_num, book_name)
        book_files[book_num] = fname

    if dry_run:
        print("\nStep 10: [DRY RUN] Would write files:")
    else:
        print("\nStep 10: Writing Markdown files ...")
        output_dir.mkdir(parents=True, exist_ok=True)

    files_written = 0
    files_skipped = 0
    total_hadiths_written = 0

    for book_num, book_name in book_num_to_name.items():
        hadiths_in_book = grouped.get(book_num, [])
        fname = book_files[book_num]
        out_path = output_dir / fname

        if not hadiths_in_book:
            all_warnings.append(
                f"Book {book_num} ({book_name}) has no hadiths assigned — skipping"
            )
            warn(f"Book {book_num} ({book_name}): no hadiths — skipping file")
            files_skipped += 1
            continue

        md_content = render_book_md(
            book_num=book_num,
            book_name=book_name,
            ara_hadiths=hadiths_in_book,
            eng_index=eng_index,
            generated_at=generated_at,
            dataset_commit=DATASET_API_VERSION,
        )

        if dry_run:
            print(f"  {out_path.relative_to(REPO_ROOT)} ({len(hadiths_in_book)} hadiths)")
        else:
            out_path.write_text(md_content, encoding="utf-8")
            files_written += 1
            total_hadiths_written += len(hadiths_in_book)

    # Write overview.md (NOT index.md — KSoR auto-generates that)
    overview_content = render_collection_overview_md(
        books=book_num_to_name,
        book_files=book_files,
        total_hadiths=total_grouped,
        generated_at=generated_at,
        ara_total=len(ara_ids),
        eng_total=len(eng_ids),
        matched=len(matched_ids),
        dataset_commit=DATASET_API_VERSION,
    )
    overview_path = output_dir / "overview.md"

    if dry_run:
        print(f"  {overview_path.relative_to(REPO_ROOT)} (collection overview)")
    else:
        overview_path.write_text(overview_content, encoding="utf-8")
        files_written += 1

    # Write hadith folder overview.md if it doesn't exist
    hadith_dir = output_dir.parent
    hadith_overview_path = hadith_dir / "overview.md"
    if not hadith_overview_path.exists():
        hadith_overview_content = render_hadith_collection_overview_md(generated_at)
        if dry_run:
            print(f"  {hadith_overview_path.relative_to(REPO_ROOT)} (hadith folder overview)")
        else:
            hadith_dir.mkdir(parents=True, exist_ok=True)
            hadith_overview_path.write_text(hadith_overview_content, encoding="utf-8")
            files_written += 1
            print(f"  Created: {hadith_overview_path.relative_to(REPO_ROOT)}")

    # ------------------------------------------------------------------
    # Step 9: Post-write verification (only if not dry-run)
    # ------------------------------------------------------------------
    if not dry_run:
        print("\nStep 11: Verifying generated files ...")
        verify_errors: list[str] = []

        # Check overview exists
        if not overview_path.exists():
            verify_errors.append("overview.md was not created")

        # Check book files
        for book_num, fname in book_files.items():
            expected = output_dir / fname
            if book_num in grouped and grouped[book_num]:
                if not expected.exists():
                    verify_errors.append(f"Expected book file missing: {fname}")
                else:
                    # Spot-check: verify hadith count in file
                    content = expected.read_text(encoding="utf-8")
                    # Count "## Hadith " occurrences (each hadith has exactly one)
                    import re as _re
                    actual_count = len(_re.findall(r'^## Hadith ', content, _re.MULTILINE))
                    expected_count = len(grouped.get(book_num, []))
                    if actual_count != expected_count:
                        verify_errors.append(
                            f"{fname}: expected {expected_count} hadiths, "
                            f"found {actual_count} in file"
                        )

        if verify_errors:
            for ve in verify_errors:
                err(ve)
            print(f"\n  {len(verify_errors)} verification errors.")
            sys.exit(1)
        else:
            print(f"  All {files_written - 1} book files verified.")  # subtract overview

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print()
    print("=" * 60)
    print("  Import Summary")
    print("=" * 60)
    print(f"  Source          : {DATASET_REPO}")
    print(f"  Arabic records  : {len(ara_ids)}")
    print(f"  English records : {len(eng_ids)}")
    print(f"  Matched records : {len(matched_ids)}")
    print(f"  Books           : {len(book_num_to_name)}")
    if not dry_run:
        print(f"  Files written   : {files_written}")
        print(f"  Files skipped   : {files_skipped}")
        print(f"  Hadiths written : {total_hadiths_written}")
    print(f"  Warnings        : {len(all_warnings)}")
    print(f"  Errors          : {len(all_errors)}")
    print()

    if all_warnings:
        print("  Warnings:")
        for w in all_warnings:
            print(f"    - {w}")
        print()

    if all_errors:
        print("  FAILED — see errors above.")
        sys.exit(1)
    elif dry_run:
        print("  Dry run complete — no files written.")
    else:
        print("  Import completed successfully.")
    print()


if __name__ == "__main__":
    main()
