#!/usr/bin/env python3
"""
scripts/extract_company_candidates.py

Extrae candidatos 'company' desde data/line_dataset.jsonl y escribe un CSV con columnas:
line,label,source_hash,source_index,line_index,reason

Criterios (heurísticos) para marcar candidato company:
 - contiene sufijos/indicadores: inc, llc, ltda, ltd, corp, company, group, s.a, sa, co
 - contiene token 'logo'
 - TitleCase corto (1-6 words con mayoría TitleCase) y no parece ser 'role' por keywords
 - (opcional) proximidad a top of posting (se prioriza usando flag --priority-top)

Uso:
  python scripts/extract_company_candidates.py --input data/line_dataset.jsonl --out data/company_candidates.csv --limit 500

Salida:
  data/company_candidates.csv
"""
import re
import csv
import json
import argparse
from pathlib import Path

COMPANY_INDICATORS = re.compile(r'\b(inc|llc|ltda|ltd|corp|company|group|s\.a|sa|co)\b', re.I)
LOGO_RE = re.compile(r'\blogo\b', re.I)
ROLE_KEYWORDS = re.compile(r'\b(analyst|engineer|developer|manager|consultant|scientist|coordinator|officer|specialist|administrator|architect|operations|data|insight|insights|analyt|analytics|analisis|analítica)\b', re.I)

def is_titlecase_short(s):
    words = [w for w in s.split() if w]
    if not (1 < len(words) <= 6):
        return False
    cap = sum(1 for w in words if w and w[0].isupper())
    return cap >= max(1, len(words)//2)

def normalize_whitespace(s):
    return re.sub(r'\s+', ' ', s).strip()

def extract(input_path, out_csv, limit=None, priority_top=False):
    input_path = Path(input_path)
    out_csv = Path(out_csv)
    rows = []

    with input_path.open('r', encoding='utf-8') as fin:
        for i, line in enumerate(fin):
            if limit and len(rows) >= limit:
                break
            try:
                obj = json.loads(line)
            except Exception:
                continue
            text = obj.get('line','').strip()
            if not text:
                continue
            text_norm = normalize_whitespace(text)
            reason = []
            score = 0

            if COMPANY_INDICATORS.search(text_norm):
                reason.append("indicator")
                score += 5
            if LOGO_RE.search(text_norm):
                reason.append("logo")
                score += 3
            # TitleCase heuristic but avoid typical role keywords
            if is_titlecase_short(text_norm) and not ROLE_KEYWORDS.search(text_norm):
                reason.append("titlecase")
                score += 2

            # deprioritize obvious noise
            if re.search(r'\b(days?\s+ago|applicants?|applicant|remote|full-?time|part-?time|contract|easy apply|promoted|save|share)\b', text_norm, re.I):
                reason.append("metadata")
                score -= 5

            if score > 0:
                rows.append({
                    "line": text,
                    "label": obj.get("label","other"),
                    "source_hash": obj.get("source_hash",""),
                    "source_index": obj.get("source_index",""),
                    "line_index": obj.get("line_index",""),
                    "reason": "|".join(reason),
                    "score": score
                })

    # sort by score desc, optionally prioritize smaller source_index (top-of-postings)
    rows.sort(key=lambda r: (-r['score'], int(r['source_index'] or 0) if r['source_index'] not in (None,"") else 999999))
    # write CSV
    with out_csv.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['line','label','source_hash','source_index','line_index','reason','score'])
        for r in rows:
            writer.writerow([r['line'], r['label'], r['source_hash'], r['source_index'], r['line_index'], r['reason'], r['score']])

    print(f"Wrote {len(rows)} candidates to {out_csv}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input','-i', default='data/line_dataset.jsonl')
    p.add_argument('--out','-o', default='data/company_candidates.csv')
    p.add_argument('--limit','-n', type=int, default=None, help='Máximo candidatos a extraer')
    args = p.parse_args()
    extract(args.input, args.out, limit=args.limit)

if __name__ == "__main__":
    main()