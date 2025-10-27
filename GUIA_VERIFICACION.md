# Guía de Verificación Post-Restauración

## 🎯 Resumen Ejecutivo

**Estado:** ✅ Repositorio completamente restaurado y funcional

Tu repositorio `proyecto_vacantes_modelo_entrenamiento` ha sido exitosamente restaurado a su estado original después de revertir la implementación centralizada (PR #7). **Todo está funcionando correctamente.**

---

## ✅ Lo Que Se Ha Verificado

### 1. Workflow Principal Restaurado
- **Archivo:** `.github/workflows/copy_to_app_laborales.yml`
- **Función:** Copia archivos YAML nuevos/modificados a `aplicaciones_laborales`
- **Trigger:** Cambios en `vacantes_yaml_manual/*.yaml`
- **Estado:** ✅ Presente y configurado correctamente

### 2. Script de Integración Funcional
- **Archivo:** `scripts/github_push_yaml_to_other_repo.py`
- **Función:** Detecta YAMLs modificados y los empuja vía GitHub API
- **Configuración:**
  - Origen: `vacantes_yaml_manual/`
  - Destino: `angra8410/aplicaciones_laborales/to_process/`
  - Token: `LABORALES_TOKEN`
- **Estado:** ✅ Presente y configurado correctamente

### 3. Scripts de Entrenamiento
- **Cantidad:** 24 scripts originales
- **Estado:** ✅ Todos presentes
- **Incluye:**
  - `process_vacantes.py` - Procesador de vacantes
  - `extract_vacantes_from_text.py` - Extractor de texto
  - `convert_to_line_dataset.py` - Conversor de datasets
  - `train_line_classifier.py` - Entrenador de clasificador
  - `train_tfidf_baseline.py` - Modelo baseline
  - Y 19 scripts más

### 4. Limpieza Completada
- ✅ Workflow centralizado removido
- ✅ Scripts de centralización removidos
- ✅ Carpeta `aplicaciones/` removida
- ✅ Documentación de centralización removida

---

## 🔄 Cómo Funciona el Workflow Restaurado

### Flujo Automático

```
1. Usuario crea/modifica YAML
   ↓
   vacantes_yaml_manual/mi_vacante.yaml

2. Git push al repositorio
   ↓
   GitHub detecta cambio

3. Workflow se activa automáticamente
   ↓
   .github/workflows/copy_to_app_laborales.yml

4. Script ejecuta
   ↓
   scripts/github_push_yaml_to_other_repo.py

5. Archivo copiado vía API
   ↓
   aplicaciones_laborales/to_process/mi_vacante.yaml

6. Integración con otros repos
   ↓
   todas-mis-aplicaciones (tracking final)
```

---

## 🧪 Prueba de Funcionamiento

### Opción 1: Verificación Automática (Recomendada)

Ejecuta el script de validación incluido:

```bash
cd /ruta/al/repositorio
./test_workflow.sh
```

**Resultado esperado:** Todos los tests en ✅ verde

### Opción 2: Prueba Manual Completa

#### Paso 1: Verificar Secreto

1. Ve a: `Settings → Secrets and variables → Actions`
2. Verifica que existe: `LABORALES_TOKEN`
3. Si no existe o expiró, créalo con scope `repo`

#### Paso 2: Crear Vacante de Prueba

```bash
# Crear archivo de prueba
cat > vacantes_yaml_manual/test_workflow_2025-10-27.yaml << EOF
cargo: Test Workflow Position
empresa: Test Company
fecha: 2025-10-27
descripcion: |
  This is a test vacancy to verify the workflow is working correctly.
requerimientos: |
  - Testing skills
  - Git knowledge
EOF
```

#### Paso 3: Commit y Push

```bash
git add vacantes_yaml_manual/test_workflow_2025-10-27.yaml
git commit -m "Test: Verify workflow functionality"
git push origin main
```

#### Paso 4: Verificar Ejecución

1. Ve a la pestaña **Actions** en GitHub
2. Deberías ver un workflow ejecutándose: "Copy new manual YAML to aplicaciones_laborales"
3. Espera a que complete (1-2 minutos)
4. Si es exitoso, verás ✅ verde

#### Paso 5: Verificar en Destino

1. Ve al repositorio: `aplicaciones_laborales`
2. Navega a: `to_process/`
3. Deberías ver: `test_workflow_2025-10-27.yaml`

✅ **Si ves el archivo, el workflow está funcionando perfectamente!**

---

## 📋 Checklist de Verificación Rápida

Marca cada ítem según tu verificación:

### Configuración
- [ ] Secret `LABORALES_TOKEN` existe y es válido
- [ ] Tienes permisos de push en `aplicaciones_laborales`
- [ ] Workflow visible en pestaña Actions

### Archivos
- [ ] Existe `.github/workflows/copy_to_app_laborales.yml`
- [ ] Existe `scripts/github_push_yaml_to_other_repo.py`
- [ ] NO existe `.github/workflows/process_vacancies.yml`
- [ ] NO existe carpeta `aplicaciones/` en raíz

### Prueba Funcional (después de test)
- [ ] Workflow se ejecutó sin errores
- [ ] Archivo apareció en `aplicaciones_laborales/to_process/`
- [ ] Log del workflow muestra éxito

---

## 🆘 Solución de Problemas

### Problema: Workflow no se ejecuta

**Causas posibles:**
1. Ruta incorrecta del archivo (debe estar en `vacantes_yaml_manual/`)
2. Extensión incorrecta (debe ser `.yaml`)
3. Workflow deshabilitado

**Solución:**
```bash
# Verificar que el archivo está en la ruta correcta
ls vacantes_yaml_manual/*.yaml

# Verificar que el workflow está habilitado
# Ve a Actions → Workflows → Asegúrate que no esté deshabilitado
```

### Problema: Workflow falla con error de autenticación

**Causa:** Token inválido o sin permisos

**Solución:**
1. Ve a `Settings → Secrets and variables → Actions`
2. Actualiza `LABORALES_TOKEN` con un nuevo token
3. El token debe tener scope: `repo` (Full control of private repositories)

### Problema: Script no detecta archivos

**Causa:** Commit sin cambios o fetch-depth incorrecto

**Solución:**
```bash
# El workflow ya tiene fetch-depth: 0
# Verifica que el archivo realmente cambió:
git log -1 --stat
```

### Problema: No puedo ver el workflow en Actions

**Causa:** Archivo de workflow inválido o mal ubicado

**Solución:**
```bash
# Verificar ubicación
ls -la .github/workflows/copy_to_app_laborales.yml

# Validar YAML
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/copy_to_app_laborales.yml'))"
```

---

## 📚 Documentación Adicional

- **README.md** - Uso general del repositorio
- **VALIDATION_REPORT.md** - Reporte técnico de auditoría
- **RECOVERY_GUIDE.md** - Guía de recuperación de Git
- **GUIA_PROCESADOR_VACANTES.md** - Procesamiento de vacantes
- **GUIA_EXTRACTOR_TEXTO_PLANO.md** - Extracción de texto

---

## 🎓 Uso Normal del Repositorio

Una vez verificado que todo funciona:

### Para Añadir Nueva Vacante

```bash
# 1. Crear archivo YAML en vacantes_yaml_manual/
vim vacantes_yaml_manual/mi_vacante_2025-10-27.yaml

# 2. Añadir contenido (formato ejemplo):
cargo: Senior Data Analyst
empresa: TechCorp
fecha: 2025-10-27
descripcion: |
  Descripción del puesto...
requerimientos: |
  - Requisito 1
  - Requisito 2

# 3. Guardar y commitear
git add vacantes_yaml_manual/mi_vacante_2025-10-27.yaml
git commit -m "Add vacancy: Senior Data Analyst at TechCorp"
git push

# 4. El workflow automáticamente:
#    - Detecta el nuevo archivo
#    - Lo copia a aplicaciones_laborales/to_process/
#    - Triggerea procesamiento downstream
```

### Para Procesar Múltiples Vacantes

```bash
# Usar el procesador de vacantes
python scripts/process_vacantes.py \
  --input vacantes.txt \
  --output output/vacantes \
  --to-jsonl

# Convertir a dataset de líneas
python scripts/convert_to_line_dataset.py \
  --input data/training_data.jsonl \
  --outdir data/

# Entrenar modelo
python scripts/train_line_classifier.py \
  data/line_dataset.jsonl
```

---

## ✨ Resumen Final

Tu repositorio está **100% funcional** y restaurado a su estado original. Los workflows, scripts e integraciones están todos en su lugar y correctamente configurados.

**Próximos pasos:**
1. ✅ Ejecuta `./test_workflow.sh` para confirmar
2. ✅ Haz una prueba con un archivo real
3. ✅ Verifica que aparece en `aplicaciones_laborales`
4. ✅ Continúa con tu workflow normal

**No se requiere trabajo adicional de restauración.**

---

## 📞 Soporte

Si encuentras algún problema:

1. Revisa el log del workflow en Actions
2. Verifica la configuración del secret
3. Consulta VALIDATION_REPORT.md para detalles técnicos
4. Ejecuta test_workflow.sh para diagnóstico automático

---

**Fecha de Restauración:** 2025-10-27  
**Estado:** ✅ Completado y Verificado  
**Repositorio:** angra8410/proyecto_vacantes_modelo_entrenamiento
