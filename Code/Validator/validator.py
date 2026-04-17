"""
utils/validator.py
==================
Stage 6 — Validates the final dataset and prints a quality report.

Checks:
  1. Required fields present and non-empty
  2. Symptom count per disease (minimum 3 for valid scenario generation)
  3. rare/common balance
  4. Fields with highest missing rates (so you know what to fix)
  5. Exports a quality report JSON

This report is useful for your pre-defence:
  You can show your committee exactly how complete the dataset is.
"""

import json
from collections import defaultdict


class DatasetValidator:

    def __init__(self, rare_required_fields: list[str], common_required_fields: list[str]):
        self.rare_required_fields = rare_required_fields
        self.common_required_fields = common_required_fields

    def validate(self, dataset: list[dict]) -> dict:
        """
        Runs all validation checks and returns a report dict.
        """
        total = len(dataset)
        rare_count   = sum(1 for d in dataset if d.get("disease_category") == "rare")
        common_count = sum(1 for d in dataset if d.get("disease_category") == "common")

        # Field completeness analysis
        field_missing = defaultdict(int)
        all_fields = list(dataset[0].keys()) if dataset else []

        invalid_records = []

        for i, disease in enumerate(dataset):
            missing_required = []
            
            category = disease.get("disease_category")
            if category == "rare":
                req_fields = self.rare_required_fields
            else:
                req_fields = self.common_required_fields

            for field in req_fields:
                val = disease.get(field)
                if not val or (isinstance(val, list) and len(val) == 0):
                    missing_required.append(field)

            if missing_required:
                invalid_records.append({
                    "index"          : i,
                    "disease_name"   : disease.get("disease_name", "UNKNOWN"),
                    "missing_fields" : missing_required,
                })

            # Count missing for all fields
            for field in all_fields:
                val = disease.get(field)
                if val is None or val == "" or val == []:
                    field_missing[field] += 1

        # Symptom count distribution
        symptom_counts = [len(d.get("symptoms", [])) for d in dataset]
        low_symptom = sum(1 for c in symptom_counts if c < 3)

        # Field completeness %
        field_completeness = {
            field: round(100 * (1 - field_missing[field] / total), 1)
            for field in all_fields
        }

        report = {
            "summary": {
                "total_diseases"    : total,
                "rare_diseases"     : rare_count,
                "common_diseases"   : common_count,
                "valid_records"     : total - len(invalid_records),
                "invalid_records"   : len(invalid_records),
                "low_symptom_count" : low_symptom,   # < 3 symptoms
            },
            "field_completeness_pct": field_completeness,
            "invalid_record_details": invalid_records[:20],  # show first 20
        }

        # Save report
        with open("data/processed/quality_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report

    def print_report(self, report: dict):
        s = report["summary"]
        print(f"\n  {'─'*45}")
        print(f"  DATASET QUALITY REPORT")
        print(f"  {'─'*45}")
        print(f"  Total diseases      : {s['total_diseases']}")
        print(f"  Rare                : {s['rare_diseases']}")
        print(f"  Common              : {s['common_diseases']}")
        print(f"  Valid records       : {s['valid_records']}")
        print(f"  Invalid records     : {s['invalid_records']}")
        print(f"  Low symptom (<3)    : {s['low_symptom_count']}")
        print(f"\n  Field Completeness:")
        for field, pct in report["field_completeness_pct"].items():
            bar  = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            flag = " ⚠" if pct < 70 else ""
            print(f"    {field:<20} {bar} {pct:5.1f}%{flag}")
        print(f"  {'─'*45}")
        print(f"  Full report: data/processed/quality_report.json")
