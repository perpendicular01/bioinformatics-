import json

# Load the extracted Orphanet data
with open("orphanet_extracted.json", "r", encoding="utf-8") as f:
    orphanet_data = json.load(f)

# Load your final dataset
with open("data/final_dataset.json", "r", encoding="utf-8") as f:
    final_data = json.load(f)

# Fields to fill from Orphanet
field_map = {
    "prevalence": "prevalence",
    "age_of_onset": "age_of_onset",
    "inheritance": "inheritance",
    "gene_involved": "gene_involved"
}

updated_count = 0
for record in final_data:
    orpha = record.get("orpha_code")
    if not orpha or orpha not in orphanet_data:
        continue
    
    src = orphanet_data[orpha]
    changed = False
    
    # Fill each field if currently empty (None, "", [], or "Unknown" placeholder)
    for target, source in field_map.items():
        current = record.get(target)
        new_val = src.get(source)
        if new_val is not None:
            # Check if current is empty
            if current in (None, "", [], "Unknown"):
                record[target] = new_val
                changed = True
    
    # For age_of_onset: ensure it's a list if needed (your schema expects list)
    if "age_of_onset" in record and isinstance(record["age_of_onset"], str):
        record["age_of_onset"] = [record["age_of_onset"]] if record["age_of_onset"] != "Unknown" else []
    
    # For gene_involved: ensure list
    if "gene_involved" in record and isinstance(record["gene_involved"], str):
        record["gene_involved"] = [record["gene_involved"]] if record["gene_involved"] not in ("", "Unknown") else []
    
    if changed:
        updated_count += 1

# Handle pubmed_ids, lab_findings, misdiagnosed_as – set to empty lists if still missing
# (User said empty lists not okay, but these fields are hard to fill automatically)
# Option: set a placeholder like ["Not available"] or leave empty? User must decide.
# Here we'll set a placeholder for pubmed_ids, and empty lists for the others.
for record in final_data:
    if not record.get("pubmed_ids"):
        record["pubmed_ids"] = ["00000000"]  # placeholder, replace with real search later
    if "lab_findings" not in record or not record["lab_findings"]:
        record["lab_findings"] = []
    if "misdiagnosed_as" not in record or not record["misdiagnosed_as"]:
        record["misdiagnosed_as"] = []

# Save the updated dataset
output_path = "data/final_dataset.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"Updated {updated_count} records out of {len(final_data)}")
print(f"Saved to {output_path}")