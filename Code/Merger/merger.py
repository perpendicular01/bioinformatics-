"""
utils/merger.py
===============
Stage 5 — Merges rare + common disease records and deduplicates.

Deduplication strategy (in priority order):
  1. Same orpha_code           → definite duplicate
  2. Same omim_id              → definite duplicate
  3. Same icd_10_code          → likely duplicate (flag + keep first)
  4. Same normalized name      → likely duplicate (flag + keep first)

Also handles:
  - Normalizing disease names (strip extra whitespace, fix casing)
  - Removing records with empty disease_name
  - Ensuring all required schema fields are present (fills with defaults)
"""

import re
import json
from pathlib import Path


# Full schema with default values
# Every record in the final dataset will have ALL these fields
SCHEMA_DEFAULTS = {
    "orpha_code"      : None,
    "omim_id"         : None,
    "disease_name"    : "",
    "synonyms"        : [],
    "disease_type"    : "",
    "disease_category": "rare",
    "icd_10_code"     : "",
    "prevalence"      : "",
    "age_of_onset"    : [],
    "gender_bias"     : "No data",
    "symptoms"        : [],
    "gene_involved"   : [],
    "inheritance"     : None,
    "lab_findings"    : [],
    "misdiagnosed_as" : [],
    "pubmed_ids"      : [],
}


class DataMerger:

    def merge(self, all_diseases: list[dict]) -> list[dict]:
        """
        Deduplicates and normalizes the combined disease list.
        Returns clean final dataset list.
        """
        print(f"    Input records: {len(all_diseases)}")

        # Step 1: Fill missing schema fields with defaults
        normalized = [self._apply_defaults(d) for d in all_diseases]

        # Step 2: Remove records without a name
        normalized = [d for d in normalized if d["disease_name"].strip()]
        print(f"    After name filter: {len(normalized)}")

        # Step 3: Deduplicate
        deduplicated = self._deduplicate(normalized)
        print(f"    After deduplication: {len(deduplicated)}")

        # Step 4: Normalize disease names
        for d in deduplicated:
            d["disease_name"] = self._normalize_name(d["disease_name"])

        # Step 5: Sort — rare diseases first, then common
        deduplicated.sort(
            key=lambda d: (0 if d["disease_category"] == "rare" else 1,
                           d["disease_name"])
        )

        return deduplicated

    def _apply_defaults(self, disease: dict) -> dict:
        """Ensures every field in SCHEMA_DEFAULTS exists in the record."""
        result = dict(SCHEMA_DEFAULTS)  # start with defaults
        result.update(disease)          # overwrite with actual data
        return result

   
    def _normalize_name(self, name: str) -> str:
        """Strips extra whitespace, fixes obvious formatting issues."""
        name = re.sub(r"\s+", " ", name).strip()
        # Title case if all-caps
        if name.isupper():
            name = name.title()
        return name
