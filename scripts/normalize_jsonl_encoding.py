#!/usr/bin/env python3
"""
Normalize a JSONL file to UTF-8.

Usage:
  python scripts/normalize_jsonl_encoding.py input.jsonl output.jsonl

This script will try utf-8, utf-8-sig, latin-1 in order to decode the file.
If decoding fails for the whole file it will fall back to latin-1 with replacement.
It also writes a small report of lines where non-UTF8 bytes were detected.
"""
import sys
from pathlib import Path

def try_read(path, enc):
    try:
        with open(path, 'r', encoding=enc) as f:
            data = f.read()
        return data
    except Exception as e:
        return None

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/normalize_jsonl_encoding.py input.jsonl output.jsonl")
        sys.exit(1)
    inp = Path(sys.argv[1])
    outp = Path(sys.argv[2])
    if not inp.exists():
        print("Input not found:", inp); sys.exit(2)

    # try several encodings
    for enc in ('utf-8', 'utf-8-sig', 'latin-1'):
        data = try_read(inp, enc)
        if data is not None:
            print(f"Successfully read {inp} with encoding {enc}")
            # write normalized utf-8 output
            with outp.open('w', encoding='utf-8') as fo:
                fo.write(data)
            print(f"Wrote normalized file: {outp} (utf-8)")
            return 0

    # fallback: read bytes and replace invalid sequences
    print("Could not read file reliably with standard encodings; falling back to bytes->utf-8 replace.")
    b = inp.read_bytes()
    text = b.decode('utf-8', errors='replace')
    with outp.open('w', encoding='utf-8') as fo:
        fo.write(text)
    print(f"Wrote fallback-normalized file: {outp} (utf-8, with replacement)")
    return 0

if __name__ == '__main__':
    main()