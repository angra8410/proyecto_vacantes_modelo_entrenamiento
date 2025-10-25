#!/usr/bin/env python3
"""
Normalize company names in a CSV (data/company_candidates*.csv) or JSONL.
- Remove '(logo)', 'logo', location parts after '·' or ' - ', '(Hybrid)', '(Remote)', trailing punctuation
- Collapse whitespace and strip
Usage (CSV):
  python scripts/normalize_company_names.py --csv data/company_candidates.autolabeled.csv --out data/company_candidates.normalized.csv
"""
import re, csv, argparse
from pathlib import Path

def normalize_name(s: str) -> str:
    if s is None:
        return ""
    t = s.strip()
    # Remove '(logo)' and trailing 'logo'
    t = re.sub(r'\s*\(logo\)\s*$', '', t, flags=re.I)
    t = re.sub(r'\s*logo\s*$', '', t, flags=re.I)
    # Remove location and metadata after '·' or ' - ' or ' — '
    t = re.split(r'\s*[·\-–—]\s*', t)[0]
    # Remove parenthetical tags like (Hybrid), (Remote)
    t = re.sub(r'\((hybrid|remote|on-site|on site|work from home)\)', '', t, flags=re.I)
    # Remove commas followed by location e.g., ", Medellín, Antioquia, Colombia"
    t = re.sub(r',\s*[A-Za-zÁÉÍÓÚÑáéíóúñ0-9\.\s\-]+$', '', t)
    # Collapse whitespace and punctuation cleanup
    t = re.sub(r'[·•\u2022]+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = t.rstrip('.,;:')
    return t

def normalize_csv(inp, out):
    inp = Path(inp); out = Path(out)
    with inp.open('r', encoding='utf-8', newline='') as fin, out.open('w', encoding='utf-8', newline='') as fout:
        r = csv.DictReader(fin)
        fieldnames = r.fieldnames
        w = csv.DictWriter(fout, fieldnames=fieldnames)
        w.writeheader()
        for row in r:
            row['line'] = normalize_name(row.get('line',''))
            w.writerow(row)
    print("Wrote normalized CSV:", out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', help='input csv to normalize')
    p.add_argument('--out', help='output csv', default='data/company_candidates.normalized.csv')
    args = p.parse_args()
    if args.csv:
        normalize_csv(args.csv, args.out)
    else:
        print("No --csv provided.")

if __name__ == '__main__':
    main()