# Guía Completa: Flujo Centralizado de Vacantes y CVs

## 📖 Descripción General

Esta guía documenta el flujo completo y centralizado para el manejo de vacantes y hojas de vida en un solo repositorio, sin dependencias externas.

## 🎯 Objetivos

- **Simplicidad**: Todo en un solo repositorio
- **Automatización**: Procesamiento automático mediante GitHub Actions
- **Organización**: CVs organizados por fecha para fácil búsqueda
- **Trazabilidad**: Historial completo de vacantes y aplicaciones
- **Eficiencia**: Eliminación de sincronización entre múltiples repositorios

## 📁 Estructura de Carpetas

```
proyecto_vacantes_modelo_entrenamiento/
│
├── vacantes_yaml_manual/        # ✏️ CREAR/EDITAR VACANTES AQUÍ
│   ├── vacante1.yaml           # Vacantes en formato YAML
│   ├── vacante2.yaml
│   └── ...
│
├── to_process/                  # 🔄 PROCESAMIENTO AUTOMÁTICO
│   ├── vacante1.yaml           # Vacantes copiadas automáticamente
│   └── processed/              # Vacantes ya procesadas (respaldo)
│       └── ...
│
├── aplicaciones/                # 📁 CVs ORGANIZADOS POR FECHA
│   ├── 2025/
│   │   ├── 10/
│   │   │   ├── 25/
│   │   │   │   ├── cv1.yaml
│   │   │   │   └── cv2.yaml
│   │   │   ├── 26/
│   │   │   └── 27/
│   │   └── 11/
│   └── 2024/
│
├── scripts/                     # 🔧 SCRIPTS DE AUTOMATIZACIÓN
│   ├── copy_to_process.py      # Copia vacantes a to_process/
│   ├── process_and_organize_cv.py  # Procesa y organiza CVs
│   ├── extract_vacantes_from_text.py  # Extrae desde texto plano
│   └── ...
│
└── .github/workflows/           # ⚙️ GITHUB ACTIONS
    └── process_vacancies.yml   # Workflow principal
```

## 🔄 Flujo de Trabajo Completo

### Paso 1: Crear/Editar Vacante

**Dónde**: `/vacantes_yaml_manual/`

**Cómo**:
1. Crear nuevo archivo YAML o editar existente
2. Seguir el formato requerido (ver sección de Formato)
3. Guardar archivo

**Ejemplo**:
```yaml
# vacantes_yaml_manual/data_analyst_techcorp_2025-10-27.yaml

cargo: "Data Analyst"
empresa: "TechCorp Solutions"
fecha: "2025-10-27"
modalidad: "remoto"
descripcion: |
  Buscamos un Data Analyst para unirse a nuestro equipo.
  
  Responsabilidades:
  - Análisis de datos empresariales
  - Creación de dashboards
  - Reportes ejecutivos
  
requerimientos:
  - 3+ años de experiencia en análisis de datos
  - Dominio de SQL y Python
  - Experiencia con Power BI o Tableau
  - Excelentes habilidades de comunicación
```

### Paso 2: Commit y Push

**Comando**:
```bash
git add vacantes_yaml_manual/data_analyst_techcorp_2025-10-27.yaml
git commit -m "Agregar vacante Data Analyst - TechCorp"
git push
```

### Paso 3: GitHub Actions (Automático)

**Trigger**: Push a `vacantes_yaml_manual/*.yaml`

**Proceso Automático**:

1. **Detecta cambios**
   - GitHub Actions identifica archivos modificados/agregados
   - Solo procesa archivos `.yaml` en `vacantes_yaml_manual/`

2. **Copia a to_process**
   - Ejecuta `scripts/copy_to_process.py`
   - Copia archivos modificados a `/to_process/`

3. **Procesa vacantes**
   - Ejecuta `scripts/process_and_organize_cv.py`
   - Lee vacantes de `/to_process/`
   - Genera documentos/CVs

4. **Organiza CVs**
   - Extrae fecha de la vacante
   - Crea estructura `aplicaciones/YYYY/MM/DD/`
   - Copia CV a la ubicación correspondiente
   - Mueve vacante procesada a `/to_process/processed/`

5. **Commit automático**
   - Guarda cambios en el repositorio
   - Push automático con mensaje `[skip ci]`

### Paso 4: Verificación

**Verificar CVs organizados**:
```bash
# Ver estructura de aplicaciones
ls -R aplicaciones/

# Ver CVs de una fecha específica
ls aplicaciones/2025/10/27/
```

## 📋 Formato de Vacante YAML

### Campos Requeridos

```yaml
cargo: "string"           # Nombre del puesto
empresa: "string"         # Nombre de la empresa
fecha: "YYYY-MM-DD"      # Fecha en formato ISO
descripcion: |            # Descripción del puesto (multilinea)
  Texto descriptivo...
requerimientos:           # Lista de requisitos
  - Requisito 1
  - Requisito 2
```

### Campos Opcionales

