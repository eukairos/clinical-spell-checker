#!/usr/bin/env python3
"""
build_dictionary.py
===================
Build a spellchecker-ready medical dictionary by merging:
  1. UMLS-extracted terms (from extract_umls_terms.py)
  2. Curated clinical abbreviations (from clinical_abbreviations.py)

Produces multiple output formats for different spellchecker use cases.

Output files:
  - dictionary_unigrams.txt      : one token per line (for token-level checking)
  - dictionary_multiword.txt     : multi-word terms preserved (for phrase checking)
  - dictionary_abbreviations.tsv : abbreviation → expansion mapping
  - dictionary_combined.txt      : flat union of all tokens
  - build_report.json            : statistics and metadata
"""

import argparse
import csv
import json
import logging
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from clinical_abbreviations import (
    get_abbreviation_tokens,
    get_abbreviations,
    get_expansion_tokens,
    write_abbreviations_tsv,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Text normalisation utilities
# ──────────────────────────────────────────────────────────────────────────────

# Pattern for strings that are mostly non-alphanumeric (likely noise)
NOISE_PATTERN = re.compile(r"^[^a-zA-Z]*$")

# Pattern for UMLS-style semantic tags, e.g. "(finding)" "(procedure)"
SEMANTIC_TAG_PATTERN = re.compile(r"\s*\([a-z\s]+\)\s*$")

# Pattern for source-specific codes embedded in terms
CODE_PATTERN = re.compile(r"^[A-Z]\d{2}(\.\d+)?$")  # ICD-style codes

# Common boilerplate strings to exclude
EXCLUDE_STRINGS = {
    "NOS",         # Not Otherwise Specified
    "unspecified",
    "RETIRED",
    "OBSOLETE",
    "DO NOT USE",
}


def normalise_unicode(text: str) -> str:
    """Normalise Unicode to NFC form and replace common variants."""
    text = unicodedata.normalize("NFC", text)
    # Replace common Unicode variants with ASCII equivalents
    replacements = {
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u00b5": "u",   # micro sign → u (for units like ug, uL)
        "\u03bc": "u",   # greek mu → u
        "\u2265": ">=",  # ≥
        "\u2264": "<=",  # ≤
        "\u00b0": " degrees ",  # degree sign
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def clean_term(term: str) -> str:
    """Clean a single term for dictionary inclusion."""
    term = normalise_unicode(term)
    # Remove semantic tags like "(finding)", "(procedure)"
    term = SEMANTIC_TAG_PATTERN.sub("", term)
    # Strip leading/trailing whitespace and punctuation
    term = term.strip().strip(".,;:")
    return term


def is_valid_term(term: str, min_length: int = 2, max_length: int = 100) -> bool:
    """Check if a term is valid for dictionary inclusion."""
    if not term:
        return False
    if len(term) < min_length or len(term) > max_length:
        return False
    # Skip purely numeric strings
    if term.isdigit():
        return False
    # Skip strings with no alphabetic characters
    if NOISE_PATTERN.match(term):
        return False
    # Skip ICD-style codes
    if CODE_PATTERN.match(term):
        return False
    # Skip known boilerplate
    if term.upper() in EXCLUDE_STRINGS:
        return False
    return True


def tokenise_term(term: str) -> list:
    """
    Split a term into individual tokens for unigram dictionary.

    Handles:
    - Hyphenated compounds (keep both hyphenated and split forms)
    - Slash-separated alternatives
    - Parenthetical qualifiers
    """
    tokens = []

    # Remove content in parentheses for cleaner tokenization
    # but keep the parenthetical content as separate tokens
    paren_content = re.findall(r"\(([^)]+)\)", term)
    for pc in paren_content:
        for word in pc.split():
            word = word.strip(".,;:")
            if word and len(word) >= 2:
                tokens.append(word)

    # Remove parenthetical content for main tokenization
    main = re.sub(r"\([^)]*\)", "", term).strip()

    for word in main.split():
        word = word.strip(".,;:()")
        if not word or len(word) < 2:
            continue

        tokens.append(word)

        # If hyphenated, also add the components
        if "-" in word and len(word) > 3:
            parts = word.split("-")
            for part in parts:
                if part and len(part) >= 2:
                    tokens.append(part)

        # If contains slash, add components
        if "/" in word:
            parts = word.split("/")
            for part in parts:
                if part and len(part) >= 2:
                    tokens.append(part)

    return tokens


def load_umls_terms(tsv_path: str) -> tuple:
    """
    Load terms from the UMLS extraction TSV.

    Returns:
        all_terms: set of raw term strings
        source_counts: Counter of terms per source
    """
    all_terms = set()
    source_counts = Counter()

    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            term = row["term"]
            sources = row.get("sources", "").split("|")
            all_terms.add(term)
            for src in sources:
                if src:
                    source_counts[src] += 1

    logger.info(f"Loaded {len(all_terms):,} unique terms from {tsv_path}")
    return all_terms, source_counts


def build_dictionary(args):
    """Main dictionary build pipeline."""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Load UMLS terms ──
    umls_terms = set()
    source_counts = Counter()
    if args.umls_terms and os.path.isfile(args.umls_terms):
        umls_terms, source_counts = load_umls_terms(args.umls_terms)
    else:
        logger.warning(
            "No UMLS terms file provided or file not found. "
            "Building dictionary from abbreviations only."
        )

    # ── Clean UMLS terms ──
    logger.info("Cleaning and validating terms...")
    clean_multiword = set()
    clean_unigrams = set()
    rejected_count = 0

    for raw_term in umls_terms:
        term = clean_term(raw_term)
        if not is_valid_term(term, args.min_length, args.max_length):
            rejected_count += 1
            continue

        # Add the full multi-word term
        clean_multiword.add(term)

        # Tokenise into unigrams
        for token in tokenise_term(term):
            if is_valid_term(token, min_length=2, max_length=50):
                clean_unigrams.add(token)

    logger.info(f"Clean multi-word terms: {len(clean_multiword):,}")
    logger.info(f"Clean unigram tokens: {len(clean_unigrams):,}")
    logger.info(f"Rejected terms: {rejected_count:,}")

    # ── Add abbreviations ──
    abbrev_tokens = set()
    expansion_tokens = set()
    if args.include_abbreviations:
        abbrev_tokens = get_abbreviation_tokens()
        expansion_tokens = get_expansion_tokens()
        logger.info(f"Adding {len(abbrev_tokens)} abbreviation tokens")
        logger.info(f"Adding {len(expansion_tokens)} expansion word tokens")

        # Write abbreviations TSV
        abbrev_path = output_dir / "dictionary_abbreviations.tsv"
        write_abbreviations_tsv(str(abbrev_path))
        logger.info(f"Wrote abbreviations to {abbrev_path}")

    # ── Build case variants ──
    # For a spellchecker, we want both the original casing and lowercase
    all_unigrams = set()
    for token in clean_unigrams | abbrev_tokens | expansion_tokens:
        all_unigrams.add(token)
        # Add lowercase variant (many clinical terms are case-sensitive,
        # so we keep originals but also add lowercase)
        all_unigrams.add(token.lower())

    # Also add the multi-word terms tokenised at lowercase
    for term in clean_multiword:
        for word in term.lower().split():
            word = word.strip(".,;:()")
            if word and len(word) >= 2:
                all_unigrams.add(word)

    logger.info(f"Total unigrams (with case variants): {len(all_unigrams):,}")

    # ── Write outputs ──

    # 1. Unigrams (sorted)
    unigram_path = output_dir / "dictionary_unigrams.txt"
    sorted_unigrams = sorted(all_unigrams, key=str.lower)
    with open(unigram_path, "w", encoding="utf-8") as f:
        for token in sorted_unigrams:
            f.write(token + "\n")
    logger.info(f"Wrote {len(sorted_unigrams):,} unigrams to {unigram_path}")

    # 2. Multi-word terms (sorted)
    multiword_path = output_dir / "dictionary_multiword.txt"
    sorted_multiword = sorted(clean_multiword, key=str.lower)
    with open(multiword_path, "w", encoding="utf-8") as f:
        for term in sorted_multiword:
            f.write(term + "\n")
    logger.info(f"Wrote {len(sorted_multiword):,} multi-word terms to {multiword_path}")

    # 3. Combined flat wordlist (everything)
    combined = all_unigrams.copy()
    # Also add full multi-word terms for phrase-level checking
    for term in clean_multiword:
        combined.add(term.lower())
    for abbr in abbrev_tokens:
        combined.add(abbr)  # Keep original case for abbreviations

    combined_path = output_dir / "dictionary_combined.txt"
    sorted_combined = sorted(combined, key=str.lower)
    with open(combined_path, "w", encoding="utf-8") as f:
        for entry in sorted_combined:
            f.write(entry + "\n")
    logger.info(f"Wrote {len(sorted_combined):,} entries to {combined_path}")

    # 4. Build report
    report = {
        "total_unigrams": len(sorted_unigrams),
        "total_multiword_terms": len(sorted_multiword),
        "total_combined_entries": len(sorted_combined),
        "abbreviations_included": args.include_abbreviations,
        "abbreviation_count": len(abbrev_tokens) if args.include_abbreviations else 0,
        "umls_terms_loaded": len(umls_terms),
        "umls_terms_rejected": rejected_count,
        "source_vocabulary_counts": dict(source_counts.most_common()),
        "filters": {
            "min_length": args.min_length,
            "max_length": args.max_length,
        },
        "output_files": {
            "unigrams": str(unigram_path),
            "multiword": str(multiword_path),
            "combined": str(combined_path),
            "abbreviations": str(output_dir / "dictionary_abbreviations.tsv")
            if args.include_abbreviations
            else None,
        },
    }

    report_path = output_dir / "build_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    logger.info(f"Wrote build report to {report_path}")

    # ── Summary ──
    print("\n" + "=" * 60)
    print("DICTIONARY BUILD SUMMARY")
    print("=" * 60)
    print(f"  Unigram tokens:          {len(sorted_unigrams):>10,}")
    print(f"  Multi-word terms:        {len(sorted_multiword):>10,}")
    print(f"  Combined entries:        {len(sorted_combined):>10,}")
    if args.include_abbreviations:
        print(f"  Clinical abbreviations:  {len(abbrev_tokens):>10}")
    print(f"\n  Output directory: {output_dir}")
    print("=" * 60)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build a medical spellchecker dictionary"
    )
    parser.add_argument(
        "--umls-terms",
        type=str,
        default=None,
        help="Path to UMLS terms TSV (from extract_umls_terms.py)",
    )
    parser.add_argument(
        "--include-abbreviations",
        action="store_true",
        default=True,
        help="Include curated clinical abbreviations (default: True)",
    )
    parser.add_argument(
        "--no-abbreviations",
        action="store_true",
        default=False,
        help="Exclude clinical abbreviations",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Output directory (default: ./output)",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=2,
        help="Minimum term length to include (default: 2)",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=100,
        help="Maximum term length to include (default: 100)",
    )
    args = parser.parse_args()

    if args.no_abbreviations:
        args.include_abbreviations = False

    return args


if __name__ == "__main__":
    args = parse_args()
    build_dictionary(args)
