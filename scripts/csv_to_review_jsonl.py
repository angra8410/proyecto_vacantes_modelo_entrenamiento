#!/usr/bin/env python3
"""
scripts/csv_to_review_jsonl.py

Convierte un CSV (line,label,source_hash) -> JSONL (misma estructura) para poder mezclarlo.
Uso:
  python scripts/csv_to_review_jsonl.py data/review_sample_200.csv data/review_sample_200_labeled.jsonl
"""
import csv
import json
import sys
from pathlib import Path
import unicodedata
import re

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def convert(csv_path: Path, out_jsonl: Path):
    if not csv_path.exists():
        print("Input CSV not found:", csv_path)
        return 2
    count = 0
    with csv_path.open(encoding='utf-8', newline='') as fin, out_jsonl.open('w', encoding='utf-8') as fout:
        reader = csv.DictReader(fin)
        expected = set(['line','label','source_hash'])
        if not expected.issubset(set(reader.fieldnames)):
            print("CSV debe contener columnas: line,label,source_hash")
            print("Found:", reader.fieldnames)
            return 3
        for row in reader:
            item = {
                "line": row.get("line","").strip(),
                "label": row.get("label","").strip() or "other",
                "source_hash": row.get("source_hash","").strip(),
                "line_norm": normalize_text(row.get("line","")),
            }
            fout.write(json.dumps(item, ensure_ascii=False) + '\n')
            count += 1
    print(f"Wrote {count} items to {out_jsonl}")
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/csv_to_review_jsonl.py input.csv output.jsonl")
        sys.exit(1)
    in_csv = Path(sys.argv[1])
    out_j = Path(sys.argv[2])
    sys.exit(convert(in_csv, out_j))