```yaml
modalidad: "string"       # remoto, híbrido, presencial
ubicacion: "string"       # Ciudad, país
tipo_contrato: "string"   # Full-time, Part-time, Contract
salario: "string"         # Rango salarial
```

### Ejemplo Completo

```yaml
cargo: "Senior Business Analyst"
empresa: "Global Tech Inc"
fecha: "2025-10-27"
modalidad: "híbrido"
ubicacion: "Bogotá, Colombia"
tipo_contrato: "Full-time"
salario: "Competitivo"

descripcion: |
  Buscamos un Business Analyst senior con experiencia en proyectos 
  de transformación digital.
  
  Responsabilidades:
  - Análisis de requerimientos de negocio
  - Documentación de procesos
  - Coordinación con equipos técnicos
  - Gestión de stakeholders

requerimientos:
  - 5+ años como Business Analyst
  - Experiencia en metodologías ágiles (Scrum, Kanban)
  - Conocimiento de herramientas: Jira, Confluence
  - Inglés avanzado (B2+)
  - Certificación CBAP (deseable)
```

## 🔧 Uso Manual de Scripts

Si prefieres ejecutar los scripts manualmente sin esperar a GitHub Actions:

### Script 1: Copiar a to_process

```bash
# Copiar solo archivos modificados (usado por GitHub Actions)
python scripts/copy_to_process.py

# Copiar todos los archivos
python scripts/copy_to_process.py --all

# Modo silencioso
python scripts/copy_to_process.py --quiet
```

**Opciones**:
- `--source DIR`: Directorio fuente (default: vacantes_yaml_manual)
- `--dest DIR`: Directorio destino (default: to_process)
- `--all`: Copiar todos los archivos, no solo modificados
- `--quiet, -q`: Modo silencioso

### Script 2: Procesar y Organizar CVs

```bash
# Procesamiento estándar
python scripts/process_and_organize_cv.py

# Especificar directorios personalizados
python scripts/process_and_organize_cv.py \
  --to-process-dir mi_proceso \
  --aplicaciones-dir mis_aplicaciones

# Modo silencioso
python scripts/process_and_organize_cv.py --quiet
```

**Opciones**:
- `--to-process-dir DIR`: Directorio con vacantes a procesar (default: to_process)
- `--aplicaciones-dir DIR`: Directorio base para CVs (default: aplicaciones)
- `--quiet, -q`: Modo silencioso

## 📊 Organización de CVs por Fecha

### Estructura Jerárquica

```
aplicaciones/
└── YYYY/              # Año
    └── MM/            # Mes (01-12)
        └── DD/        # Día (01-31)
            └── archivo.yaml
```

### Beneficios

1. **Búsqueda Rápida**: Encontrar CVs por fecha específica
2. **Organización Cronológica**: Orden temporal claro
3. **Facilidad de Archivo**: Estructura intuitiva
4. **Escalabilidad**: Soporta crecimiento ilimitado

### Ejemplos de Rutas

```
aplicaciones/2025/10/27/senior_developer_techcorp_2025-10-27.yaml
aplicaciones/2025/11/15/business_analyst_consulting_2025-11-15.yaml
aplicaciones/2024/12/20/data_scientist_startup_2024-12-20.yaml
```

## 🤖 GitHub Actions Workflow

### Configuración: .github/workflows/process_vacancies.yml

```yaml
name: Process Vacancies and Organize CVs

on:
  push:
    paths:
      - 'vacantes_yaml_manual/*.yaml'

jobs:
  process_vacancies:
    runs-on: ubuntu-latest
    steps:
      - Checkout repository
      - Set up Python
      - Install dependencies
      - Copy to to_process
      - Process and organize CVs
      - Commit and push changes
```

### Características

- **Trigger selectivo**: Solo se ejecuta con cambios en `vacantes_yaml_manual/*.yaml`
- **Procesamiento eficiente**: Solo procesa archivos modificados
- **Commit inteligente**: Solo hace commit si hay cambios
- **Skip CI**: Evita bucles infinitos con `[skip ci]`

## 🔍 Trazabilidad y Auditoría

### Historial de Git

Cada vacante y CV queda registrado en el historial de Git:

```bash
# Ver historial de una vacante
git log -- vacantes_yaml_manual/mi_vacante.yaml

# Ver historial de CVs de una fecha
git log -- aplicaciones/2025/10/27/

# Ver todos los cambios recientes
git log --oneline --graph --all
```

### Respaldos

Las vacantes procesadas se mueven a `/to_process/processed/` como respaldo:

```bash
# Ver vacantes procesadas
ls to_process/processed/

# Restaurar una vacante procesada
cp to_process/processed/mi_vacante.yaml vacantes_yaml_manual/
```

## 🚨 Solución de Problemas

### Problema: GitHub Actions no se ejecuta

**Posibles causas**:
- Cambios en archivos que no son YAML
- Cambios fuera de `vacantes_yaml_manual/`
- Workflow deshabilitado

