import json

# Load the full Orphanet data (with synonyms and genes)
with open("orphanet_full.json", "r", encoding="utf-8") as f:
    orphanet = json.load(f)

# Load your current filled dataset (from previous merge)
with open("data/final_dataset_filled.json", "r", encoding="utf-8") as f:
    final = json.load(f)

# Fill missing fields from Orphanet
for rec in final:
    orpha = rec.get("orpha_code")
    if orpha and orpha in orphanet:
        src = orphanet[orpha]
        # Fill synonyms if missing
        if not rec.get("synonyms") and src.get("synonyms"):
            rec["synonyms"] = src["synonyms"]
        # Fill gene_involved if missing
        if not rec.get("gene_involved") and src.get("gene_involved"):
            rec["gene_involved"] = src["gene_involved"]
        # Also ensure prevalence, age_of_onset, inheritance are filled (though already done)
        if not rec.get("prevalence") and src.get("prevalence"):
            rec["prevalence"] = src["prevalence"]
        if not rec.get("age_of_onset") and src.get("age_of_onset"):
            rec["age_of_onset"] = src["age_of_onset"]
        if not rec.get("inheritance") and src.get("inheritance"):
            rec["inheritance"] = src["inheritance"]

# After merging, set placeholders for any remaining empty required fields
for rec in final:
    if not rec.get("synonyms"):
        rec["synonyms"] = ["No synonyms"]
    if not rec.get("gene_involved"):
        rec["gene_involved"] = ["None reported"]
    if not rec.get("age_of_onset") or rec["age_of_onset"] == "Unknown":
        rec["age_of_onset"] = ["Unknown"]
    elif isinstance(rec["age_of_onset"], str):
        rec["age_of_onset"] = [rec["age_of_onset"]]
    if not rec.get("pubmed_ids"):
        rec["pubmed_ids"] = ["00000000"]  # placeholder
    # Ensure lab_findings and misdiagnosed_as exist (empty lists allowed)
    if "lab_findings" not in rec:
        rec["lab_findings"] = []
    if "misdiagnosed_as" not in rec:
        rec["misdiagnosed_as"] = []

# Save the final ready dataset
output_path = "data/final_dataset_ready.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)

print(f"Final dataset saved to {output_path}")
print(f"Total records: {len(final)}")