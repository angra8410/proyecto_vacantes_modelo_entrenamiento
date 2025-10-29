```text
# proyecto_vacantes

Repositorio con scripts para procesar vacantes, generar dataset por línea y entrenar clasificadores (role/company/other).

## ⚡ Flujo Automático de Vacantes (NUEVO)

**Ahora el procesamiento de vacantes es completamente automático:**

1. **Sube tu archivo de vacantes** (`vacantes.txt` o `vacantes_sample.txt`) al repositorio
2. **GitHub Actions detecta el cambio** automáticamente
3. **Se generan archivos YAML** individuales en **DOS carpetas**:
   - `vacantes_yaml/` - Copia original (respaldo, no tocar)
   - `vacantes_yaml_manual/` - Copia editable (puedes ajustar manualmente)
4. **Los archivos se copian** automáticamente a `aplicaciones_laborales` desde `vacantes_yaml_manual/`

### 📁 Diferencia entre carpetas

- **`vacantes_yaml/`**: Respaldo automático, NO editar (se sobrescribe al regenerar)
- **`vacantes_yaml_manual/`**: Copia para ajustes manuales, esta se envía a `aplicaciones_laborales`

**Formato esperado del archivo de entrada:**
```yaml
cargo: Senior Developer
empresa: Tech Corp
fecha: 2025-01-15
descripcion: |
  Descripción del puesto...
requerimientos: |
  - Requisito 1
  - Requisito 2
---
cargo: Data Analyst
empresa: Analytics Inc
fecha: 2025-01-20
descripcion: |
  Otra descripción...
requerimientos: |
  - SQL avanzado
  - Python
```

**¡Eso es todo!** No necesitas ejecutar scripts manualmente. El sistema procesa y distribuye las vacantes automáticamente.

📖 **Ver guía completa:** [GUIA_WORKFLOW_AUTOMATICO.md](GUIA_WORKFLOW_AUTOMATICO.md)

Estructura:
- scripts/        # scripts Python para conversión, etiquetado, entrenamiento y utilidades
- data/           # datasets (no versionar datos sensibles)
- models/         # modelos guardados (no versionar)
- output/         # archivos generados (no versionar)
- venv/           # entorno virtual (no versionar)
- vacantes_yaml/  # YAMLs generados automáticamente (copia original, respaldo)
- vacantes_yaml_manual/  # YAMLs generados automáticamente (copia editable)

Instrucciones rápidas:
1. Crear y activar venv:
   python -m venv venv
   .\venv\Scripts\Activate.ps1

2. Instalar dependencias:
   pip install -r requirements.txt

3. Procesar vacantes desde texto plano (MANUAL):
   python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted
   python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --run-dataset-conversion
   Ver GUIA_EXTRACTOR_TEXTO_PLANO.md para más detalles

4. Procesar vacantes desde YAML estructurado (MANUAL):
   python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes
   python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl

5. Generar dataset de líneas:
   python .\scripts\convert_to_line_dataset.py --input .\data\training_data.jsonl --outdir .\data

6. Revisar/etiquetar:
   python .\scripts\review_label_tool.py --input .\data\line_dataset_review.jsonl --out .\data\line_dataset_review_labeled.jsonl

7. Entrenar (baseline TF-IDF):
   python .\scripts\train_tfidf_baseline.py data/line_dataset.jsonl

## Extractor de Vacantes desde Texto Plano (NUEVO)

Módulo para procesar vacantes en texto desestructurado y extraer automáticamente campos clave.

### Características:
- Extrae automáticamente: cargo, empresa, fecha, descripcion, requerimientos, modalidad
- Normaliza nombres de archivo: minúsculas, sin tildes, sin espacios
- Genera archivos YAML estructurados
- Ejecuta conversión a dataset de líneas automáticamente
- Reportes de calidad con sugerencias de mejora
- Soporta múltiples formatos de entrada (texto libre, bullets, listas, etc.)

### Uso:
```bash
# Extracción básica
python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted

# Extracción + conversión a dataset
python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --run-dataset-conversion --dataset-output data

# Con reporte detallado
python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --generate-report
```

Ver **GUIA_EXTRACTOR_TEXTO_PLANO.md** para documentación completa.

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
