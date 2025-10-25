```text
# proyecto_vacantes

Repositorio con scripts para procesar vacantes, generar dataset por línea y entrenar clasificadores (role/company/other).

Estructura:
- scripts/        # scripts Python para conversión, etiquetado, entrenamiento y utilidades
- data/           # datasets (no versionar datos sensibles)
- models/         # modelos guardados (no versionar)
- output/         # archivos generados (no versionar)
- venv/           # entorno virtual (no versionar)

Instrucciones rápidas:
1. Crear y activar venv:
   python -m venv venv
   .\venv\Scripts\Activate.ps1

2. Instalar dependencias:
   pip install -r requirements.txt

3. Procesar vacantes desde YAML:
   python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes
   python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl

4. Generar dataset de líneas:
   python .\scripts\convert_to_line_dataset.py --input .\data\training_data.jsonl --outdir .\data

5. Revisar/etiquetar:
   python .\scripts\review_label_tool.py --input .\data\line_dataset_review.jsonl --out .\data\line_dataset_review_labeled.jsonl

6. Entrenar (baseline TF-IDF):
   python .\scripts\train_tfidf_baseline.py data/line_dataset.jsonl

## Procesador de Vacantes (process_vacantes.py)

Módulo para procesar y validar archivos con múltiples vacantes en formato YAML separadas por `---`.

### Características:
- Lee archivos con múltiples vacantes en formato YAML
- Valida campos requeridos: cargo, empresa, fecha, descripcion, requerimientos
- Genera archivos .yaml individuales por cada vacante válida
- Reporta inconsistencias y campos faltantes de manera detallada
- Convierte vacantes válidas a formato .jsonl para pipelines de ML

### Uso:
```bash
# Procesar vacantes y generar archivos YAML individuales
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes

# Procesar y convertir a JSONL
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl

# Especificar archivo JSONL personalizado
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl --jsonl-file mis_vacantes.jsonl

# Modo silencioso
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --quiet
```

### Formato del archivo de entrada:
El archivo debe contener vacantes en formato YAML separadas por `---`:
```yaml
cargo: Senior Developer
empresa: Tech Corp
fecha: 2025-01-15
descripcion: |
  Descripción detallada del puesto...
requerimientos: |
  - Requisito 1
  - Requisito 2
---
cargo: Business Analyst
empresa: Consulting Inc
...
```

### Validaciones:
- Campos requeridos: cargo, empresa, fecha, descripcion, requerimientos
- Formato de fecha: YYYY-MM-DD (o objeto date de Python)
- Los campos no pueden estar vacíos

### Salida:
- Archivos YAML individuales: `{fecha}_{cargo}_{empresa}.yaml`
- Archivo JSONL opcional con todas las vacantes válidas
- Reporte detallado de errores y estadísticas
```
