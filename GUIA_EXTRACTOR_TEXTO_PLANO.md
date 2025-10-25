# Guía de Uso: Extractor de Vacantes desde Texto Plano

## Descripción General

El módulo `extract_vacantes_from_text.py` procesa vacantes en **texto plano/desestructurado** y extrae automáticamente los campos clave usando técnicas de procesamiento de lenguaje natural (NLP) y patrones regex.

## Características Principales

- **Extracción automática de campos**: cargo, empresa, fecha, descripción, requerimientos, modalidad
- **Normalización de nombres de archivo**: minúsculas, sin tildes, sin espacios, sin caracteres especiales
- **Generación de YAML estructurado**: formato estándar compatible con el pipeline de ML
- **Integración con convert_to_line_dataset.py**: conversión automática a dataset de líneas
- **Reportes detallados**: métricas de calidad, campos extraídos, sugerencias de mejora
- **Soporte para múltiples formatos**: texto libre, bullets, listas numeradas, etc.

## Instalación

```bash
# Asegurarse de tener las dependencias instaladas
pip install -r requirements.txt
```

## Uso Básico

### 1. Extracción Simple

Procesa un archivo de texto y genera archivos YAML estructurados:

```bash
python scripts/extract_vacantes_from_text.py \
  --input mi_vacante.txt \
  --output output/extracted
```

### 2. Extracción + Conversión a Dataset

Extrae campos, genera YAMLs y ejecuta la conversión a dataset de líneas:

```bash
python scripts/extract_vacantes_from_text.py \
  --input mi_vacante.txt \
  --output output/extracted \
  --run-dataset-conversion \
  --dataset-output data
```

### 3. Extracción con Reporte Detallado

Genera reportes de calidad y sugerencias de mejora:

```bash
python scripts/extract_vacantes_from_text.py \
  --input mi_vacante.txt \
  --output output/extracted \
  --generate-report
```

### 4. Flujo Completo

Extracción + conversión + reporte:

```bash
python scripts/extract_vacantes_from_text.py \
  --input mi_vacante.txt \
  --output output/extracted \
  --run-dataset-conversion \
  --dataset-output data \
  --generate-report
```

## Formato del Archivo de Entrada

### Texto Libre (Desestructurado)

El módulo acepta vacantes en **texto plano sin estructura específica**. Puede contener una o varias vacantes separadas por `---` o bloques de texto separados por líneas vacías dobles.

#### Ejemplo 1: Vacante en texto libre

```text
Estamos buscando un Senior Data Scientist para unirse a nuestro equipo en TechCorp Solutions.

El candidato ideal tendrá experiencia trabajando con grandes volúmenes de datos y modelos de machine learning.

Requerimientos:
- Más de 5 años de experiencia en ciencia de datos
- Dominio de Python y librerías como scikit-learn, TensorFlow
- Experiencia con SQL y bases de datos relacionales
- Inglés avanzado

Modalidad: Remoto
Publicado: 2025-01-25
```

#### Ejemplo 2: Múltiples vacantes separadas

```text
Business Intelligence Analyst - DataMind Inc

DataMind Inc está en búsqueda de un Analista BI con experiencia en visualización.

Requisitos:
1. 3+ años en roles de BI
2. Experto en Power BI y/o Tableau
3. SQL avanzado

Modalidad: Híbrido
Fecha: 25/01/2025

---

DevOps Engineer at CloudTech Global

Join our team and help us build scalable infrastructure.

Must have:
- 4+ years DevOps experience
- Docker and Kubernetes
- AWS or Azure certification

Work mode: Remote
```

## Campos Extraídos

El módulo intenta extraer los siguientes campos:

| Campo | Descripción | Requerido |
|-------|-------------|-----------|
| **cargo** | Título del puesto (Developer, Analyst, etc.) | Sí |
| **empresa** | Nombre de la empresa u organización | Sí |
| **fecha** | Fecha de publicación (normalizada a YYYY-MM-DD) | Sí (usa fecha actual si no se encuentra) |
| **descripcion** | Descripción del puesto y responsabilidades | Sí |
| **requerimientos** | Requisitos y calificaciones necesarias | Sí |
| **modalidad** | Remoto, Híbrido, Presencial | Opcional |

## Nomenclatura de Archivos

Los archivos YAML generados siguen la nomenclatura:

```
{cargo}_{empresa}_{fecha}.yaml
```

