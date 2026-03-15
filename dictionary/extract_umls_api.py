#!/usr/bin/env python3
"""
extract_umls_api.py
===================
Alternative extraction method using the UMLS REST API (UTS).
Use this if you don't have the full MRCONSO.RRF download.

Requires:
  - UMLS API key (get from https://uts.nlm.nih.gov/uts/profile)
  - requests library: pip install requests

Limitations:
  - Rate-limited (20 requests/second for authenticated users)
  - Returns paginated results (max 25 per page)
  - Much slower than processing MRCONSO.RRF directly
  - Best used for targeted extraction of specific vocabularies or concepts

Recommended workflow:
  1. Use this script for smaller targeted extractions
  2. For full vocabulary extraction, download MRCONSO.RRF instead
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from typing import Optional

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_URL = "https://uts-ws.nlm.nih.gov/rest"
AUTH_URL = "https://utslogin.nlm.nih.gov/cas/v1/api-key"


class UMLSClient:
    """Client for the UMLS REST API."""

    def __init__(self, api_key: str, rate_limit: float = 0.1):
        self.api_key = api_key
        self.rate_limit = rate_limit  # seconds between requests
        self._last_request_time = 0

    def _rate_limit_wait(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self._last_request_time = time.time()

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make authenticated GET request to UMLS API."""
        self._rate_limit_wait()

        if params is None:
            params = {}
        params["apiKey"] = self.api_key

        url = f"{BASE_URL}/{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                logger.error("Authentication failed. Check your UMLS API key.")
            elif response.status_code == 429:
                logger.warning("Rate limited. Backing off...")
                time.sleep(5)
                return self._get(endpoint, params)
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def search(
        self,
        query: str,
        source: Optional[str] = None,
        search_type: str = "words",
        page_size: int = 25,
        max_pages: int = 100,
    ) -> list:
        """
        Search UMLS for terms.

        Args:
            query: Search string
            source: Source vocabulary filter (e.g., "SNOMEDCT_US")
            search_type: "exact", "words", "leftTruncation", "rightTruncation"
            page_size: Results per page (max 25)
            max_pages: Maximum pages to retrieve

        Returns:
            List of result dicts with keys: ui, name, rootSource, uri
        """
        params = {
            "string": query,
            "searchType": search_type,
            "pageSize": min(page_size, 25),
        }
        if source:
            params["sabs"] = source

        all_results = []
        page = 1

        while page <= max_pages:
            params["pageNumber"] = page
            data = self._get("search/current", params)

            result = data.get("result", {})
            results = result.get("results", [])

            if not results or (len(results) == 1 and results[0].get("ui") == "NONE"):
                break

            all_results.extend(results)
            logger.debug(f"Page {page}: {len(results)} results")

            # Check if more pages
            total_count = result.get("recCount", 0)
            if len(all_results) >= total_count:
                break

            page += 1

        return all_results

    def get_atoms(
        self,
        cui: str,
        source: Optional[str] = None,
        preferred_only: bool = False,
        language: str = "ENG",
    ) -> list:
        """
        Get atoms (surface forms) for a CUI.

        Args:
            cui: Concept Unique Identifier (e.g., "C0027051")
            source: Filter by source vocabulary
            preferred_only: Only return preferred atoms
            language: Language filter

        Returns:
            List of atom dicts
        """
        params = {
            "language": language,
            "pageSize": 25,
        }
        if source:
            params["sabs"] = source

        all_atoms = []
        page = 1

        while True:
            params["pageNumber"] = page
            data = self._get(f"content/current/CUI/{cui}/atoms", params)

            result = data.get("result", [])
            if not result:
                break

            for atom in result:
                if preferred_only and atom.get("obsolete") == "true":
                    continue
                all_atoms.append({
                    "name": atom.get("name", ""),
                    "source": atom.get("rootSource", ""),
                    "termType": atom.get("termType", ""),
                    "language": atom.get("language", ""),
                    "cui": cui,
                })

            if len(result) < 25:
                break
            page += 1

        return all_atoms

    def get_source_atoms(
        self,
        source: str,
        page_size: int = 25,
        max_results: int = 10000,
    ) -> list:
        """
        Browse atoms from a specific source vocabulary.
        Uses content endpoint to iterate through source concepts.

        Note: This is slow for large vocabularies. Use MRCONSO.RRF for full extraction.
        """
        logger.warning(
            f"Extracting from {source} via API. This is slow for large vocabularies. "
            "Consider downloading MRCONSO.RRF for full extraction."
        )

        # Search with wildcards to get broad coverage
        search_terms = [
            "a*", "b*", "c*", "d*", "e*", "f*", "g*", "h*", "i*", "j*",
            "k*", "l*", "m*", "n*", "o*", "p*", "q*", "r*", "s*", "t*",
            "u*", "v*", "w*", "x*", "y*", "z*",
        ]

        all_terms = set()
        for prefix in search_terms:
            if len(all_terms) >= max_results:
                logger.info(f"Reached max_results ({max_results}). Stopping.")
                break

            results = self.search(
                query=prefix,
                source=source,
                search_type="rightTruncation",
                max_pages=10,
            )

            for r in results:
                name = r.get("name", "").strip()
                if name:
                    all_terms.add(name)

            logger.info(f"  {prefix}: {len(results)} results, total unique: {len(all_terms)}")

        return list(all_terms)


