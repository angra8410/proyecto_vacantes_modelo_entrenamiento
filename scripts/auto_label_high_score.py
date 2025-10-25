#!/usr/bin/env python3
"""
Auto-label candidates in a CSV produced by extract_company_candidates.py

- Marca 'company' en la columna label para filas con score >= threshold y label != 'company'
- Guarda un CSV nuevo (por ejemplo data/company_candidates.autolabeled.csv) para revisión.
Uso:
  python scripts/auto_label_high_score.py data/company_candidates.csv data/company_candidates.autolabeled.csv --threshold 5
"""
import csv
import argparse
from pathlib import Path

def auto_label(inp, outp, threshold=5):
    inp = Path(inp)
    outp = Path(outp)
    if not inp.exists():
        print("Input CSV not found:", inp); return 2
    rows = []
    with inp.open('r', encoding='utf-8', newline='') as fin:
        r = csv.DictReader(fin)
        fieldnames = r.fieldnames
        for row in r:
            try:
                score = float(row.get('score') or 0)
            except:
                score = 0
            if score >= threshold:
                # auto-mark as company, but preserve original label in a new column for audit
                row.setdefault('orig_label', row.get('label',''))
                row['label'] = 'company'
                row.setdefault('auto_labeled', 'yes')
            else:
                row.setdefault('auto_labeled', 'no')
            rows.append(row)
    with outp.open('w', encoding='utf-8', newline='') as fout:
        w = csv.DictWriter(fout, fieldnames=fieldnames + ['orig_label','auto_labeled'] if 'orig_label' not in fieldnames else fieldnames + ['auto_labeled'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("Wrote auto-labeled CSV:", outp, "rows:", len(rows))
    return 0

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input_csv")
    p.add_argument("output_csv")
    p.add_argument("--threshold", type=float, default=5.0)
    args = p.parse_args()
    auto_label(args.input_csv, args.output_csv, args.threshold)