Con normalización aplicada:
- **Minúsculas**: todas las letras en minúsculas
- **Sin tildes**: á → a, é → e, etc.
- **Sin espacios**: reemplazados por guiones bajos (_)
- **Sin caracteres especiales**: eliminados
- **Longitud limitada**: máximo 50 caracteres por campo

### Ejemplos de nombres generados:

- `senior_data_scientist_techcorp_solutions_2025-01-25.yaml`
- `business_intelligence_analyst_datamind_inc_2025-01-25.yaml`
- `devops_engineer_cloudtech_global_2025-10-25.yaml`

## Archivos de Salida

### 1. Archivos YAML Individuales

Un archivo YAML por vacante procesada:

```yaml
cargo: Senior Data Scientist
empresa: TechCorp Solutions
fecha: '2025-01-25'
modalidad: Remoto
descripcion: |
  El candidato ideal tendrá experiencia trabajando con grandes 
  volúmenes de datos y modelos de machine learning en producción.
requerimientos: |
  - Más de 5 años de experiencia en ciencia de datos
  - Dominio de Python y librerías como scikit-learn, TensorFlow
  - Experiencia con SQL y bases de datos relacionales
```

### 2. Reporte de Extracción (JSON)

`extraction_report.json` contiene métricas detalladas:

```json
{
  "timestamp": "2025-01-25T10:30:00",
  "total_processed": 3,
  "successful": 3,
  "failed": 0,
  "average_quality_score": 95.0,
  "fields_extracted_counts": {
    "cargo": 3,
    "empresa": 3,
    "fecha": 3,
    "descripcion": 3,
    "requerimientos": 3,
    "modalidad": 2
  },
  "vacancies": [...],
  "suggestions": [...]
}
```

### 3. Reporte de Extracción (Texto)

`extraction_report.txt` es un reporte legible con:
- Resumen general
- Campos extraídos/no extraídos
- Detalle por vacante (calidad, observaciones)
- Sugerencias de mejora
- Instrucciones de uso del dataset

### 4. Dataset de Líneas (si --run-dataset-conversion)

Se generan 3 archivos en el directorio especificado:

- `line_dataset.jsonl`: Dataset en formato JSONL
- `line_dataset.csv`: Dataset en formato CSV
- `line_dataset_review.jsonl`: Ejemplos para revisión manual

## Métricas de Calidad

Cada vacante recibe un **score de calidad de 0-100** basado en:

| Criterio | Puntos |
|----------|--------|
| Cargo extraído correctamente | 20 |
| Empresa extraída correctamente | 20 |
| Descripción presente y completa (>50 chars) | 20 |
| Requerimientos presentes y completos (>20 chars) | 20 |
| Modalidad detectada | 10 |
| Fecha extraída/normalizada | 10 |

## Sugerencias de Mejora

El sistema genera sugerencias automáticas cuando detecta:

- **Campos faltantes**: Recomienda incluir etiquetas explícitas
- **Calidad baja (<60%)**: Sugiere estructurar mejor el texto
- **Campos incompletos**: Indica cómo mejorar la extracción

### Ejemplo de sugerencias:

```
SUGERENCIAS DE MEJORA:
  1. 2 vacantes sin modalidad
     → Especificar modalidad (remoto/híbrido/presencial) de forma explícita

  2. Calidad promedio moderada (75.0/100)
     → Algunos campos no se están extrayendo correctamente. 
       Revise el formato del texto original
```

## Integración con Pipeline de ML

### Flujo Completo

```bash
# 1. Extraer campos y generar dataset
python scripts/extract_vacantes_from_text.py \
  --input vacantes_nuevas.txt \
  --output output/extracted \
  --run-dataset-conversion \
  --dataset-output data

# 2. Entrenar modelo (baseline TF-IDF)
python scripts/train_tfidf_baseline.py data/line_dataset.jsonl

# 3. Entrenar clasificador de líneas
python scripts/train_line_classifier.py data/line_dataset.jsonl
```

## Patrones de Detección

El módulo usa patrones regex y heurísticas para detectar campos:

### Cargo
- Patrones explícitos: `cargo:`, `position:`, `role:`
- Primera línea si parece un título
- Palabras clave: developer, analyst, engineer, manager, etc.

### Empresa
- Patrones explícitos: `empresa:`, `company:`
- Nombres propios con sufijos: Inc, Corp, Ltd, SA, SAS, Group, etc.
- Contexto: "en TechCorp", "at DataMind"

### Fecha
- Formatos soportados: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY
- Patrones: `fecha:`, `date:`, `publicado:`
- Normalización automática a YYYY-MM-DD

