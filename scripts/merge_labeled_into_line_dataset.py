#!/usr/bin/env python3
"""
scripts/merge_labeled_into_line_dataset.py

Toma:
 - data/line_dataset.jsonl (original generado)
 - un JSONL con labels manuales (por ejemplo resultante de csv_to_review_jsonl.py)

Actualiza las entradas de line_dataset.jsonl reemplazando label cuando coincida (por source_hash + line_norm),
añade nuevas si no existían y escribe data/line_dataset.merged.jsonl y data/line_dataset.merged.dedup.jsonl

Uso:
  python scripts/merge_labeled_into_line_dataset.py data/line_dataset.jsonl data/review_sample_200_labeled.jsonl
"""
import json
import sys
from pathlib import Path
import unicodedata
import re
from collections import OrderedDict

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def load_jsonl(path: Path):
    items = []
    if not path.exists():
        return items
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                items.append(obj)
            except Exception:
                # ignore malformed
                continue
    return items

def merge(main_path: Path, labeled_path: Path, out_path: Path):
    main = load_jsonl(main_path)
    labeled = load_jsonl(labeled_path)

    # index main by (source_hash, line_norm) -> object (keep first occurrence)
    index = OrderedDict()
    for obj in main:
        key = (obj.get('source_hash',''), normalize_text(obj.get('line','')))
        if key not in index:
            index[key] = obj

    # apply labeled updates: replace label when matching key, else add new
    added = 0
    updated = 0
    for lab in labeled:
        key = (lab.get('source_hash',''), normalize_text(lab.get('line','')))
        if key in index:
            if index[key].get('label') != lab.get('label'):
                index[key]['label'] = lab.get('label')
                updated += 1
        else:
            # create a full item (keep minimal required fields)
            new_item = {
                "line": lab.get('line',''),
                "line_norm": normalize_text(lab.get('line','')),
                "label": lab.get('label','other'),
                "source_hash": lab.get('source_hash',''),
                "source_yaml": lab.get('source_yaml',''),
                "source_index": lab.get('source_index', None),
                "line_index": lab.get('line_index', None)
            }
            index[key] = new_item
            added += 1

    # write merged file
    with out_path.open('w', encoding='utf-8') as fout:
        for obj in index.values():
            fout.write(json.dumps(obj, ensure_ascii=False) + '\n')

    print(f"Merged. updated={updated} added={added} total_after={len(index)} wrote={out_path}")
    return updated, added, len(index)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/merge_labeled_into_line_dataset.py line_dataset.jsonl labeled_review.jsonl")
        sys.exit(1)
    main_p = Path(sys.argv[1])
    lab_p = Path(sys.argv[2])
    out_p = Path('data') / 'line_dataset.merged.jsonl'
    merge(main_p, lab_p, out_p)