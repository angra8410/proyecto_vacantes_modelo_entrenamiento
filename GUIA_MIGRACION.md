# Guía de Migración: Flujo Centralizado

## 🔄 Cambios Implementados

Este repositorio ha sido actualizado para centralizar todo el manejo de vacantes y hojas de vida en un solo lugar, eliminando la dependencia del repositorio externo `aplicaciones_laborales`.

## 📌 ¿Qué cambió?

### Antes (Flujo Antiguo)

```
proyecto_vacantes_modelo_entrenamiento:
  - vacantes_yaml_manual/  → Crear vacantes aquí
  
       ↓ (GitHub Actions)
  
aplicaciones_laborales:
  - to_process/  → Vacantes copiadas vía API
  - [Procesamiento externo]
```

**Problemas del flujo antiguo**:
- ❌ Dependencia de múltiples repositorios
- ❌ Necesidad de tokens/secrets para acceso cruzado
- ❌ Sincronización compleja
- ❌ Dificulta trazabilidad
- ❌ Mayor superficie de error

### Ahora (Flujo Centralizado)

```
proyecto_vacantes_modelo_entrenamiento:
  - vacantes_yaml_manual/  → Crear vacantes aquí
       ↓ (GitHub Actions automático)
  - to_process/  → Vacantes a procesar
       ↓ (Procesamiento automático)
  - aplicaciones/YYYY/MM/DD/  → CVs organizados por fecha
```

**Beneficios del flujo centralizado**:
- ✅ Todo en un solo repositorio
- ✅ Sin tokens/secrets externos
- ✅ Automatización simplificada
- ✅ Trazabilidad completa en Git
- ✅ Organización por fecha

## 🚀 Cómo Usar el Nuevo Flujo

### Opción 1: Automático (Recomendado)

1. Crear/editar vacante en `vacantes_yaml_manual/`:
   ```yaml
   cargo: "Data Analyst"
   empresa: "TechCorp"
   fecha: "2025-10-27"
   ...
   ```

2. Commit y push:
   ```bash
   git add vacantes_yaml_manual/mi_vacante.yaml
   git commit -m "Agregar nueva vacante"
   git push
   ```

3. **¡GitHub Actions hace todo automáticamente!**
   - Copia a `to_process/`
   - Procesa y genera CV
   - Organiza en `aplicaciones/2025/10/27/`

### Opción 2: Manual

```bash
# Copiar vacantes a procesar
python scripts/copy_to_process.py --all

# Procesar y organizar CVs
python scripts/process_and_organize_cv.py

# Verificar resultados
ls -R aplicaciones/
```

## 📂 Nueva Estructura de Carpetas

```
proyecto_vacantes_modelo_entrenamiento/
├── vacantes_yaml_manual/     # Crear/editar vacantes aquí
│   └── *.yaml
│
├── to_process/                # Procesamiento automático
│   ├── .gitkeep
│   └── processed/            # Vacantes ya procesadas
│
├── aplicaciones/              # CVs organizados por fecha
│   └── YYYY/
│       └── MM/
│           └── DD/
│               └── *.yaml
│
├── scripts/
│   ├── copy_to_process.py              # Script de copia
│   ├── process_and_organize_cv.py      # Script de procesamiento
│   └── github_push_yaml_to_other_repo.py  # [DEPRECATED]
│
└── .github/workflows/
    ├── process_vacancies.yml           # Workflow principal (NUEVO)
    └── copy_to_app_laborales.yml      # [DEPRECATED]
```

## 🔧 Scripts y Workflows

### Nuevos Scripts

1. **scripts/copy_to_process.py**
   - Copia vacantes de `vacantes_yaml_manual/` a `to_process/`
   - Detecta archivos modificados en git
   - Usado por GitHub Actions

2. **scripts/process_and_organize_cv.py**
   - Procesa vacantes de `to_process/`
   - Genera CVs/documentos
   - Organiza en `aplicaciones/` por fecha
   - Mueve procesados a `to_process/processed/`

### Nuevo Workflow

**.github/workflows/process_vacancies.yml**
- Trigger: cambios en `vacantes_yaml_manual/*.yaml`
- Ejecuta copia y procesamiento automático
- Hace commit de resultados

### Scripts Deprecados

1. **scripts/github_push_yaml_to_other_repo.py** → ⚠️  DEPRECATED
   - Ya no se usa
   - Reemplazado por `copy_to_process.py`

2. **.github/workflows/copy_to_app_laborales.yml** → ⚠️  DEPRECATED
   - Ya no se ejecuta
   - Reemplazado por `process_vacancies.yml`

## 📝 Migrando Datos Existentes

