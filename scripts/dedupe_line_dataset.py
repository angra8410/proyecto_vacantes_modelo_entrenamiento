#!/usr/bin/env python3
"""
scripts/dedupe_line_dataset.py
Deduplica data/line_dataset.jsonl por key (source_hash + line_index) y exporta data/line_dataset.dedup.jsonl
Uso:
  python scripts/dedupe_line_dataset.py data/line_dataset.jsonl data/line_dataset.dedup.jsonl
"""
import sys, json
from pathlib import Path

def dedupe(infile: str, outfile: str):
    seen = set()
    out_lines = []
    with open(infile, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                continue
            key = (obj.get('source_hash',''), str(obj.get('line_index','')), obj.get('line','').strip())
            if key in seen:
                continue
            seen.add(key)
            out_lines.append(obj)
    with open(outfile, 'w', encoding='utf-8') as fout:
        for o in out_lines:
            fout.write(json.dumps(o, ensure_ascii=False) + '\n')
    print("Wrote deduped:", outfile, "total:", len(out_lines))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts/dedupe_line_dataset.py in.jsonl out.jsonl")
        sys.exit(1)
    dedupe(sys.argv[1], sys.argv[2])