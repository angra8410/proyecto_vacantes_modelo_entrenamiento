#!/usr/bin/env python3
"""
scripts/check_counts.py

Cuenta cuántos ejemplos hay por etiqueta en data/line_dataset.jsonl
Imprime el conteo y muestra unas muestras por etiqueta.

Uso:
  python scripts/check_counts.py --input data/line_dataset.jsonl --show-samples 5
"""
import json
import argparse
import collections
from pathlib import Path
import random

def load_items(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    return items

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default="data/line_dataset.jsonl")
    p.add_argument("--show-samples", "-s", type=int, default=5)
    args = p.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print("Input not found:", in_path)
        return

    items = load_items(in_path)
    counts = collections.Counter()
    by_label = {}
    for it in items:
        lab = it.get("label", "other")
        counts[lab] += 1
        by_label.setdefault(lab, []).append(it)

    print("Total lines:", len(items))
    print("Counts per label:")
    for k,v in counts.items():
        print(f"  {k}: {v}")

    n = args.show_samples
    print("\nSample lines per label (up to {} each):".format(n))
    for lab, lst in by_label.items():
        print(f"\n== {lab} (showing up to {n}) ==")
        samples = random.sample(lst, min(n, len(lst)))
        for s in samples:
            line = s.get("line","")[:200].replace("\n"," ")
            print(" -", repr(line))

if __name__ == "__main__":
    main()