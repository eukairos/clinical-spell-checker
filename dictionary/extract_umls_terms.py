#!/usr/bin/env python3
"""
extract_umls_terms.py
=====================
Extract clinically relevant terms from the UMLS Metathesaurus (MRCONSO.RRF).

MRCONSO.RRF is a pipe-delimited file with the following columns (0-indexed):
  0  CUI    - Concept Unique Identifier
  1  LAT    - Language
  2  TS     - Term Status (P=Preferred, S=Non-preferred)
  3  LUI    - Lexical Unique Identifier
  4  STT    - String Type (PF=Preferred Form, etc.)
  5  SUI    - String Unique Identifier
  6  ISPREF - Is Preferred (Y/N)
  7  AUI    - Atom Unique Identifier
  8  SAUI   - Source Asserted Atom Identifier
  9  SCUI   - Source Asserted Concept Identifier
  10 SDUI   - Source Asserted Descriptor Identifier
  11 SAB    - Source Abbreviation (vocabulary name)
  12 TTY    - Term Type in Source
  13 CODE   - Source vocabulary code
  14 STR    - String (the actual term text)
  15 SRL    - Source Restriction Level
  16 SUPPRESS - Suppressible flag
  17 CVF    - Content View Flag

For a spellchecker dictionary, we primarily need: SAB, STR, LAT, TTY, SUPPRESS.
"""

import argparse
import csv
import json
import logging
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Default source vocabularies relevant to clinical practice
# ──────────────────────────────────────────────────────────────────────────────
DEFAULT_SABS = [
    # Core clinical terminologies
    "SNOMEDCT_US",  # SNOMED CT US Edition - clinical findings, procedures, body structures
    "RXNORM",       # RxNorm - normalised drug names, ingredients, dose forms
    "LNC",          # LOINC - lab tests, clinical observations, surveys
    "MSH",          # MeSH - Medical Subject Headings (broad biomedical)
    # Diagnosis / procedure coding
    "ICD10CM",      # ICD-10-CM - diagnosis codes
    "ICD10PCS",     # ICD-10-PCS - procedure codes
    "ICD9CM",       # ICD-9-CM - legacy diagnosis/procedure codes (still in records)
    "CPT",          # CPT - outpatient procedure codes
    # Oncology / pathology
    "NCI",          # NCI Thesaurus - oncology, broad biomedical
    # Pharmacology
    "NDFRT",        # National Drug File - Reference Terminology
    "VANDF",        # VA National Drug File
    "ATC",          # Anatomical Therapeutic Chemical classification
    "DRUGBANK",     # DrugBank
    "NDDF",         # National Drug Data File
    "MMSL",         # Multum MediSource Lexicon
    "GS",           # Gold Standard Drug Database
    # Anatomy
    "FMA",          # Foundational Model of Anatomy
    "UWDA",         # University of Washington Digital Anatomist
    # Genetics / genomics
    "HGNC",         # HUGO Gene Nomenclature Committee
    "OMIM",         # Online Mendelian Inheritance in Man
    "GO",           # Gene Ontology
    "HPO",          # Human Phenotype Ontology
    # Adverse events / safety
    "MDR",          # MedDRA - Medical Dictionary for Regulatory Activities
    # Patient-facing
    "MEDLINEPLUS",  # MedlinePlus health topics
    "CHV",          # Consumer Health Vocabulary
    # Clinical data exchange
    "HL7V3.0",      # HL7 Version 3.0
    # Nursing
    "NIC",          # Nursing Interventions Classification
    "NOC",          # Nursing Outcomes Classification
    "NANDA-I",      # NANDA International nursing diagnoses
    # Microbiology
    "NCBI",         # NCBI Taxonomy (organisms)
]

# Term types to EXCLUDE (typically internal/hierarchical, not surface terms)
# These are generally not useful for a spellchecker dictionary
EXCLUDE_TTYS = {
    "AB",    # Abbreviation (we handle these separately with curated list)
    "SY",    # Designated synonym — keep some but they can be noisy
    "IS",    # Obsolete
    "OA",    # Obsolete abbreviation
    "OF",    # Obsolete fully specified name
    "MTH_OA",# Metathesaurus obsolete abbreviation
}

