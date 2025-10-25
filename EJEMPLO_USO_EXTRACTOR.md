# Ejemplo: Uso del Extractor de Vacantes

Este ejemplo demuestra cómo usar el extractor de vacantes desde texto plano.

## Paso 1: Preparar el archivo de entrada

Crear un archivo `mi_vacante.txt` con contenido en texto libre:

```
Desarrollador Full Stack Senior - TechStart Solutions

TechStart Solutions busca un desarrollador full stack con experiencia en React y Node.js para unirse a nuestro equipo de desarrollo.

Sobre el puesto:
Trabajarás en proyectos innovadores desarrollando aplicaciones web modernas. Serás parte de un equipo ágil colaborando directamente con diseñadores y product managers.

Requerimientos:
- 5+ años de experiencia en desarrollo web
- Dominio de React, Node.js y TypeScript
- Experiencia con bases de datos SQL y NoSQL
- Conocimientos de Docker y CI/CD
- Inglés intermedio-avanzado

Modalidad: Híbrido (3 días remoto, 2 días oficina)
Ubicación: Bogotá, Colombia
Fecha: 2025-01-28
```

## Paso 2: Ejecutar el extractor

```bash
# Extracción básica
python scripts/extract_vacantes_from_text.py \
  --input mi_vacante.txt \
  --output output/mi_extraccion

# Con conversión a dataset
python scripts/extract_vacantes_from_text.py \
  --input mi_vacante.txt \
  --output output/mi_extraccion \
  --run-dataset-conversion \
  --dataset-output data

# Con reporte completo
python scripts/extract_vacantes_from_text.py \
  --input mi_vacante.txt \
  --output output/mi_extraccion \
  --run-dataset-conversion \
  --dataset-output data \
  --generate-report
```

## Paso 3: Verificar resultados

### Archivos generados:

1. **YAML estructurado**: `output/mi_extraccion/desarrollador_full_stack_senior_techstart_solutions_2025-01-28.yaml`

```yaml
cargo: Desarrollador Full Stack Senior
empresa: TechStart Solutions
fecha: '2025-01-28'
modalidad: Híbrido (3 días remoto
descripcion: |
  Trabajarás en proyectos innovadores desarrollando aplicaciones web modernas. 
  Serás parte de un equipo ágil colaborando directamente con diseñadores y 
  product managers.
requerimientos: |
  - 5+ años de experiencia en desarrollo web
  - Dominio de React, Node.js y TypeScript
  - Experiencia con bases de datos SQL y NoSQL
  - Conocimientos de Docker y CI/CD
  - Inglés intermedio-avanzado
```

2. **Reporte de extracción**: `output/mi_extraccion/extraction_report.txt`

```
======================================================================
REPORTE DE EXTRACCIÓN DE VACANTES
======================================================================

RESUMEN
----------------------------------------------------------------------
Total procesadas: 1
Exitosas: 1
Fallidas: 0
Calidad promedio: 100.0/100

CAMPOS EXTRAÍDOS
----------------------------------------------------------------------
  ✓ cargo: 1
  ✓ empresa: 1
  ✓ fecha: 1
  ✓ descripcion: 1
  ✓ requerimientos: 1
  ✓ modalidad: 1
```

3. **Dataset de líneas**: `data/line_dataset.jsonl`, `data/line_dataset.csv`

## Paso 4: Usar el dataset para entrenamiento

```bash
# Entrenar clasificador baseline
python scripts/train_tfidf_baseline.py data/line_dataset.jsonl

# Entrenar clasificador de líneas
python scripts/train_line_classifier.py data/line_dataset.jsonl
```

## Ejemplo con múltiples vacantes

Archivo `varias_vacantes.txt`:

```
Data Scientist - AnalyticsPro

Buscamos un científico de datos con experiencia en ML para nuestro equipo en AnalyticsPro.

Requisitos:
- Python y R
- Experiencia con modelos predictivos
- 3+ años en ciencia de datos

Modalidad: Remoto
Fecha: 2025-01-28

---

DevOps Engineer - CloudSystems Inc.

CloudSystems Inc. busca ingeniero DevOps para gestionar infraestructura cloud.

Must have:
- Kubernetes y Docker
- AWS/Azure/GCP
- CI/CD pipelines
- 4+ años de experiencia

Work mode: Remote
Published: 2025-01-28
```

Procesar:

```bash
python scripts/extract_vacantes_from_text.py \
  --input varias_vacantes.txt \
  --output output/batch_enero \
  --run-dataset-conversion \
  --dataset-output data/batch_enero
```

Resultado:
- 2 archivos YAML generados
- Dataset con todas las líneas combinadas
- Reporte comparativo de calidad

## Consejos para mejor extracción

1. **Incluir etiquetas claras**:
   - `Cargo:`, `Empresa:`, `Fecha:`
   - `Requerimientos:`, `Modalidad:`

2. **Usar formatos estándar**:
   - Fecha: YYYY-MM-DD
   - Listas: bullets (-) o numeradas (1.)

3. **Separar vacantes**:
   - Usar `---` entre vacantes
   - O dejar líneas vacías dobles

4. **Incluir información completa**:
   - Nombre completo de la empresa
   - Título del cargo
   - Descripción clara del rol
   - Requerimientos específicos

## Troubleshooting

### Problema: Cargo mal extraído

**Antes**:
```
Estamos buscando desarrollador backend con experiencia en Java...
```
**Cargo extraído**: "Estamos buscando desarrollador backend con experiencia en Java..."

**Solución**: Usar formato explícito
```
Cargo: Desarrollador Backend Java

Estamos buscando desarrollador backend con experiencia en Java...
```
**Cargo extraído**: "Desarrollador Backend Java" ✓

### Problema: Empresa no detectada

**Antes**:
```
Buscamos ingeniero de software...
```
**Empresa**: NO EXTRAÍDO

**Solución**: Incluir nombre de empresa
```
Empresa: MiCompany Inc.

Buscamos ingeniero de software...
```
**Empresa**: "MiCompany Inc." ✓

### Problema: Requerimientos incompletos

**Antes**:
```
Necesitas tener experiencia en Python, JavaScript y bases de datos.
```
**Requerimientos**: "No se pudieron extraer requerimientos específicos"

**Solución**: Usar lista estructurada
```
Requerimientos:
- Experiencia en Python
- Conocimiento de JavaScript
- Manejo de bases de datos
```
**Requerimientos**: Lista completa extraída ✓
