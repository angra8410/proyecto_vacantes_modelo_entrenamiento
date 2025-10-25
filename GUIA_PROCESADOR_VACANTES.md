# Guía de Uso: Procesador de Vacantes

## Descripción General
El módulo `process_vacantes.py` procesa archivos con múltiples vacantes en formato YAML, valida su estructura y genera archivos individuales o un archivo consolidado JSONL.

## Instalación de Dependencias
```bash
pip install -r requirements.txt
```

## Uso Básico

### 1. Procesar vacantes y generar archivos YAML individuales
```bash
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes
```

### 2. Procesar y convertir a JSONL
```bash
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl
```

### 3. Especificar nombre personalizado para archivo JSONL
```bash
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl --jsonl-file mis_vacantes.jsonl
```

### 4. Modo silencioso (para scripts)
```bash
python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --quiet
```

## Formato del Archivo de Entrada

El archivo debe contener vacantes en formato YAML separadas por `---`:

```yaml
cargo: Senior Developer
empresa: Tech Corp
fecha: 2025-01-15
descripcion: |
  Descripción detallada del puesto de trabajo.
  Puede incluir múltiples líneas.
requerimientos: |
  - Requisito 1
  - Requisito 2
  - Requisito 3
ubicacion: Colombia (Remote)
tipo_contrato: Full-time
---
cargo: Business Analyst
empresa: Consulting Inc
fecha: 2025-01-20
descripcion: |
  Otra descripción detallada...
requerimientos: |
  - Experiencia en análisis
  - Conocimiento de SQL
---
```

## Campos Requeridos

El módulo valida los siguientes campos obligatorios:
- `cargo`: Nombre del puesto
- `empresa`: Nombre de la empresa
- `fecha`: Fecha en formato YYYY-MM-DD
- `descripcion`: Descripción del puesto
- `requerimientos`: Lista de requisitos

Los campos adicionales son opcionales y se preservan en la salida.

## Validaciones Realizadas

1. **Presencia de campos**: Verifica que todos los campos requeridos estén presentes
2. **Campos vacíos**: Detecta campos que existen pero están vacíos
3. **Formato de fecha**: Valida que la fecha esté en formato YYYY-MM-DD o sea un objeto date válido

## Archivos de Salida

### Archivos YAML Individuales
Se generan con el formato: `{fecha}_{cargo}_{empresa}.yaml`

Ejemplos:
- `2025-01-15_Senior_Developer_Tech_Corp.yaml`
- `2025-01-20_Business_Analyst_Consulting_Inc.yaml`

Los nombres de archivo se sanitizan automáticamente:
- Caracteres especiales se eliminan
- Espacios se reemplazan por guiones bajos
- Se limita la longitud para evitar nombres muy largos

### Archivo JSONL
Cada línea contiene una vacante válida en formato JSON:
```json
{"cargo": "Senior Developer", "empresa": "Tech Corp", "fecha": "2025-01-15", ...}
{"cargo": "Business Analyst", "empresa": "Consulting Inc", "fecha": "2025-01-20", ...}
```

## Manejo de Errores

El módulo reporta errores de manera detallada:

```
⚠️  ERRORES DETECTADOS (2):
----------------------------------------------------------------------

1. Bloque 2:
   • Campo faltante: 'descripcion'
   Cargo: Test Position
   Empresa: Company Name

2. Bloque 3:
   • Campo vacío: 'empresa'
   • Formato de fecha inválido: '01-02-2025' (esperado: YYYY-MM-DD)
   Cargo: Another Position
   Empresa: N/A
```

## Códigos de Salida

- `0`: Todas las vacantes procesadas exitosamente
- `1`: Una o más vacantes inválidas (archivos válidos aún se generan)

## Ejemplo Completo

```bash
# 1. Preparar archivo de entrada
cat > vacantes.txt << EOF
cargo: Python Developer
empresa: AI Solutions
fecha: 2025-02-01
descripcion: Desarrollador Python con experiencia en ML
requerimientos: |
  - Python 3.8+
  - PyTorch o TensorFlow
  - 3+ años de experiencia
---
cargo: Data Analyst
empresa: Analytics Corp
fecha: 2025-02-05
descripcion: Analista de datos con SQL y Python
requerimientos: |
  - SQL avanzado
  - Python/Pandas
  - Tableau o Power BI
EOF

# 2. Procesar y generar archivos YAML + JSONL
python scripts/process_vacantes.py \
  --input vacantes.txt \
  --output output/vacantes \
  --to-jsonl \
  --jsonl-file vacantes.jsonl

# 3. Verificar salida
ls output/vacantes/
# Salida:
# 2025-02-01_Python_Developer_AI_Solutions.yaml
# 2025-02-05_Data_Analyst_Analytics_Corp.yaml
# vacantes.jsonl
```

## Integración con Pipelines de ML

El archivo JSONL generado puede usarse directamente con otros scripts del proyecto:

```bash
# Convertir a dataset de líneas
python scripts/convert_to_line_dataset.py \
  --input output/vacantes/vacantes.jsonl \
  --outdir data

# Entrenar modelo
python scripts/train_line_classifier.py data/line_dataset.jsonl
```

## Solución de Problemas

### Error: "El archivo vacantes.txt no existe"
- Verificar que la ruta del archivo sea correcta
- Usar rutas absolutas o relativas desde el directorio raíz del proyecto

### Error: "Error al parsear YAML"
- Verificar que el archivo tenga formato YAML válido
- Asegurar que los bloques estén separados por `---` en líneas independientes
- Revisar la indentación (YAML es sensible a la indentación)

### Las fechas no se validan correctamente
- Usar formato YYYY-MM-DD (e.g., 2025-01-15)
- Evitar formatos como DD-MM-YYYY o MM/DD/YYYY

### Caracteres especiales en nombres de archivo
- Los caracteres especiales se eliminan automáticamente
- Los espacios se reemplazan por guiones bajos
- Los nombres muy largos se truncan a 50 caracteres

## Recomendaciones

1. **Validar formato antes de procesar**: Usar un validador YAML online para verificar sintaxis
2. **Backup de datos**: Mantener copias del archivo original antes de modificar
3. **Revisión manual**: Después del procesamiento automático, revisar manualmente las vacantes marcadas como inválidas
4. **Retroalimentación continua**: Documentar patrones de error para mejorar la calidad de entrada

## Soporte

Para problemas o sugerencias, abrir un issue en el repositorio del proyecto.