**Solución**:
```bash
# Verificar que el archivo esté en la ruta correcta
ls vacantes_yaml_manual/*.yaml

# Verificar que el workflow esté habilitado
# En GitHub: Actions > Workflows > Process Vacancies > Enable
```

### Problema: CV no se organizó correctamente

**Posible causa**: Fecha inválida en el YAML

**Solución**:
```bash
# Verificar formato de fecha en el YAML
# Debe ser: YYYY-MM-DD

# Ejemplo correcto:
fecha: "2025-10-27"

# Ejemplo incorrecto:
fecha: "27/10/2025"  # ❌
```

### Problema: Vacante no se procesó

**Diagnóstico**:
```bash
# Verificar logs de GitHub Actions
# En GitHub: Actions > último workflow run > Ver logs

# Ejecutar manualmente para ver errores
python scripts/process_and_organize_cv.py
```

## 📈 Mejores Prácticas

### 1. Nomenclatura de Archivos

Usar formato descriptivo:
```
{cargo}_{empresa}_{fecha}.yaml

Ejemplos:
- senior_developer_techcorp_2025-10-27.yaml
- business_analyst_consulting_2025-11-15.yaml
- data_scientist_startup_2025-12-20.yaml
```

### 2. Commits Descriptivos

```bash
# ✅ Bueno
git commit -m "Agregar vacante Senior Developer - TechCorp"

# ✅ Bueno
git commit -m "Actualizar requisitos de Business Analyst - Consulting Inc"

# ❌ Malo
git commit -m "Update"
git commit -m "cambios"
```

### 3. Validación Previa

Antes de hacer push, verificar el YAML:

```bash
# Verificar sintaxis YAML
python -c "import yaml; yaml.safe_load(open('vacantes_yaml_manual/mi_vacante.yaml'))"

# Si no hay output, el YAML es válido
```

### 4. Revisión de CVs

Periódicamente revisar los CVs organizados:

```bash
# Ver CVs del mes actual
ls aplicaciones/$(date +%Y)/$(date +%m)/

# Contar CVs por mes
find aplicaciones/ -type f | cut -d'/' -f2,3 | sort | uniq -c
```

## 🔐 Seguridad

### No Versionar Datos Sensibles

El `.gitignore` ya excluye:
- Datos personales (`data/`)
- Modelos entrenados (`models/`)
- Archivos temporales (`output/`)

### Datos a Versionar

✅ **Sí versionar**:
- Vacantes en `vacantes_yaml_manual/`
- CVs en `aplicaciones/` (si no contienen datos sensibles)
- Scripts y configuraciones

❌ **No versionar**:
- Datos de entrenamiento en `data/`
- Modelos en `models/`
- Archivos temporales en `output/`

## 📚 Referencias

- **GUIA_EXTRACTOR_TEXTO_PLANO.md**: Extracción desde texto desestructurado
- **GUIA_PROCESADOR_VACANTES.md**: Procesamiento de YAML múltiples
- **EJEMPLO_USO_EXTRACTOR.md**: Ejemplos prácticos
- **README.md**: Guía rápida del repositorio

## 🎓 Ejemplos de Uso

### Ejemplo 1: Agregar Nueva Vacante

```bash
# 1. Crear archivo YAML
cat > vacantes_yaml_manual/python_developer_startup_2025-10-27.yaml << EOF
cargo: "Python Developer"
empresa: "AI Startup"
fecha: "2025-10-27"
modalidad: "remoto"
descripcion: |
  Desarrollador Python para proyecto de IA.
requerimientos:
  - Python avanzado
  - FastAPI o Django
  - Docker y Kubernetes
EOF

# 2. Commit y push
git add vacantes_yaml_manual/python_developer_startup_2025-10-27.yaml
git commit -m "Agregar vacante Python Developer - AI Startup"
git push

# 3. GitHub Actions procesa automáticamente
# 4. Verificar resultado
git pull
ls aplicaciones/2025/10/27/
```

### Ejemplo 2: Procesamiento Manual de Múltiples Vacantes

```bash
# 1. Copiar todas las vacantes a to_process
python scripts/copy_to_process.py --all

# 2. Procesar todas
python scripts/process_and_organize_cv.py

# 3. Ver resultados
find aplicaciones/ -name "*.yaml" -type f | head -10
```

### Ejemplo 3: Buscar CVs por Fecha

```bash
# CVs de octubre 2025
ls aplicaciones/2025/10/*/

# CVs de un día específico
ls aplicaciones/2025/10/27/

# Contar CVs por día
find aplicaciones/2025/10/ -name "*.yaml" | wc -l
```

## 🏆 Conclusión

Este flujo centralizado proporciona:

✅ **Simplicidad**: Todo en un repositorio  
✅ **Automatización**: GitHub Actions maneja el flujo  
✅ **Organización**: CVs por fecha año/mes/día  
✅ **Trazabilidad**: Historial completo en Git  
✅ **Eficiencia**: Sin dependencias externas  

**¡Listo para usar!** 🚀
