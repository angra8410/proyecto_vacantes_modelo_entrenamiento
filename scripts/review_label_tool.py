#!/usr/bin/env python3
"""
review_label_tool.py

Interactive tool for reviewing and labeling line dataset entries.
Allows manual classification of lines into categories like role/company/other.
"""

import argparse
import json
import os
import sys


class ReviewLabelTool:
    """Interactive tool for reviewing and labeling dataset lines."""
    
    LABELS = ['role', 'company', 'other', 'skip']
    
    def __init__(self, input_file, output_file, text_preview_length=100):
        self.input_file = input_file
        self.output_file = output_file
        self.reviewed_count = 0
        self.skipped_count = 0
        self.text_preview_length = text_preview_length
    
    def review(self):
        """Start the interactive review process."""
        print("=" * 60)
        print("Line Dataset Review and Labeling Tool")
        print("=" * 60)
        print(f"Input: {self.input_file}")
        print(f"Output: {self.output_file}")
        print("\nAvailable labels:")
        for i, label in enumerate(self.LABELS, 1):
            print(f"  {i}. {label}")
        print("\nPress Ctrl+C to quit and save progress\n")
        print("=" * 60)
        
        output_lines = []
        
        # Load existing output if resuming
        if os.path.exists(self.output_file):
            print(f"Loading existing output file...")
            with open(self.output_file, 'r', encoding='utf-8') as f:
                output_lines = [json.loads(line) for line in f]
            print(f"Loaded {len(output_lines)} previously labeled entries\n")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as infile:
                for line_num, line in enumerate(infile, 1):
                    # Skip already processed lines
                    if line_num <= len(output_lines):
                        continue
                    
                    try:
                        data = json.loads(line.strip())
                        
                        text = data.get('text', '')
                        preview = text[:self.text_preview_length] + ('...' if len(text) > self.text_preview_length else '')
                        print(f"\n[{line_num}] Text: {preview}")
                        print(f"Current label: {data.get('label', 'unlabeled')}")
                        
                        choice = input("Select label (1-4): ").strip()
                        
                        if choice.isdigit() and 1 <= int(choice) <= len(self.LABELS):
                            new_label = self.LABELS[int(choice) - 1]
                            
                            if new_label == 'skip':
                                self.skipped_count += 1
                                continue
                            
                            data['label'] = new_label
                            data['reviewed'] = True
                            output_lines.append(data)
                            self.reviewed_count += 1
                            
                            # Save progress periodically
                            if self.reviewed_count % 10 == 0:
                                self._save_progress(output_lines)
                        else:
                            print("Invalid choice. Skipping...")
                            self.skipped_count += 1
                            
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
                        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Saving progress...")
        
        self._save_progress(output_lines)
        self._print_summary()
    
    def _save_progress(self, output_lines):
        """Save progress to output file."""
        with open(self.output_file, 'w', encoding='utf-8') as outfile:
            for entry in output_lines:
                outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"Progress saved to {self.output_file}")
    
    def _print_summary(self):
        """Print summary of review session."""
        print("\n" + "=" * 60)
        print("Review Summary")
        print("=" * 60)
        print(f"Reviewed: {self.reviewed_count}")
        print(f"Skipped: {self.skipped_count}")
        print(f"Total: {self.reviewed_count + self.skipped_count}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Interactive tool for reviewing and labeling line dataset'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input JSONL file with lines to review'
    )
    parser.add_argument(
        '--out',
        required=True,
        help='Output JSONL file for labeled data'
    )
    parser.add_argument(
        '--preview-length',
        type=int,
        default=100,
        help='Number of characters to show in text preview (default: 100)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    tool = ReviewLabelTool(args.input, args.out, args.preview_length)
    tool.review()
    
    return 0


if __name__ == '__main__':
    exit(main())