Si tienes datos en el repositorio `aplicaciones_laborales`, puedes migrarlos:

### Opción 1: Migración Manual

```bash
# 1. Clonar el repositorio antiguo
git clone https://github.com/angra8410/aplicaciones_laborales.git /tmp/aplicaciones_laborales

# 2. Copiar archivos al nuevo repo
cp -r /tmp/aplicaciones_laborales/aplicaciones/* aplicaciones/

# 3. Commit en el nuevo repo
git add aplicaciones/
git commit -m "Migrar datos de aplicaciones_laborales"
git push
```

### Opción 2: Reprocesar Desde Vacantes

Si tienes todas las vacantes en `vacantes_yaml_manual/`:

```bash
# Procesar todas las vacantes nuevamente
python scripts/copy_to_process.py --all
python scripts/process_and_organize_cv.py
```

## 🔍 Verificación Post-Migración

### 1. Verificar Estructura

```bash
# Debe mostrar la estructura de carpetas por fecha
tree aplicaciones/ -L 3
```

Salida esperada:
```
aplicaciones/
└── 2025/
    └── 10/
        ├── 25/
        ├── 26/
        └── 27/
```

### 2. Verificar CVs

```bash
# Contar CVs por mes
find aplicaciones/ -name "*.yaml" | cut -d'/' -f2,3 | sort | uniq -c

# Ver CVs de una fecha específica
ls aplicaciones/2025/10/27/
```

### 3. Probar Workflow

```bash
# 1. Crear vacante de prueba
cat > vacantes_yaml_manual/test_vacante.yaml << EOF
cargo: "Test Position"
empresa: "Test Company"
fecha: "2025-10-27"
descripcion: "Test description"
requerimientos:
  - Test requirement
EOF

# 2. Commit y push
git add vacantes_yaml_manual/test_vacante.yaml
git commit -m "Test: nueva vacante"
git push

# 3. Verificar en GitHub Actions que el workflow se ejecutó
# 4. Verificar que el CV se creó en aplicaciones/2025/10/27/
```

## 🆘 Solución de Problemas

### Problema: GitHub Actions no se ejecuta

**Solución**: Verificar que el workflow esté habilitado
```
GitHub → Actions → Workflows → Process Vacancies → Enable workflow
```

### Problema: CVs no se organizan correctamente

**Causa común**: Formato de fecha inválido en YAML

**Solución**: Verificar formato de fecha
```yaml
# ✅ Correcto
fecha: "2025-10-27"

# ❌ Incorrecto
fecha: "27/10/2025"
```

### Problema: Archivos no se copian a to_process

**Diagnóstico**:
```bash
# Ejecutar manualmente para ver errores
python scripts/copy_to_process.py --all
```

## 📚 Documentación Relacionada

- **README.md**: Guía rápida del repositorio
- **GUIA_FLUJO_CENTRALIZADO.md**: Guía completa del flujo centralizado
- **GUIA_EXTRACTOR_TEXTO_PLANO.md**: Extracción desde texto plano
- **EJEMPLO_VACANTE.yaml**: Ejemplo de vacante

## 🎯 Próximos Pasos

1. Revisar la nueva documentación
2. Migrar datos si es necesario
3. Probar el nuevo flujo con una vacante de prueba
4. Eliminar el repositorio `aplicaciones_laborales` (opcional)
5. Comenzar a usar el flujo centralizado

## 💡 Ventajas del Nuevo Flujo

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| Repositorios | 2 (modelo + aplicaciones) | 1 (todo integrado) |
| Tokens/Secrets | Requerido (LABORALES_TOKEN) | No requerido |
| Trazabilidad | Dividida entre repos | Completa en un repo |
| Organización | Manual/variable | Automática por fecha |
| Complejidad | Alta | Baja |
| Mantenimiento | 2 repos a mantener | 1 repo a mantener |

## ✅ Checklist de Migración

- [ ] Leer documentación del nuevo flujo
- [ ] Verificar estructura de carpetas
- [ ] Migrar datos existentes (si aplica)
- [ ] Probar workflow con vacante de prueba
- [ ] Verificar que CVs se organizan por fecha
- [ ] Actualizar scripts personales (si existen)
- [ ] Marcar repositorio antiguo como deprecated
- [ ] Comenzar a usar flujo centralizado

## 🎉 ¡Listo!

El nuevo flujo centralizado está operativo y listo para usar. Cualquier cambio en `vacantes_yaml_manual/` activará automáticamente todo el procesamiento.

**¿Preguntas?** Consulta:
- GUIA_FLUJO_CENTRALIZADO.md
- README.md
- Issues en GitHub
