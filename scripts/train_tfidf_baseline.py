#!/usr/bin/env python3
"""
Entrena un clasificador TF-IDF + LogisticRegression rápido como baseline.
Salida: model.pkl (joblib) y imprime métricas.
Uso:
  python scripts/train_tfidf_baseline.py data/line_dataset.jsonl
"""
import sys, json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

def load(path):
    X=[]; y=[]
    with open(path,encoding='utf-8') as f:
        for l in f:
            obj=json.loads(l)
            X.append(obj.get('line',''))
            y.append(obj.get('label','other'))
    return X,y

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv)>1 else 'data/line_dataset.jsonl'
    X,y = load(path)
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1, random_state=42, stratify=y)
    v = TfidfVectorizer(ngram_range=(1,2), max_features=20000)
    Xt = v.fit_transform(X_train)
    clf = LogisticRegression(max_iter=200, class_weight='balanced')
    clf.fit(Xt, y_train)
    Xtst = v.transform(X_test)
    preds = clf.predict(Xtst)
    print(classification_report(y_test, preds))
    joblib.dump({'vect':v, 'clf':clf}, 'models/tfidf_baseline.joblib')
    print("Saved models/tfidf_baseline.joblib")