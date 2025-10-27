# proyecto_vacantes

Repositorio centralizado para gestión completa de vacantes y hojas de vida. Incluye procesamiento de vacantes, generación de documentos, almacenamiento de CVs y entrenamiento de clasificadores ML.

## 🎯 Flujo Automatizado de Trabajo

Este repositorio implementa un flujo completamente automatizado para el manejo de vacantes:

1. **Crear/Modificar** vacantes en formato YAML en `/vacantes_yaml_manual/`
2. **Automático**: GitHub Actions detecta cambios y copia archivos a `/to_process/`
3. **Automático**: Se procesan las vacantes y se generan CVs
4. **Automático**: CVs se organizan en `/aplicaciones/` por fecha (año/mes/día)

Todo funciona de forma centralizada, sin dependencias de repositorios externos.

## 📁 Estructura del Repositorio

```
proyecto_vacantes_modelo_entrenamiento/
├── vacantes_yaml_manual/    # Vacantes en formato YAML (crear/editar aquí)
├── to_process/              # Vacantes pendientes de procesamiento (automático)
├── aplicaciones/            # CVs generados organizados por fecha (automático)
│   └── YYYY/MM/DD/         # Estructura: año/mes/día
├── scripts/                 # Scripts Python para procesamiento y automatización
├── data/                    # Datasets ML (no versionar)
├── models/                  # Modelos entrenados (no versionar)
├── output/                  # Archivos generados (no versionar)
├── backups/                 # Respaldos
└── .github/workflows/       # GitHub Actions para automatización
```

## 🚀 Inicio Rápido

### Configuración Inicial

1. Crear y activar entorno virtual:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\Activate.ps1
   # Linux/Mac:
   source venv/bin/activate
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Uso del Flujo Automatizado

#### Opción 1: Flujo Automático (Recomendado)

1. Crear o modificar vacante YAML en `/vacantes_yaml_manual/`:
   ```bash
   # Editar archivo existente o crear uno nuevo
   nano vacantes_yaml_manual/mi_nueva_vacante.yaml
   ```

2. Commit y push:
   ```bash
   git add vacantes_yaml_manual/mi_nueva_vacante.yaml
   git commit -m "Agregar nueva vacante"
   git push
   ```

3. **¡GitHub Actions hace el resto automáticamente!**
   - Copia la vacante a `/to_process/`
   - Procesa y genera el CV
   - Organiza el CV en `/aplicaciones/YYYY/MM/DD/`

#### Opción 2: Procesamiento Manual

Si prefieres procesar localmente sin esperar a GitHub Actions:

1. Copiar vacantes a procesar:
   ```bash
   python scripts/copy_to_process.py --all
   ```

2. Procesar vacantes y organizar CVs:
   ```bash
   python scripts/process_and_organize_cv.py
   ```

3. Verificar CVs organizados:
   ```bash
   ls -R aplicaciones/
   ```

## 📋 Formato de Vacante YAML

Las vacantes deben seguir este formato en `/vacantes_yaml_manual/`:

```yaml
cargo: "Business Analyst"
empresa: "Tech Solutions Inc"
fecha: "2025-10-27"
modalidad: "remoto"
descripcion: |
  Descripción detallada del puesto.
  Puede incluir múltiples líneas y párrafos.
  
  Responsabilidades principales:
  - Responsabilidad 1
  - Responsabilidad 2

requerimientos:
  - Requisito 1: Experiencia en análisis de datos
  - Requisito 2: Conocimiento de SQL y Python
  - Requisito 3: Excelentes habilidades de comunicación
```

**Campos requeridos:**
- `cargo`: Nombre del puesto
- `empresa`: Nombre de la empresa
- `fecha`: Fecha en formato YYYY-MM-DD
- `descripcion`: Descripción del puesto
- `requerimientos`: Lista de requisitos

**Campos opcionales:**
- `modalidad`: remoto, híbrido, presencial
- `ubicacion`: Ubicación geográfica
- `tipo_contrato`: Full-time, Part-time, Contract, etc.

## 🔄 Scripts de Procesamiento Avanzado

### 1. Extracción de Vacantes desde Texto Plano

Para procesar vacantes en formato de texto desestructurado:

```bash
# Extracción básica
python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted

# Extracción + conversión a dataset
python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --run-dataset-conversion
```

Ver **GUIA_EXTRACTOR_TEXTO_PLANO.md** para más detalles.

### 2. Procesamiento de Vacantes YAML Múltiples

Para procesar archivos con múltiples vacantes YAML separadas por `---`:

```bash
# Generar archivos YAML individuales
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes

# Procesar y convertir a JSONL
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl
```

### 3. Generación de Datasets ML

```bash
# Generar dataset de líneas
python scripts/convert_to_line_dataset.py --input data/training_data.jsonl --outdir data

# Revisar y etiquetar
python scripts/review_label_tool.py --input data/line_dataset_review.jsonl --out data/line_dataset_review_labeled.jsonl

# Entrenar clasificador (baseline TF-IDF)
python scripts/train_tfidf_baseline.py data/line_dataset.jsonl
```

## 📊 Organización de CVs por Fecha

Los CVs generados se organizan automáticamente por fecha en la siguiente estructura:

```
aplicaciones/
├── 2025/
│   ├── 10/
│   │   ├── 25/
│   │   │   ├── analista_bi_2025-10-25.yaml
│   │   │   └── business_analyst_2025-10-25.yaml
│   │   ├── 26/
│   │   │   ├── data_analyst_2025-10-26.yaml
│   │   │   └── bi_developer_2025-10-26.yaml
│   │   └── 27/
│   │       └── senior_developer_2025-10-27.yaml
│   └── 11/
│       └── ...
└── 2024/
    └── ...
```

Esta estructura facilita:
- **Búsqueda rápida** de CVs por fecha
- **Organización cronológica** de aplicaciones
- **Trazabilidad** del historial de vacantes
- **Archivo eficiente** de documentos

## 🔧 Scripts de Automatización

### copy_to_process.py

Copia vacantes desde `vacantes_yaml_manual/` a `to_process/`:

```bash
# Copiar solo archivos modificados (usado por GitHub Actions)
python scripts/copy_to_process.py

# Copiar todos los archivos
python scripts/copy_to_process.py --all
```

### process_and_organize_cv.py

Procesa vacantes de `to_process/` y organiza CVs en `aplicaciones/`:

```bash
# Procesamiento estándar
python scripts/process_and_organize_cv.py

# Modo silencioso
python scripts/process_and_organize_cv.py --quiet
```

## 🤖 GitHub Actions

El repositorio incluye workflows automatizados:

### process_vacancies.yml

**Trigger**: Cambios en `vacantes_yaml_manual/*.yaml`

**Acciones**:
1. Detecta archivos YAML modificados/agregados
2. Copia a `to_process/`
3. Procesa vacantes y genera CVs
4. Organiza CVs en `aplicaciones/` por fecha
5. Commit y push automático de cambios

**Uso**: Simplemente haz push de cambios en `vacantes_yaml_manual/` y el workflow se ejecuta automáticamente.

## 📚 Documentación Adicional

- **GUIA_EXTRACTOR_TEXTO_PLANO.md**: Guía completa del extractor de texto plano
- **GUIA_PROCESADOR_VACANTES.md**: Guía del procesador de vacantes YAML
- **EJEMPLO_USO_EXTRACTOR.md**: Ejemplos prácticos de uso
- **RESUMEN_IMPLEMENTACION.md**: Resumen de la implementación del módulo
- **RECOVERY_GUIDE.md**: Guía de recuperación ante problemas

## Extractor de Vacantes desde Texto Plano

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
