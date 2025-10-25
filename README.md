```text
# proyecto_vacantes

Repositorio con scripts para procesar vacantes, generar dataset por línea y entrenar clasificadores (role/company/other).

Estructura:
- scripts/        # scripts Python para conversión, etiquetado, entrenamiento y utilidades
- data/           # datasets (no versionar datos sensibles)
- models/         # modelos guardados (no versionar)
- venv/           # entorno virtual (no versionar)

Instrucciones rápidas:
1. Crear y activar venv:
   python -m venv venv
   .\venv\Scripts\Activate.ps1

2. Instalar dependencias:
   pip install -r requirements.txt

3. Generar dataset de líneas:
   python .\scripts\convert_to_line_dataset.py --input .\data\training_data.jsonl --outdir .\data

4. Revisar/etiquetar:
   python .\scripts\review_label_tool.py --input .\data\line_dataset_review.jsonl --out .\data\line_dataset_review_labeled.jsonl

5. Entrenar (baseline TF-IDF):
   python .\scripts\train_tfidf_baseline.py data/line_dataset.jsonl
```
