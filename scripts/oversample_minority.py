#!/usr/bin/env python3
"""
Oversample minority class in data/line_dataset.jsonl by duplicating examples.
Uso:
  python scripts/oversample_minority.py --input data/line_dataset.jsonl --output data/line_dataset.oversampled.jsonl --target-ratio 0.33
target-ratio = fraction deseada de la clase minoritaria (ej. 0.33 => queremos que 'company' sea ~33% del dataset)
"""
import argparse, json, random
from collections import defaultdict
from pathlib import Path

def load(path):
    with open(path,'r',encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]

def save(path, items):
    with open(path,'w',encoding='utf-8') as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + '\n')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input','-i', default='data/line_dataset.jsonl')
    p.add_argument('--output','-o', default='data/line_dataset.oversampled.jsonl')
    p.add_argument('--label', default='company')
    p.add_argument('--target-ratio', type=float, default=0.25)
    args = p.parse_args()

    items = load(Path(args.input))
    by_label = defaultdict(list)
    for it in items:
        by_label[it.get('label','other')].append(it)

    n_total = len(items)
    n_min = len(by_label[args.label])
    desired_min = int(args.target_ratio * n_total / (1 - args.target_ratio))
    # desired_min is how many minority examples we want in total, compute factor:
    if n_min == 0:
        print("No examples for label", args.label); return
    # needed additional examples:
    need = max(0, desired_min - n_min)
    print(f"Current total={n_total} {args.label}={n_min}. Need to add {need} duplicates to reach target ratio {args.target_ratio}.")
    new_items = list(items)
    if need>0:
        for _ in range(need):
            new_items.append(random.choice(by_label[args.label]))
    random.shuffle(new_items)
    save(Path(args.output), new_items)
    print("Wrote oversampled file:", args.output, "new_total:", len(new_items))

if __name__ == '__main__':
    main()