# Term types that are HIGH QUALITY for spellchecking
PREFERRED_TTYS = {
    "PT",    # Preferred Term (designated)
    "FN",    # Full Name
    "MH",    # Main Heading (MeSH)
    "PEP",   # Preferred Entry term
    "ET",    # Entry Term
    "CE",    # Entry term for Supplementary Concept
    "HT",    # Hierarchical term
    "NM",    # Name (MeSH supplementary)
    "SCD",   # Semantic Clinical Drug (RxNorm)
    "SBD",   # Semantic Branded Drug (RxNorm)
    "SCDF",  # Semantic Clinical Drug Form
    "SBDF",  # Semantic Branded Drug Form
    "IN",    # Ingredient (RxNorm)
    "MIN",   # Multiple Ingredients
    "PIN",   # Precise Ingredient
    "BN",    # Brand Name
    "DF",    # Dose Form
    "LN",    # LOINC long common name
    "LC",    # Long common name
    "LO",    # Obsolete long common name — still valid surface forms
    "OSN",   # Official Short Name
    "CN",    # LOINC class name
    "OL",    # Official name (long)
    "ON",    # Official name
    "MTH_PT",# Metathesaurus preferred term
    "HG",    # High-level group term
    "LLT",   # Lowest Level Term (MedDRA)
    "LA",    # Label (for drug products)
    "BD",    # Fully-specified name
    "OP",    # Obsolete preferred — still valid surface forms
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract clinically relevant terms from UMLS MRCONSO.RRF"
    )
    parser.add_argument(
        "--mrconso",
        type=str,
        required=True,
        help="Path to MRCONSO.RRF file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="umls_terms.tsv",
        help="Output TSV file path (default: umls_terms.tsv)",
    )
    parser.add_argument(
        "--sab",
        nargs="+",
        default=None,
        help="Source vocabularies to include (default: comprehensive clinical set)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        default="ENG",
        help="Language filter (default: ENG)",
    )
    parser.add_argument(
        "--preferred-only",
        action="store_true",
        default=False,
        help="Only include preferred term types (more conservative)",
    )
    parser.add_argument(
        "--include-suppressed",
        action="store_true",
        default=False,
        help="Include suppressed entries (default: exclude)",
    )
    parser.add_argument(
        "--stats-output",
        type=str,
        default=None,
        help="Path to write extraction statistics JSON",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500_000,
        help="Lines to process per chunk (for memory management)",
    )
    return parser.parse_args()


