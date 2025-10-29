# Guía del Workflow Automático de Procesamiento de Vacantes

## 📋 Descripción General

Este repositorio cuenta con un **flujo de trabajo completamente automatizado** que procesa vacantes y las distribuye automáticamente sin necesidad de intervención manual.

## 🔄 Flujo Completo Automatizado

```
┌─────────────────────────────────────────────────────────────────┐
│  1. Usuario sube/actualiza vacantes.txt                        │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. GitHub Actions detecta el cambio automáticamente            │
│     Workflow: process_vacantes.yml                              │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Se ejecuta process_vacantes.py                              │
│     - Valida campos requeridos                                  │
│     - Genera archivos YAML individuales                         │
│     - Guarda en vacantes_yaml_manual/                           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. GitHub Actions hace commit y push automático                │
│     - Commit: "Auto-generated YAML files from vacantes.txt"     │
│     - Push a la rama actual                                     │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. Se activa copy_to_app_laborales.yml                         │
│     (detecta cambios en vacantes_yaml_manual/)                  │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. Los YAML se copian a aplicaciones_laborales/to_process/     │
│     (usando LABORALES_TOKEN)                                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  7. ¡Vacantes listas para procesamiento posterior!              │
└─────────────────────────────────────────────────────────────────┘
```

## 📝 Formato del Archivo de Entrada

### Archivo: `vacantes.txt` o `vacantes_sample.txt`

El archivo debe contener vacantes en formato YAML separadas por `---`:

```yaml
cargo: Senior Developer
empresa: Tech Corp
fecha: 2025-01-15
descripcion: |
  Descripción detallada del puesto.
  Puede incluir múltiples líneas.
  Responsabilidades, contexto, etc.
requerimientos: |
  - Requisito 1
  - Requisito 2
  - Requisito 3
ubicacion: Bogotá, Colombia (Remote)
tipo_contrato: Full-time
---
cargo: Data Analyst
empresa: Analytics Inc
fecha: 2025-01-20
descripcion: |
  Otra descripción detallada...
requerimientos: |
  - SQL avanzado
  - Python/Pandas
  - Visualización con Power BI
ubicacion: México (Hybrid)
tipo_contrato: Full-time
---
```

### Campos Requeridos

| Campo | Descripción | Obligatorio |
|-------|-------------|-------------|
| `cargo` | Título del puesto | ✅ Sí |
| `empresa` | Nombre de la empresa | ✅ Sí |
| `fecha` | Fecha en formato YYYY-MM-DD | ✅ Sí |
| `descripcion` | Descripción del puesto (usar `|` para multilínea) | ✅ Sí |
| `requerimientos` | Lista de requisitos (usar `|` para multilínea) | ✅ Sí |
| `ubicacion` | Ubicación del trabajo | ❌ Opcional |
| `tipo_contrato` | Tipo de contrato (Full-time, Contract, etc.) | ❌ Opcional |

## 🚀 Cómo Usar el Sistema

### Opción 1: Subir Archivo Completo

1. **Edita `vacantes.txt`** con tus nuevas vacantes:
   ```bash
   vim vacantes.txt
   # O usa tu editor preferido
   ```

2. **Haz commit y push**:
   ```bash
   git add vacantes.txt
   git commit -m "Agregar nuevas vacantes: [descripción]"
   git push
   ```

3. **¡Eso es todo!** El sistema hace el resto automáticamente:
   - ✅ Genera YAMLs individuales
   - ✅ Los guarda en `vacantes_yaml_manual/`
   - ✅ Los copia a `aplicaciones_laborales`

### Opción 2: GitHub Web Interface

1. Ve al repositorio en GitHub
2. Navega a `vacantes.txt`
3. Haz clic en el icono de editar (lápiz)
4. Agrega/modifica las vacantes
5. Haz clic en "Commit changes"
6. ✅ El workflow se ejecuta automáticamente

## 📊 Monitorear la Ejecución

### Ver el Workflow en Acción

1. Ve a la pestaña **Actions** en GitHub
2. Verás dos workflows ejecutándose:
   - `Process vacantes and generate YAML files`
   - `Copy new manual YAML to aplicaciones_laborales`

3. Haz clic en cada uno para ver los logs detallados

### Estados Posibles

| Estado | Significado |
|--------|-------------|
| 🟢 Success | Todo funcionó correctamente |
| 🟡 In Progress | Workflow ejecutándose |
| 🔴 Failed | Hubo un error (ver logs) |

## 🔍 Validación de Resultados

### 1. Verificar YAMLs Generados

```bash
# Ver archivos generados en vacantes_yaml_manual/
ls -la vacantes_yaml_manual/

# Ver el último archivo generado
ls -lt vacantes_yaml_manual/ | head -5

# Ver contenido de un archivo específico
cat vacantes_yaml_manual/2025-01-15_Senior_Developer_Tech_Corp.yaml
```

### 2. Verificar en aplicaciones_laborales

1. Ve al repositorio `aplicaciones_laborales`
2. Navega a `to_process/`
3. Deberías ver tus archivos YAML copiados ahí

## ❗ Solución de Problemas

### Problema: Workflow no se ejecuta

**Causas posibles:**
- El archivo no se llama `vacantes.txt` o `vacantes_sample.txt`
- No hubo cambios en esos archivos
- Workflow está deshabilitado

**Solución:**
```bash
# Verifica que el archivo existe
ls -la vacantes.txt

# Verifica que hay cambios
git status

# Verifica en GitHub Actions que el workflow esté habilitado
```

### Problema: Error en el procesamiento

