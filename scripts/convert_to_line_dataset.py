#!/usr/bin/env python3
"""
convert_to_line_dataset.py

Script to convert training data from JSONL format to line-by-line dataset format.
Each line from the input data is processed and normalized for classification tasks.
"""

import argparse
import json
import os
from pathlib import Path


def convert_to_line_dataset(input_file, output_dir):
    """
    Convert JSONL training data to line dataset format.
    
    Args:
        input_file: Path to input JSONL file
        output_dir: Directory to save output files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "line_dataset.jsonl"
    review_file = output_dir / "line_dataset_review.jsonl"
    
    print(f"Reading from: {input_file}")
    print(f"Writing to: {output_file}")
    
    line_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile, \
         open(review_file, 'w', encoding='utf-8') as reviewfile:
        
        for line_num, line in enumerate(infile, 1):
            try:
                data = json.loads(line.strip())
                
                # Process each line from the vacancy data
                if 'lines' in data:
                    for line_text in data['lines']:
                        line_obj = {
                            'text': line_text,
                            'source_id': data.get('id', f'unknown_{line_num}'),
                            'label': data.get('label', 'unlabeled')
                        }
                        outfile.write(json.dumps(line_obj, ensure_ascii=False) + '\n')
                        reviewfile.write(json.dumps(line_obj, ensure_ascii=False) + '\n')
                        line_count += 1
                        
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
    
    print(f"Processed {line_count} lines")
    print(f"Review file created at: {review_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert training data to line dataset format'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input JSONL file with training data'
    )
    parser.add_argument(
        '--outdir',
        required=True,
        help='Output directory for line dataset files'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    convert_to_line_dataset(args.input, args.outdir)
    return 0


if __name__ == '__main__':
    exit(main())