def extract_via_api(args):
    """Main extraction workflow using UMLS API."""
    client = UMLSClient(args.api_key, rate_limit=args.rate_limit)

    # Test authentication
    logger.info("Testing API authentication...")
    try:
        test = client.search("heart", max_pages=1)
        if not test:
            logger.error("API returned no results. Check your API key.")
            sys.exit(1)
        logger.info("Authentication successful.")
    except Exception as e:
        logger.error(f"API authentication failed: {e}")
        sys.exit(1)

    sources = args.sab
    all_terms = {}  # term -> set of sources

    for source in sources:
        logger.info(f"\nExtracting from {source}...")
        terms = client.get_source_atoms(
            source=source,
            max_results=args.max_per_source,
        )

        for term in terms:
            if term not in all_terms:
                all_terms[term] = set()
            all_terms[term].add(source)

        logger.info(f"  {source}: {len(terms)} terms extracted")

    # Write output
    logger.info(f"\nWriting {len(all_terms)} unique terms to {args.output}")
    with open(args.output, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["term", "source_count", "sources", "cui_count", "sample_cui", "ttys"])

        for term in sorted(all_terms, key=str.lower):
            sources_list = sorted(all_terms[term])
            writer.writerow([
                term,
                len(sources_list),
                "|".join(sources_list),
                0,  # CUI count not available via this method
                "",  # No CUI from search results
                "",  # No TTY from search results
            ])

    # Summary
    print("\n" + "=" * 60)
    print("API EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"  Unique terms extracted:  {len(all_terms):>10,}")
    print(f"  Source vocabularies:     {len(sources):>10}")
    print()
    print("  NOTE: API extraction is limited compared to full MRCONSO.RRF.")
    print("  For comprehensive extraction, download the UMLS Metathesaurus.")
    print("=" * 60)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract UMLS terms via REST API"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        required=True,
        help="UMLS API key (from https://uts.nlm.nih.gov/uts/profile)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="umls_terms_api.tsv",
        help="Output TSV file",
    )
    parser.add_argument(
        "--sab",
        nargs="+",
        default=["SNOMEDCT_US", "RXNORM", "LNC", "MSH"],
        help="Source vocabularies to extract",
    )
    parser.add_argument(
        "--max-per-source",
        type=int,
        default=50000,
        help="Maximum terms per source (default: 50000)",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=0.1,
        help="Seconds between API requests (default: 0.1)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    extract_via_api(args)