def validate_mrconso(path: str) -> bool:
    """Quick validation that the file looks like MRCONSO.RRF."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        first_line = f.readline()
    fields = first_line.strip().split("|")
    if len(fields) < 18:
        logger.error(
            f"Expected ≥18 pipe-delimited fields, got {len(fields)}. "
            "Is this a valid MRCONSO.RRF?"
        )
        return False
    # Check that field 1 looks like a language code
    if len(fields[1]) not in (2, 3):
        logger.warning(f"Field 1 = '{fields[1]}' — unexpected language code format")
    return True


def extract_terms(args):
    """
    Stream through MRCONSO.RRF, filter, and collect unique terms.

    Returns:
        terms_by_source: dict[str, set[str]] — unique strings per source
        term_info: dict[str, dict] — metadata per unique string
    """
    sabs = set(args.sab) if args.sab else set(DEFAULT_SABS)
    lang = args.lang

    logger.info(f"Filtering for {len(sabs)} source vocabularies, language={lang}")
    logger.info(f"Source vocabularies: {sorted(sabs)}")

    terms_by_source = defaultdict(set)  # SAB -> set of strings
    term_metadata = {}  # string -> {sources, cuis, ttys}
    line_count = 0
    kept_count = 0
    skipped_suppress = 0
    skipped_lang = 0
    skipped_sab = 0
    skipped_tty = 0

    try:
        from tqdm import tqdm

        # Estimate line count for progress bar
        file_size = os.path.getsize(args.mrconso)
        estimated_lines = file_size // 200  # rough estimate
        progress = tqdm(total=estimated_lines, desc="Processing MRCONSO.RRF", unit="lines")
    except ImportError:
        progress = None
        logger.info("Install tqdm for progress bars: pip install tqdm")

    with open(args.mrconso, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line_count += 1

            if progress and line_count % 100_000 == 0:
                progress.update(100_000)

            fields = line.rstrip("\n").split("|")
            if len(fields) < 18:
                continue

            lat = fields[1]   # Language
            sab = fields[11]  # Source vocabulary
            tty = fields[12]  # Term type
            string = fields[14]  # The actual term
            suppress = fields[16]  # Suppressible flag
            cui = fields[0]   # Concept ID

            # ── Filter: language ──
            if lat != lang:
                skipped_lang += 1
                continue

            # ── Filter: source vocabulary ──
            if sab not in sabs:
                skipped_sab += 1
                continue

            # ── Filter: suppressed entries ──
            if not args.include_suppressed and suppress in ("O", "E", "Y"):
                skipped_suppress += 1
                continue

            # ── Filter: term type ──
            if args.preferred_only and tty not in PREFERRED_TTYS:
                skipped_tty += 1
                continue
            elif tty in EXCLUDE_TTYS:
                skipped_tty += 1
                continue

            # ── Filter: basic string quality ──
            string = string.strip()
            if not string:
                continue
            if len(string) < 2:
                continue
            # Skip strings that are purely numeric (codes, not terms)
            if string.isdigit():
                continue

            # ── Collect ──
            terms_by_source[sab].add(string)
            kept_count += 1

            if string not in term_metadata:
                term_metadata[string] = {
                    "sources": set(),
                    "cuis": set(),
                    "ttys": set(),
                }
            term_metadata[string]["sources"].add(sab)
            term_metadata[string]["cuis"].add(cui)
            term_metadata[string]["ttys"].add(tty)

    if progress:
        progress.close()

    logger.info(f"Processed {line_count:,} lines total")
    logger.info(f"Kept {kept_count:,} term instances")
    logger.info(f"Unique strings: {len(term_metadata):,}")
    logger.info(f"Skipped — language: {skipped_lang:,}")
    logger.info(f"Skipped — source: {skipped_sab:,}")
    logger.info(f"Skipped — suppressed: {skipped_suppress:,}")
    logger.info(f"Skipped — term type: {skipped_tty:,}")

    return terms_by_source, term_metadata


def write_output(term_metadata: dict, output_path: str):
    """Write terms to TSV with metadata columns."""
    logger.info(f"Writing {len(term_metadata):,} unique terms to {output_path}")

    # Sort by number of sources (descending), then alphabetically
    sorted_terms = sorted(
        term_metadata.items(),
        key=lambda x: (-len(x[1]["sources"]), x[0].lower()),
    )

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["term", "source_count", "sources", "cui_count", "sample_cui", "ttys"])

        for term, meta in sorted_terms:
            sources = sorted(meta["sources"])
            cuis = sorted(meta["cuis"])
            ttys = sorted(meta["ttys"])
            writer.writerow([
                term,
                len(sources),
                "|".join(sources),
                len(cuis),
                cuis[0] if cuis else "",
                "|".join(ttys),
            ])

    logger.info(f"Output written to {output_path}")


def write_stats(terms_by_source: dict, term_metadata: dict, stats_path: str):
    """Write extraction statistics to JSON."""
    stats = {
        "total_unique_terms": len(term_metadata),
        "terms_per_source": {
            sab: len(terms) for sab, terms in sorted(terms_by_source.items())
        },
        "multi_source_terms": sum(
            1 for meta in term_metadata.values() if len(meta["sources"]) > 1
        ),
        "single_source_terms": sum(
            1 for meta in term_metadata.values() if len(meta["sources"]) == 1
        ),
        "top_20_by_source_count": [
            {"term": t, "sources": len(m["sources"])}
            for t, m in sorted(
                term_metadata.items(),
                key=lambda x: -len(x[1]["sources"]),
            )[:20]
        ],
    }

    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    logger.info(f"Statistics written to {stats_path}")


def main():
    args = parse_args()

    # Validate input
    if not os.path.isfile(args.mrconso):
        logger.error(f"MRCONSO.RRF not found at: {args.mrconso}")
        logger.error(
            "Download the UMLS Metathesaurus from https://www.nlm.nih.gov/research/umls/ "
            "and extract MRCONSO.RRF from the META directory."
        )
        sys.exit(1)

    if not validate_mrconso(args.mrconso):
        sys.exit(1)

    # Extract
    terms_by_source, term_metadata = extract_terms(args)

    if not term_metadata:
        logger.error("No terms extracted. Check your filters.")
        sys.exit(1)

    # Write outputs
    write_output(term_metadata, args.output)

    stats_path = args.stats_output or args.output.replace(".tsv", "_stats.json")
    write_stats(terms_by_source, term_metadata, stats_path)

    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"  Unique terms extracted:  {len(term_metadata):>10,}")
    print(f"  Source vocabularies:     {len(terms_by_source):>10}")
    print(f"  Multi-source terms:      {sum(1 for m in term_metadata.values() if len(m['sources']) > 1):>10,}")
    print()
    print("  Terms per source:")
    for sab in sorted(terms_by_source, key=lambda s: -len(terms_by_source[s])):
        print(f"    {sab:<20s} {len(terms_by_source[sab]):>10,}")
    print("=" * 60)


if __name__ == "__main__":
    main()
