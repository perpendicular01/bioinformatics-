import json
import os
import re

REQUIRED_FIELDS = [
    "orpha_code", "disease_name", "synonyms", "disease_type",
    "disease_category", "icd_10_code", "prevalence", "age_of_onset",
    "gender_bias", "symptoms", "gene_involved", "inheritance",
    "lab_findings", "misdiagnosed_as", "pubmed_ids"
]

LIST_FIELDS = [
    "synonyms", "age_of_onset", "symptoms", "gene_involved",
    "lab_findings", "misdiagnosed_as", "pubmed_ids"
]

def is_empty(value):
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    return False

def validate_record(record, idx, filename):
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"{filename}[{idx}]: Missing field '{field}'")
        elif is_empty(record[field]):
            errors.append(f"{filename}[{idx}]: Field '{field}' is empty (null, '', or [])")
    
    if "orpha_code" in record and not is_empty(record["orpha_code"]):
        if not record["orpha_code"].startswith("ORPHA:"):
            errors.append(f"{filename}[{idx}]: orpha_code should start with ORPHA:")
    
    for field in LIST_FIELDS:
        if field in record and record[field] is not None and not isinstance(record[field], list):
            errors.append(f"{filename}[{idx}]: '{field}' must be a list")
    
    if "symptoms" in record and not is_empty(record["symptoms"]):
        symptoms = record["symptoms"]
        for i, sym in enumerate(symptoms):
            if not isinstance(sym, dict):
                errors.append(f"{filename}[{idx}]: symptom[{i}] not an object")
            else:
                if "name" not in sym or is_empty(sym.get("name")):
                    errors.append(f"{filename}[{idx}]: symptom[{i}] missing/empty 'name'")
                if "hpo" not in sym or is_empty(sym.get("hpo")):
                    errors.append(f"{filename}[{idx}]: symptom[{i}] missing/empty 'hpo'")
                if "frequency_label" not in sym and "frequency" not in sym:
                    errors.append(f"{filename}[{idx}]: symptom[{i}] missing frequency")
    return errors

def validate_json_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        print(f"{filepath}: Invalid top-level type")
        return
    
    all_errors = []
    for idx, rec in enumerate(data):
        all_errors.extend(validate_record(rec, idx, os.path.basename(filepath)))
    
    error_indices = set()
    for err in all_errors:
        m = re.search(r'\[(\d+)\]', err)
        if m:
            error_indices.add(int(m.group(1)))
    
    print(f"\n=== {filepath} ===")
    print(f"Records: {len(data)}")
    print(f"Records with issues: {len(error_indices)}")
    if all_errors:
        print(f"Total errors: {len(all_errors)}")
        for err in all_errors[:30]:
            print(f"  {err}")
    else:
        print("✓ All records are complete and properly formatted.")

if __name__ == "__main__":
    files_to_check = [
        "data/final_dataset.json",
        "data/raw/pubmed/pubmed_enriched.json",
        "data/raw/omim/omim_common_raw.json",
        "data/raw/omim/omim_enriched.json",
        "data/raw/orphanet/orphanet_raw.json"
    ]
    for f in files_to_check:
        validate_json_file(f)