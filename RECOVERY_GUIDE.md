# Guía de Recuperación de Scripts y Gestión de Ramas

Este documento describe el proceso seguro para recuperar scripts y gestionar ramas limpias en el repositorio.

## Problema Común: Archivos Grandes o Entornos Virtuales Accidentalmente Comiteados

### Síntomas
- Push rechazado por archivos mayores a 100MB
- `.gitignore` no funcionando correctamente (ignora todo)
- Archivos de `venv/` o `data/` accidentalmente trackeados

### Solución: Verificación Pre-Commit

Antes de hacer commit, **siempre** ejecutar:

```bash
# En PowerShell
git status --short
git ls-files | Select-String '^venv/' 
git ls-files | Select-String '^data/'
git ls-files | Select-String '^models/'

# En Linux/Mac
git status --short
git ls-files | grep '^venv/'
git ls-files | grep '^data/'
git ls-files | grep '^models/'
```

Si estos comandos muestran archivos, **NO** hacer commit. Primero limpiar el índice.

### Limpiar Archivos del Índice

```bash
# Quitar archivos del índice sin borrar localmente
git rm -r --cached venv
git rm -r --cached data
git rm -r --cached models

# Verificar que se quitaron
git status
```

## Recuperación de Scripts desde Commit Anterior

Si perdiste archivos del working tree y necesitas recuperarlos desde un commit anterior:

```bash
# 1. Identificar el commit que tiene los archivos
git log --oneline --all

# 2. Crear rama limpia desde main
git checkout main
git checkout -b add-local-files-clean

# 3. Recuperar archivos específicos desde commit
git checkout <COMMIT_SHA> -- scripts/

# 4. Verificar que SOLO scripts están staged
git status
git ls-files | Select-String '^venv/' || Write-Host "✓ Sin venv"
git ls-files | Select-String '^data/' || Write-Host "✓ Sin data"

# 5. Commit seguro
git commit -m "Recover scripts from commit <COMMIT_SHA>"

# 6. Push de rama limpia
git push origin add-local-files-clean
```

## Crear Pull Request

### Título sugerido
```
Recover project scripts and add for review
```

### Descripción sugerida
```markdown
## Descripción
Recupera la carpeta `scripts/` desde un commit anterior y añade utilidades para:
- Normalización y conversión de datasets
- Herramienta de revisión y etiquetado interactivo
- Entrenamiento de modelo baseline con TF-IDF

## Checklist de revisión
- [x] Sólo scripts y archivos de código incluidos
- [x] `venv/`, `data/`, `models/` NO presentes
- [x] No hay archivos >100MB
- [x] Rama principal (`main`) no modificada directamente
- [x] `.gitignore` actualizado correctamente

## Archivos incluidos
- `scripts/convert_to_line_dataset.py` - Conversión de datos a formato línea por línea
- `scripts/review_label_tool.py` - Herramienta interactiva de etiquetado
- `scripts/train_tfidf_baseline.py` - Entrenamiento de clasificador baseline
- `requirements.txt` - Dependencias Python necesarias
- `.gitignore` - Configuración para ignorar venv, data, models

Por favor revisar antes de mergear.
```

## Prevención: .gitignore Correcto

Asegúrate de que tu `.gitignore` incluye:

```gitignore
# Virtual environment
venv/
env/
ENV/
.venv/

# Data files
data/
*.csv
*.jsonl
*.pkl

# Model files
models/
*.h5
*.pt
*.pth
*.model

# Python
__pycache__/
*.py[cod]
```

## Limpieza de Historia (Avanzado)

⚠️ **ADVERTENCIA**: Solo usar si ya subiste archivos grandes y necesitas limpiar la historia.

### Usando BFG Repo-Cleaner

```bash
# 1. Hacer backup del repositorio
git clone --mirror https://github.com/usuario/repo.git repo-backup.git

# 2. Descargar BFG
# https://rtyley.github.io/bfg-repo-cleaner/

# 3. Limpiar archivos grandes
java -jar bfg.jar --strip-blobs-bigger-than 100M repo.git

# 4. Limpiar reflog y garbage collection
cd repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push (PELIGROSO - coordinar con equipo)
git push --force
```

### Usando git-filter-repo

```bash
# 1. Instalar git-filter-repo
pip install git-filter-repo

# 2. Eliminar directorios completos de la historia
git filter-repo --path venv --invert-paths
git filter-repo --path data --invert-paths

# 3. Force push
git push --force
```

## Riesgos y Mitigaciones

### ⚠️ Riesgo: Push accidental de binarios grandes
**Mitigación**: Checklist de verificación pre-commit

### ⚠️ Riesgo: Reescritura de historia afecta a colaboradores
**Mitigación**: 
- Comunicar antes de hacer force push
- Todos deben re-clonar después de la limpieza
- Trabajar en rama separada primero

### ⚠️ Riesgo: Pérdida de datos locales
**Mitigación**: 
- Hacer backup antes de operaciones destructivas
- Usar `git stash` para cambios no comiteados
- Verificar con `git status` antes de reset/checkout

## Comandos Útiles de Diagnóstico

```bash
# Ver archivos más grandes en el repositorio
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | sed -n 's/^blob //p' \
  | sort --numeric-sort --key=2 \
  | tail -20

# Ver tamaño total del repositorio
git count-objects -vH

# Listar todos los archivos trackeados
git ls-files

# Ver historial de un archivo específico
git log --follow -- ruta/al/archivo
```

## Contacto y Ayuda

Si encuentras problemas durante la recuperación:
1. **NO** hacer push --force sin consultar
2. Crear un issue describiendo el problema
3. Incluir output de `git status` y `git log --oneline -10`