### Modalidad
- Palabras clave: remoto, remote, híbrido, hybrid, presencial, on-site
- Patrones: `modalidad:`, `work mode:`

### Descripción
- Secciones etiquetadas: `descripción:`, `about the role:`
- Heurística: bloque de texto más grande
- Fallback: primeras N líneas del texto

### Requerimientos
- Secciones etiquetadas: `requerimientos:`, `requirements:`, `must have:`
- Listas con bullets (`-`, `•`, `*`)
- Listas numeradas (`1.`, `2.`, etc.)

## Consejos para Mejor Extracción

### ✅ Buenas Prácticas

1. **Usar etiquetas claras**:
   ```
   Cargo: Senior Developer
   Empresa: TechCorp
   Fecha: 2025-01-25
   ```

2. **Estructurar requerimientos**:
   ```
   Requerimientos:
   - Python 3.8+
   - 5 años de experiencia
   - Inglés fluido
   ```

3. **Incluir modalidad explícitamente**:
   ```
   Modalidad: Remoto
   ```

4. **Separar múltiples vacantes**:
   ```
   [Vacante 1]
   ---
   [Vacante 2]
   ---
   [Vacante 3]
   ```

### ❌ Evitar

- Mezclar múltiples vacantes sin separadores
- Usar formatos de fecha inconsistentes
- Omitir información clave (empresa, cargo)
- Textos muy cortos (<50 caracteres)

## Solución de Problemas

### Error: "No se pudo extraer cargo"

**Solución**: Incluir el cargo al inicio del texto o usar formato `Cargo: ...`

### Error: "Empresa no detectada"

**Solución**: Usar nombre completo de la empresa con sufijo (Inc, Corp, etc.) o formato `Empresa: ...`

### Error: "Calidad de extracción baja"

**Solución**: Estructurar mejor el texto usando etiquetas claras para cada campo

### Warning: "Fecha no parseada correctamente"

**Solución**: Usar formato estándar YYYY-MM-DD o incluir etiqueta `Fecha: ...`

## Ejemplos Avanzados

### Ejemplo 1: Procesar archivo con múltiples vacantes

```bash
python scripts/extract_vacantes_from_text.py \
  --input vacantes_lote_enero.txt \
  --output output/enero_2025 \
  --run-dataset-conversion \
  --dataset-output data/enero_2025
```

### Ejemplo 2: Modo silencioso para scripts

```bash
python scripts/extract_vacantes_from_text.py \
  --input vacante.txt \
  --output output/extracted \
  --quiet
```

### Ejemplo 3: Solo extracción, sin dataset

```bash
python scripts/extract_vacantes_from_text.py \
  --input vacante.txt \
  --output output/extracted \
  --generate-report
```

## Comparación con process_vacantes.py

| Característica | extract_vacantes_from_text.py | process_vacantes.py |
|---------------|------------------------------|---------------------|
| Formato entrada | Texto plano/desestructurado | YAML estructurado |
| Extracción automática | ✅ Sí | ❌ No (requiere YAML válido) |
| Normalización nombres | ✅ Completa (sin tildes) | ⚠️ Parcial |
| Reportes de calidad | ✅ Sí | ⚠️ Limitado |
| Sugerencias | ✅ Sí | ❌ No |
| Integración dataset | ✅ Automática | ⚠️ Manual |

## Retroalimentación y Mejora Continua

El sistema está diseñado para mejorar con el uso:

1. **Revisar reportes**: Los reportes indican qué campos no se extraen bien
2. **Ajustar patrones**: Si ciertos formatos no se detectan, se pueden agregar nuevos patrones
3. **Validar calidad**: Revisar manualmente vacantes con score <80%
4. **Iterar**: Usar sugerencias para mejorar el formato de entrada

## Soporte

Para problemas o sugerencias:
- Revisar el archivo `extraction_report.txt` para diagnóstico
- Verificar que el texto de entrada tenga formato adecuado
- Consultar ejemplos en esta guía
- Abrir un issue en el repositorio

## Próximos Pasos

Después de la extracción y conversión:

1. **Revisar dataset generado**: 
   ```bash
   python scripts/review_label_tool.py \
     --input data/line_dataset_review.jsonl \
     --out data/line_dataset_labeled.jsonl
   ```

2. **Entrenar modelos**:
   ```bash
   python scripts/train_line_classifier.py data/line_dataset.jsonl
   ```

3. **Evaluar y mejorar**: Usar métricas de los reportes para optimizar la extracción
