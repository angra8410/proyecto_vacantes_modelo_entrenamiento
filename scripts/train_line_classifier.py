#!/usr/bin/env python3
"""
scripts/train_line_classifier.py

Entrena un clasificador de líneas (labels: role, company, other) usando HuggingFace
Transformers + Datasets (ej. DistilBERT). El script asume que ya generaste
data/line_dataset.jsonl con scripts/convert_to_line_dataset.py.

Uso (ejemplo):
  python scripts/train_line_classifier.py \
    --data-file data/line_dataset.jsonl \
    --model distilbert-base-uncased \
    --output-dir models/line-classifier \
    --epochs 3 \
    --per-device-batch-size 16 \
    --max-length 128

Requisitos:
  dentro del venv:
    python -m pip install --upgrade pip
    python -m pip install transformers datasets accelerate scikit-learn evaluate

El script:
 - carga el JSONL en datasets
 - mapea labels a integers
 - tokeniza con el tokenizer del modelo base
 - entrena con Trainer y guarda el modelo/tokenizer al final
 - imprime métricas (accuracy, precision, recall, f1)
"""
import argparse
import os
from pathlib import Path
import numpy as np
from datasets import load_dataset, ClassLabel
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    DataCollatorWithPadding,
    TrainingArguments,
    Trainer,
)
import evaluate

LABELS = ["role", "company", "other"]

def parse_args():
    p = argparse.ArgumentParser(description="Train line-level classifier")
    p.add_argument("--data-file", type=str, default="data/line_dataset.jsonl",
                   help="Path to line-level JSONL produced by convert_to_line_dataset.py")
    p.add_argument("--model", type=str, default="distilbert-base-uncased",
                   help="Pretrained model to fine-tune")
    p.add_argument("--output-dir", type=str, default="models/line-classifier",
                   help="Where to save model and tokenizer")
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--per-device-batch-size", type=int, default=16)
    p.add_argument("--learning-rate", type=float, default=5e-5)
    p.add_argument("--weight-decay", type=float, default=0.01)
    p.add_argument("--max-length", type=int, default=128)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--push-to-hub", action="store_true", help="(optional) push model to HF Hub")
    return p.parse_args()

def map_labels(example):
    # convert string label to integer id
    label2id = {l: i for i, l in enumerate(LABELS)}
    lab = example.get("label")
    # fallback: if label already numeric, keep it
    if isinstance(lab, int):
        example["labels"] = lab
    else:
        example["labels"] = label2id.get(lab, label2id["other"])
    return example

def tokenize_batch(examples, tokenizer, max_length):
    # tokenize 'line' field
    return tokenizer(examples["line"], truncation=True, padding="max_length", max_length=max_length)

def compute_metrics_fn(pred):
    accuracy = evaluate.load("accuracy")
    precision = evaluate.load("precision")
    recall = evaluate.load("recall")
    f1 = evaluate.load("f1")
    preds = np.argmax(pred.predictions, axis=1)
    labels = pred.label_ids
    return {
        "accuracy": accuracy.compute(predictions=preds, references=labels)["accuracy"],
        "precision": precision.compute(predictions=preds, references=labels, average="weighted")["precision"],
        "recall": recall.compute(predictions=preds, references=labels, average="weighted")["recall"],
        "f1": f1.compute(predictions=preds, references=labels, average="weighted")["f1"],
    }

def main():
    args = parse_args()

    # verify files
    data_path = Path(args.data_file)
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # load dataset (JSON lines)
    ds = load_dataset("json", data_files=str(data_path), field=None)
    # dataset comes as ds['train']
    ds = ds["train"]
    # quick info
    print("Loaded dataset examples:", len(ds))

    # Map labels (string -> int) to a consistent column 'labels'
    ds = ds.map(map_labels)

    # remove examples with missing 'line' or labels if any
    ds = ds.filter(lambda x: bool(x.get("line")))

    # train/test split
    if "test" not in ds:
        ds = ds.train_test_split(test_size=0.10, seed=args.seed)
    train_ds = ds["train"]
    test_ds = ds["test"]
    print("Train size:", len(train_ds), "Test size:", len(test_ds))

    # tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=len(LABELS))

    # tokenize datasets
    tokenized_train = train_ds.map(lambda x: tokenize_batch(x, tokenizer, args.max_length), batched=True)
    tokenized_test = test_ds.map(lambda x: tokenize_batch(x, tokenizer, args.max_length), batched=True)

    # set format for PyTorch
    tokenized_train = tokenized_train.remove_columns([c for c in tokenized_train.column_names if c not in ("input_ids","attention_mask","labels")])
    tokenized_test = tokenized_test.remove_columns([c for c in tokenized_test.column_names if c not in ("input_ids","attention_mask","labels")])

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        evaluation_strategy="epoch",
        per_device_train_batch_size=args.per_device_batch_size,
        per_device_eval_batch_size=args.per_device_batch_size,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        num_train_epochs=args.epochs,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        seed=args.seed,
        fp16=(os.environ.get("USE_FP16","0") == "1"),
        logging_steps=50,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics_fn,
    )

    # train
    trainer.train()

    # final evaluation
    eval_res = trainer.evaluate(tokenized_test)
    print("Final evaluation:", eval_res)

    # save model + tokenizer
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)
    print("Saved model and tokenizer to", args.output_dir)

    if args.push_to_hub:
        try:
            trainer.push_to_hub()
            print("Pushed to the Hub.")
        except Exception as e:
            print("Push to Hub failed:", e)

if __name__ == "__main__":
    main()