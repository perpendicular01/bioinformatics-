"""
==============================================================
  Rare Disease Dataset Collection Pipeline
  Thesis: AI-Based Generation and Clinical Validation of
          Rare Disease Scenarios Using BioGPT
==============================================================
  Sources  : Orphanet, OMIM, PubMed
  Target   : 400 rare + 100 common diseases → 500 total
  Output   : data/final_dataset.json
==============================================================

  HOW TO RUN:
    1. pip install requests beautifulsoup4 lxml tqdm
    2. Get free NCBI API key: https://www.ncbi.nlm.nih.gov/account/
    3. Set your key in config.py
    4. python pipeline.py

  PIPELINE STAGES:
    Stage 1 → Fetch 400 rare diseases from Orphanet
    Stage 2 → Fetch 100 common diseases from OMIM
    Stage 3 → Enrich all 500 with OMIM genetic data
    Stage 4 → Enrich all 500 with PubMed case report data
    Stage 5 → Merge + deduplicate into final JSON
==============================================================
"""

import json
import os
import time
from pathlib import Path

from orphanet_scraper import OrphanetScraper
from omim_scraper import OMIMScraper
from pubmed_scraper import PubMedScraper
from merger import DataMerger
from validator import DatasetValidator
import config

# ── Output directories ──────────────────────────────────────
Path("data/raw/orphanet").mkdir(parents=True, exist_ok=True)
Path("data/raw/omim").mkdir(parents=True, exist_ok=True)
Path("data/raw/pubmed").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("data/logs").mkdir(parents=True, exist_ok=True)


def run_pipeline():
    print("\n" + "="*60)
    print("  DISEASE DATASET COLLECTION PIPELINE")
    print("="*60)

    # ── STAGE 1: Orphanet → 400 Rare Diseases ───────────────
    print("\n[STAGE 1] Fetching rare diseases from Orphanet...")
    orphanet = OrphanetScraper(
        api_key=config.ORPHANET_API_KEY,
        output_dir="data/raw/orphanet",
        target_count=400
    )
    rare_diseases = orphanet.fetch_all()
    print(f"  [SUCCESS] Collected {len(rare_diseases)} rare diseases from Orphanet")

    # ── STAGE 2: OMIM → 100 Common Diseases ─────────────────
    print("\n[STAGE 2] Fetching common diseases from OMIM...")
    omim = OMIMScraper(
        api_key=config.NCBI_API_KEY,
        output_dir="data/raw/omim",
        target_count=100,
        mode="common"          # switches OMIM to common disease query set
    )
    common_diseases = omim.fetch_common_diseases()
    print(f"  [SUCCESS] Collected {len(common_diseases)} common diseases from OMIM")

    # ── STAGE 3: OMIM Enrichment → Genetic data for rare ────
    print("\n[STAGE 3] Enriching rare diseases with OMIM genetic data...")
    omim_enricher = OMIMScraper(
        api_key=config.NCBI_API_KEY,
        output_dir="data/raw/omim",
        mode="enrich"
    )
    rare_enriched = omim_enricher.enrich_with_genetics(rare_diseases)
    print(f"  [SUCCESS] Enriched {len(rare_enriched)} rare diseases with gene/inheritance data")

    # ── STAGE 4: PubMed Enrichment → Case report data ───────
    print("\n[STAGE 4] Enriching all diseases with PubMed case reports...")
    pubmed = PubMedScraper(
        api_key=config.NCBI_API_KEY,
        output_dir="data/raw/pubmed",
        max_papers_per_disease=config.MAX_PUBMED_PAPERS
    )
    all_diseases = rare_enriched + common_diseases
    all_enriched = pubmed.enrich_all(all_diseases)
    print(f"  [SUCCESS] PubMed enrichment complete for {len(all_enriched)} diseases")

    # ── STAGE 5: Merge + Deduplicate ────────────────────────
    print("\n[STAGE 5] Merging and deduplicating...")
    merger = DataMerger()
    final_dataset = merger.merge(all_enriched)
    print(f"  [SUCCESS] Final dataset: {len(final_dataset)} unique diseases")

    # ── STAGE 6: Validate ───────────────────────────────────
    print("\n[STAGE 6] Validating dataset completeness...")
    validator = DatasetValidator(
        rare_required_fields=config.RARE_REQUIRED_FIELDS,
        common_required_fields=config.COMMON_REQUIRED_FIELDS
    )
    report = validator.validate(final_dataset)
    validator.print_report(report)

    # ── Save Final Output ────────────────────────────────────
    output_path = "data/final_dataset.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_dataset, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  PIPELINE COMPLETE")
    print(f"  Output : {output_path}")
    print(f"  Total  : {len(final_dataset)} diseases")
    print(f"  Rare   : {sum(1 for d in final_dataset if d.get('disease_category') == 'rare')}")
    print(f"  Common : {sum(1 for d in final_dataset if d.get('disease_category') == 'common')}")
    print(f"{'='*60}\n")

    return final_dataset


if __name__ == "__main__":
    run_pipeline()