**Causas posibles:**
- Formato YAML inválido
- Campos requeridos faltantes
- Sintaxis incorrecta

**Solución:**
1. Revisa los logs en GitHub Actions
2. Verifica el formato YAML:
   ```bash
   # Validar YAML con múltiples documentos localmente
   python -c "import yaml; list(yaml.safe_load_all(open('vacantes.txt')))"
   ```
3. Asegúrate que todos los campos requeridos estén presentes

### Problema: YAMLs no se generan

**Causas posibles:**
- Error de sintaxis en el YAML
- Campos vacíos
- Fecha en formato incorrecto

**Solución:**
```bash
# Prueba localmente
python scripts/process_vacantes.py --input vacantes.txt --output /tmp/test

# Revisa los errores reportados
```

### Problema: YAMLs no se copian a aplicaciones_laborales

**Causas posibles:**
- Token `LABORALES_TOKEN` inválido o expirado
- Permisos insuficientes
- Repositorio destino no accesible

**Solución:**
1. Ve a Settings → Secrets → Actions
2. Verifica que `LABORALES_TOKEN` existe
3. Si no existe o expiró:
   - Genera un nuevo Personal Access Token en GitHub
   - Asegúrate que tenga scope "repo"
   - Actualiza el secret `LABORALES_TOKEN`

## 📈 Ejemplos Prácticos

### Ejemplo 1: Agregar Una Vacante

```bash
# Editar el archivo
cat >> vacantes.txt << 'EOF'
---
cargo: Full Stack Developer
empresa: StartupXYZ
fecha: 2025-10-29
descripcion: |
  Desarrollador full stack con experiencia en React y Node.js
  para proyecto de e-commerce.
requerimientos: |
  - 3+ años de experiencia
  - React, Node.js, MongoDB
  - Inglés intermedio
ubicacion: Colombia (Remote)
tipo_contrato: Full-time
EOF

# Commit y push
git add vacantes.txt
git commit -m "Agregar vacante: Full Stack Developer en StartupXYZ"
git push
```

**Resultado esperado:**
- ✅ Se genera: `vacantes_yaml_manual/2025-10-29_Full_Stack_Developer_StartupXYZ.yaml`
- ✅ Se copia a: `aplicaciones_laborales/to_process/2025-10-29_Full_Stack_Developer_StartupXYZ.yaml`

### Ejemplo 2: Agregar Múltiples Vacantes

```bash
cat > vacantes.txt << 'EOF'
cargo: Backend Developer
empresa: TechCorp
fecha: 2025-10-29
descripcion: |
  Backend developer para sistemas de alta disponibilidad.
requerimientos: |
  - Python/Django o Node.js
  - PostgreSQL
  - Docker/Kubernetes
---
cargo: DevOps Engineer
empresa: CloudSolutions
fecha: 2025-10-29
descripcion: |
  DevOps engineer para infraestructura cloud.
requerimientos: |
  - AWS o Azure
  - Terraform
  - CI/CD pipelines
---
cargo: Data Scientist
empresa: AI Innovations
fecha: 2025-10-29
descripcion: |
  Científico de datos para proyectos de ML.
requerimientos: |
  - Python (pandas, sklearn, tensorflow)
  - SQL
  - Experiencia con modelos de ML
EOF

git add vacantes.txt
git commit -m "Agregar 3 vacantes nuevas"
git push
```

**Resultado esperado:**
- ✅ 3 archivos YAML generados en `vacantes_yaml_manual/`
- ✅ 3 archivos copiados a `aplicaciones_laborales/to_process/`

## 🔐 Seguridad

### Tokens y Secretos

- `GITHUB_TOKEN`: Proporcionado automáticamente por GitHub Actions (lectura/escritura en el repo actual)
- `LABORALES_TOKEN`: Debe ser configurado manualmente en Settings → Secrets (acceso al repo `aplicaciones_laborales`)

### Permisos Necesarios

El token `LABORALES_TOKEN` necesita:
- ✅ `repo` (Full control of private repositories)
- ✅ Acceso al repositorio `aplicaciones_laborales`

## 📚 Documentación Relacionada

- `GUIA_PROCESADOR_VACANTES.md` - Guía del script process_vacantes.py
- `GUIA_EXTRACTOR_TEXTO_PLANO.md` - Guía del extractor de texto plano
- `GUIA_VERIFICACION.md` - Guía de verificación del repositorio
- `README.md` - Documentación principal del proyecto

## 🆘 Soporte

Si tienes problemas:

1. **Revisa los logs** en GitHub Actions
2. **Prueba localmente** con:
   ```bash
   python scripts/process_vacantes.py --input vacantes.txt --output /tmp/test
   ```
3. **Verifica el formato** de tu archivo YAML
4. **Consulta esta guía** para troubleshooting

## ✅ Checklist de Verificación

Antes de subir vacantes, verifica:

- [ ] Archivo se llama `vacantes.txt` o `vacantes_sample.txt`
- [ ] Formato YAML es válido (puedes validar online o localmente)
- [ ] Todos los campos requeridos están presentes
- [ ] Fecha en formato YYYY-MM-DD
- [ ] Bloques separados por `---`
- [ ] Descripción y requerimientos usan `|` para multilínea

## 🎉 ¡Listo!

Con este sistema, ya no necesitas:
- ❌ Ejecutar scripts manualmente
- ❌ Generar archivos YAML individuales
- ❌ Copiar archivos entre repositorios
- ❌ Preocuparte por la sincronización

¡Todo es automático! Solo sube `vacantes.txt` y el sistema hace el resto. 🚀
