#!/usr/bin/env python3
# scripts/find_bad_extractions.py
import json, re, sys

infile = 'data/training_data.jsonl'
bad = []

with open(infile, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception as e:
            print("Skipping invalid json line at", i, e)
            continue
        yaml_text = obj.get('yaml','')
        # empty company
        if re.search(r'empresa:\s*""|empresa:\s*"\s*"', yaml_text):
            bad.append((i,'empty_company', obj))
            continue
        # metadata used as company
        if re.search(r'(days ago|applicants|applicant)', yaml_text, re.I):
            bad.append((i,'metadata_as_company', obj))
            continue
        # cargo == empresa
        m = re.search(r'cargo:\s*"(?P<c>[^"]+)"\s*[\r\n]+empresa:\s*"(?P<e>[^"]+)"', yaml_text)
        if m and m.group('c').strip() == m.group('e').strip():
            bad.append((i,'cargo_equals_empresa', obj))

print("Bad extractions found:", len(bad))
for i, kind, obj in bad[:200]:
    print(f"{i:6d} {kind} -> text (truncated): {obj.get('text','')[:120]!r}")