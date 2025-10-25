#!/usr/bin/env python3
"""
scripts/review_sample_to_csv.py
Convierte un JSONL (cada línea JSON) en un CSV con columnas: line,label,source_hash
Uso:
  python scripts/review_sample_to_csv.py data/review_sample_200.jsonl data/review_sample_200.csv
"""
import sys, json, csv
from pathlib import Path

def convert(in_path: str, out_path: str):
    p_in = Path(in_path)
    p_out = Path(out_path)
    if not p_in.exists():
        print("Input not found:", p_in); return 1
    with p_in.open(encoding='utf-8') as fin, p_out.open('w', encoding='utf-8', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(['line','label','source_hash'])
        for ln in fin:
            ln = ln.strip()
            if not ln:
                continue
            try:
                obj = json.loads(ln)
            except Exception as e:
                print("Skipping invalid json line:", e)
                continue
            writer.writerow([obj.get('line',''), obj.get('label','other'), obj.get('source_hash','')])
    print("Wrote CSV:", p_out)
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/review_sample_to_csv.py input.jsonl output.csv")
        sys.exit(1)
    sys.exit(convert(sys.argv[1], sys.argv[2]))