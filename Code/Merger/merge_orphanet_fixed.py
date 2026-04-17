import json

# Load Orphanet extracted data
with open("orphanet_extracted.json", "r", encoding="utf-8") as f:
    orphanet_data = json.load(f)

# Load your original final_dataset.json
with open("data/final_dataset.json", "r", encoding="utf-8") as f:
    final_data = json.load(f)

updated_count = 0
for record in final_data:
    orpha = record.get("orpha_code")
    if not orpha or orpha not in orphanet_data:
        continue
    
    src = orphanet_data[orpha]
    changed = False
    
    # Fill prevalence
    if record.get("prevalence") in (None, "", [], "Unknown") and src.get("prevalence"):
        record["prevalence"] = src["prevalence"]
        changed = True
    
    # Fill age_of_onset (convert string to list if needed)
    if record.get("age_of_onset") in (None, "", [], "Unknown") and src.get("age_of_onset"):
        age = src["age_of_onset"]
        if isinstance(age, str):
            record["age_of_onset"] = [age]
        else:
            record["age_of_onset"] = age
        changed = True
    
    # Fill inheritance
    if record.get("inheritance") in (None, "", [], "Unknown") and src.get("inheritance"):
        record["inheritance"] = src["inheritance"]
        changed = True
    
    # Fill gene_involved (ensure list)
    if (not record.get("gene_involved") or record["gene_involved"] in ([], "")) and src.get("gene_involved"):
        genes = src["gene_involved"]
        if isinstance(genes, list):
            record["gene_involved"] = genes
        else:
            record["gene_involved"] = [genes]
        changed = True
    
    if changed:
        updated_count += 1

# Set default for pubmed_ids if still empty
for record in final_data:
    if not record.get("pubmed_ids"):
        record["pubmed_ids"] = ["00000000"]  # placeholder
    if "lab_findings" not in record:
        record["lab_findings"] = []
    if "misdiagnosed_as" not in record:
        record["misdiagnosed_as"] = []

# Save merged file
with open("data/final_dataset_filled.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"Updated {updated_count} out of {len(final_data)} records")
print("Saved to data/final_dataset_filled.json")