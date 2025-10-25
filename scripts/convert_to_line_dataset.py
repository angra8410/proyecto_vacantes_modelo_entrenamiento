#!/usr/bin/env python3
"""
scripts/convert_to_line_dataset.py

Convierte data/training_data.jsonl (cada línea: {"text":..., "yaml": ...})
en un dataset a nivel de línea listo para entrenamiento de un clasificador
(line -> label in {role,company,other}).

Salida:
 - data/line_dataset.jsonl      (cada línea: {"line":..., "label":..., "source_hash":..., "source_yaml":...})
 - data/line_dataset.csv        (columns: line,label,source_hash)
 - data/line_dataset_review.jsonl  (ejemplos para revisión manual)

Uso:
  python scripts/convert_to_line_dataset.py
  python scripts/convert_to_line_dataset.py --input data/training_data.jsonl --outdir data

"""
from pathlib import Path
import json
import re
import csv
import hashlib
import unicodedata
import argparse

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r'[·•/\\()\[\]\{\}:,;"“”‘’`~\-–—]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def extract_fields_from_yaml(yaml_text: str):
    cargo = ""
    empresa = ""
    m_c = re.search(r'cargo:\s*"([^"]*)"', yaml_text)
    m_e = re.search(r'empresa:\s*"([^"]*)"', yaml_text)
    if m_c:
        cargo = m_c.group(1).strip()
    if m_e:
        empresa = m_e.group(1).strip()
    return cargo, empresa

def simple_lines(text: str):
    return [l.strip() for l in text.splitlines() if l.strip()]

def sha1_hex(s: str) -> str:
    return hashlib.sha1(s.encode('utf-8')).hexdigest()

def line_contains_target(line_norm: str, target_norm: str) -> bool:
    if not target_norm:
        return False
    if target_norm in line_norm:
        return True
    try:
        if re.search(r'\b' + re.escape(target_norm) + r'\b', line_norm):
            return True
    except re.error:
        pass
    return False

def convert(input_path: Path, outdir: Path, min_examples: int = 0):
    input_path = Path(input_path)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    jsonl_out = outdir / 'line_dataset.jsonl'
    csv_out = outdir / 'line_dataset.csv'
    review_out = outdir / 'line_dataset_review.jsonl'

    total_examples = 0
    label_counts = {"role":0, "company":0, "other":0}
    review_items = []

    with open(input_path, 'r', encoding='utf-8-sig') as fin, \
         open(jsonl_out, 'w', encoding='utf-8') as fout_jsonl, \
         open(csv_out, 'w', encoding='utf-8', newline='') as fout_csv:

        csv_writer = csv.writer(fout_csv)
        csv_writer.writerow(['text','label','source_hash'])

        for i, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"Skipping invalid json line {i}: {e}")
                continue
            src_text = obj.get('text','')
            src_yaml = obj.get('yaml','')
            cargo, empresa = extract_fields_from_yaml(src_yaml)

            src_hash = sha1_hex(src_text)

            lines = simple_lines(src_text)
            if not lines:
                continue

            cargo_norm = normalize_text(cargo)
            empresa_norm = normalize_text(empresa)

            for idx, ln in enumerate(lines):
                ln_norm = normalize_text(ln)
                label = "other"
                if cargo_norm and line_contains_target(ln_norm, cargo_norm):
                    label = "role"
                elif empresa_norm and line_contains_target(ln_norm, empresa_norm):
                    label = "company"
                else:
                    if cargo_norm:
                        cargo_tokens = cargo_norm.split()
                        if all(tok in ln_norm for tok in cargo_tokens[:min(len(cargo_tokens),3)]):
                            label = "role"
                    if empresa_norm and label == "other":
                        empresa_tokens = empresa_norm.split()
                        if all(tok in ln_norm for tok in empresa_tokens[:min(len(empresa_tokens),3)]):
                            label = "company"

                item = {
                    "line": ln,
                    "line_norm": ln_norm,
                    "label": label,
                    "source_hash": src_hash,
                    "source_yaml": src_yaml,
                    "source_index": i,
                    "line_index": idx
                }
                fout_jsonl.write(json.dumps(item, ensure_ascii=False) + "\n")
                csv_writer.writerow([ln, label, src_hash])
                total_examples += 1
                label_counts[label] = label_counts.get(label,0) + 1

                if label == "other" and (cargo_norm or empresa_norm):
                    review_items.append(item)

    with open(review_out, 'w', encoding='utf-8') as frev:
        for it in review_items:
            frev.write(json.dumps(it, ensure_ascii=False) + "\n")

    print("Wrote:", jsonl_out)
    print("Wrote:", csv_out)
    print("Wrote review file:", review_out)
    print("Total line examples:", total_examples)
    print("Label counts:", label_counts)
    print("Review candidates:", len(review_items))

    return {
        "jsonl": str(jsonl_out),
        "csv": str(csv_out),
        "review": str(review_out),
        "total": total_examples,
        "counts": label_counts
    }

def main():
    p = argparse.ArgumentParser(description="Convert training_data.jsonl -> line-level dataset")
    p.add_argument('--input', '-i', default='data/training_data.jsonl', help='Input JSONL file')
    p.add_argument('--outdir', '-o', default='data', help='Output directory')
    p.add_argument('--min-examples', type=int, default=0, help='Min examples filter (unused currently)')
    args = p.parse_args()

    res = convert(Path(args.input), Path(args.outdir), args.min_examples)
    print("Done:", res)

if __name__ == '__main__':
    main()