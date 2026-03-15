# Dictionary Builder

Tools to create a medical dictionary from the UMLS Metathesaurus for use with the Clinical Spell Screener.

## Prerequisites

You need a free UMLS license. Register at https://uts.nlm.nih.gov/uts/

## Option 1: From MRCONSO.RRF (recommended for full coverage)

Download the UMLS Metathesaurus and extract `MRCONSO.RRF` from the META directory.

```bash
pip install pandas tqdm

# Extract terms from 28 clinical vocabularies (SNOMED CT, RxNorm, LOINC, MeSH, etc.)
python extract_umls_terms.py --mrconso /path/to/MRCONSO.RRF --output umls_terms.tsv

# Build the final dictionary (merges UMLS terms + clinical abbreviations)
python build_dictionary.py --umls-terms umls_terms.tsv --output-dir ./output
```

This produces `output/dictionary_combined.txt` — upload this to the screener.

## Option 2: Via UMLS REST API (no large download)

```bash
pip install requests

python extract_umls_api.py \
    --api-key YOUR_UMLS_API_KEY \
    --sab SNOMEDCT_US RXNORM LNC MSH \
    --output umls_terms_api.tsv
```

Slower and less complete, but no multi-GB download required.

## Clinical Abbreviations

`clinical_abbreviations.py` contains 483 curated clinical abbreviations across 11 categories. These are exported as part of the dictionary build, or independently:

```bash
python clinical_abbreviations.py --output clinical_abbreviations.tsv --stats
```
