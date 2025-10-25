#!/usr/bin/env python3
# scripts/dedupe_training.py
import json, hashlib, sys
from collections import defaultdict

infile = 'data/training_data.jsonl'
outfile = 'data/training_data.dedup.jsonl'
out = {}
conflicts = defaultdict(list)

with open(infile,'r',encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as e:
            print("Skipping invalid json line:", e)
            continue
        txt = obj.get('text','').strip()
        key = hashlib.sha1(txt.encode('utf-8')).hexdigest()
        if key not in out:
            out[key] = obj
        else:
            if out[key].get('yaml') != obj.get('yaml'):
                conflicts[key].append(obj)

# Write merged file and print conflicts for manual review
with open(outfile,'w',encoding='utf-8') as f:
    for k,obj in out.items():
        f.write(json.dumps(obj,ensure_ascii=False) + '\n')

print("Wrote deduped file:", outfile)
print("Conflicts:", len(conflicts))
for k,items in conflicts.items():
    print("Conflict for key",k)
    print("Existing:", out[k])
    print("Others sample:", items[:3])