#!/usr/bin/env python3
"""
train_tfidf_baseline.py

Baseline classifier using TF-IDF features for line classification.
Trains a model to classify lines into role/company/other categories.
"""

import argparse
import json
import os
import pickle
from pathlib import Path
from collections import Counter

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
except ImportError:
    print("Error: scikit-learn is required. Install with: pip install scikit-learn")
    exit(1)


def load_dataset(file_path):
    """
    Load line dataset from JSONL file.
    
    Args:
        file_path: Path to JSONL file
        
    Returns:
        Tuple of (texts, labels)
    """
    texts = []
    labels = []
    
    print(f"Loading dataset from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                # Skip unlabeled or skipped entries
                label = data.get('label', 'unlabeled')
                if label in ['unlabeled', 'skip']:
                    continue
                
                text = data.get('text', '').strip()
                if text:
                    texts.append(text)
                    labels.append(label)
                    
            except json.JSONDecodeError as e:
                print(f"Warning: Error parsing line {line_num}: {e}")
                continue
    
    print(f"Loaded {len(texts)} labeled examples")
    print(f"Label distribution: {dict(Counter(labels))}")
    
    return texts, labels


def train_tfidf_baseline(dataset_file, output_dir='models'):
    """
    Train a TF-IDF + Logistic Regression baseline classifier.
    
    Args:
        dataset_file: Path to labeled line dataset
        output_dir: Directory to save trained model
    """
    # Load data
    texts, labels = load_dataset(dataset_file)
    
    if len(texts) < 10:
        print("Error: Not enough labeled data to train. Need at least 10 examples.")
        return 1
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    print(f"\nTraining set: {len(X_train)} examples")
    print(f"Test set: {len(X_test)} examples")
    
    # Train TF-IDF vectorizer
    print("\nTraining TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)
    
    # Train classifier
    print("Training Logistic Regression classifier...")
    classifier = LogisticRegression(
        max_iter=1000,
        random_state=42,
        C=1.0
    )
    classifier.fit(X_train_tfidf, y_train)
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Evaluation Results")
    print("=" * 60)
    
    y_pred = classifier.predict(X_test_tfidf)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nAccuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = output_dir / 'tfidf_baseline_model.pkl'
    vectorizer_path = output_dir / 'tfidf_vectorizer.pkl'
    
    with open(model_path, 'wb') as f:
        pickle.dump(classifier, f)
    
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    
    print(f"\nModel saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Train TF-IDF baseline classifier for line classification'
    )
    parser.add_argument(
        'dataset',
        help='Path to labeled line dataset JSONL file'
    )
    parser.add_argument(
        '--output-dir',
        default='models',
        help='Directory to save trained model (default: models)'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.dataset):
        print(f"Error: Dataset file not found: {args.dataset}")
        return 1
    
    return train_tfidf_baseline(args.dataset, args.output_dir)


if __name__ == '__main__':
    exit(main())
