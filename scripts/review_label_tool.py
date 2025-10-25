#!/usr/bin/env python3
"""
Herramienta interactiva para revisar y etiquetar líneas en data/line_dataset_review.jsonl

Uso:
  python scripts/review_label_tool.py --input data/line_dataset_review.jsonl --out data/line_dataset_review_labeled.jsonl

Teclea:
  r  -> role
  c  -> company
  o  -> other
  s  -> skip (deja para después)
  q  -> salir (guarda lo etiquetado hasta ahora)
"""
import json, argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', default='data/line_dataset_review.jsonl')
    p.add_argument('--out', '-o', default='data/line_dataset_review_labeled.jsonl')
    args = p.parse_args()

    try:
        fin = open(args.input, 'r', encoding='utf-8')
    except FileNotFoundError:
        print("No encontrado:", args.input); return

    out_lines = []
    count = 0
    for line in fin:
        obj = json.loads(line)
        line_text = obj.get('line','')
        orig_label = obj.get('label','other')
        print("\n---")
        print(f"Source idx: {obj.get('source_index')}  line_idx: {obj.get('line_index')}")
        print("Line:", line_text)
        print("Current auto-label:", orig_label)
        ans = input("Label [r=role, c=company, o=other, s=skip, q=quit] > ").strip().lower()
        if ans == 'q':
            break
        if ans == 's':
            continue
        if ans in ('r','role'):
            obj['label'] = 'role'
        elif ans in ('c','company'):
            obj['label'] = 'company'
        elif ans in ('o','other'):
            obj['label'] = 'other'
        else:
            print("Opción no reconocida, se ignora y se sigue.")
            continue
        out_lines.append(obj)
        count += 1

    if out_lines:
        with open(args.out, 'a', encoding='utf-8') as fout:
            for o in out_lines:
                fout.write(json.dumps(o, ensure_ascii=False) + '\n')
    print(f"Guardadas {count} etiquetas en {args.out}")

if __name__ == '__main__':
    main()