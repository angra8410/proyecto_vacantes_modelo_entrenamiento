# ✅ RESUMEN FINAL: Workflow Automático con Dual Folder

## 🎯 Lo que se implementó

### Funcionalidad Principal
**Generación automática de archivos YAML en DOS carpetas** cuando se sube `vacantes.txt`:

1. **`vacantes_yaml/`** - Copia original (respaldo automático)
   - Se genera automáticamente
   - NO editar manualmente
   - Sirve como referencia/respaldo
   - Se sobrescribe cada vez que se procesa vacantes.txt

2. **`vacantes_yaml_manual/`** - Copia editable  
   - Se genera automáticamente (idéntica a la original)
   - PUEDES editar manualmente
   - Esta versión se copia a `aplicaciones_laborales`
   - Los cambios manuales se mantienen hasta la próxima regeneración

---

## 🔄 Flujo Completo

```
1. Subes vacantes.txt al repositorio
         ↓
2. GitHub Actions detecta el cambio
         ↓
3. Workflow genera YAMLs en AMBAS carpetas:
   - vacantes_yaml/ (original)
   - vacantes_yaml_manual/ (editable)
         ↓
4. Commit automático de ambas carpetas
         ↓
5. Puedes editar archivos en vacantes_yaml_manual/
         ↓
6. Los YAMLs de vacantes_yaml_manual/ se copian a aplicaciones_laborales
         ↓
7. ✅ Listo para procesar
```

---

## 💡 Casos de Uso

### Caso 1: Vacante perfecta (sin editar)
```bash
# 1. Subes vacantes.txt
git add vacantes.txt
git commit -m "Nueva vacante"
git push

# 2. Sistema genera en ambas carpetas automáticamente
# 3. No necesitas editar nada
# 4. El YAML se copia a aplicaciones_laborales
# ✅ Listo!
```

### Caso 2: Necesitas ajustar la vacante
```bash
# 1. Sistema genera YAMLs automáticamente en ambas carpetas

# 2. Editas el archivo en vacantes_yaml_manual/
vim vacantes_yaml_manual/2025-10-29_Senior_Developer_TechCorp.yaml

# 3. Haces los ajustes que necesites:
#    - Corregir descripción
#    - Agregar ubicación
#    - Ajustar requerimientos
#    - etc.

# 4. Commit de tus cambios
git add vacantes_yaml_manual/2025-10-29_Senior_Developer_TechCorp.yaml
git commit -m "Ajustar descripción de vacante Senior Developer"
git push

# 5. El archivo editado se copia a aplicaciones_laborales
# ✅ Listo con tus ajustes!

# BONUS: Si la editaste mal, puedes recuperar el original:
cp vacantes_yaml/2025-10-29_Senior_Developer_TechCorp.yaml \
   vacantes_yaml_manual/2025-10-29_Senior_Developer_TechCorp.yaml
```

### Caso 3: Comparar original vs editado
```bash
# Ver las diferencias entre original y editado
diff vacantes_yaml/mi_vacante.yaml \
     vacantes_yaml_manual/mi_vacante.yaml

# O usar un diff visual
git diff --no-index \
  vacantes_yaml/mi_vacante.yaml \
  vacantes_yaml_manual/mi_vacante.yaml
```

### Caso 4: Regenerar todo desde vacantes.txt
```bash
# 1. Editas vacantes.txt con las vacantes actualizadas
vim vacantes.txt

# 2. Commit y push
git add vacantes.txt
git commit -m "Actualizar vacantes"
git push

# 3. ⚠️ AMBAS carpetas se regeneran
#    - vacantes_yaml/ se actualiza
#    - vacantes_yaml_manual/ se actualiza
#    - Se pierden los cambios manuales en vacantes_yaml_manual/

# ✅ Usa esto cuando quieras resetear todo
```

---

## 📋 Archivo de Entrada (vacantes.txt)

```yaml
cargo: Backend Developer
empresa: TechCorp
fecha: 2025-10-29
descripcion: |
  Desarrollador backend para sistemas de alta disponibilidad.
  Trabajarás con Python, Django y PostgreSQL.
requerimientos: |
  - 3+ años de experiencia en Python
  - Django o Flask
  - PostgreSQL
  - Docker
ubicacion: Bogotá, Colombia (Remote)
tipo_contrato: Full-time
---
cargo: Frontend Developer
empresa: StartupXYZ
fecha: 2025-10-29
descripcion: |
  Desarrollador frontend con React y TypeScript.
requerimientos: |
  - React 18+
  - TypeScript
  - Next.js
---
```

---

## 🎓 Mejores Prácticas

### ✅ Hacer (DO)

1. **Editar solo en vacantes_yaml_manual/**
   ```bash
   vim vacantes_yaml_manual/mi_vacante.yaml
   ```

2. **Mantener vacantes_yaml/ como referencia**
   ```bash
   # Solo lectura - para comparar o recuperar
   cat vacantes_yaml/mi_vacante.yaml
   ```

3. **Hacer commit de tus ediciones**
   ```bash
   git add vacantes_yaml_manual/*.yaml
   git commit -m "Ajustar vacantes manualmente"
   git push
   ```

4. **Comparar antes de editar**
   ```bash
   diff vacantes_yaml/vacante.yaml vacantes_yaml_manual/vacante.yaml
   ```

### ❌ No Hacer (DON'T)

1. **No editar vacantes_yaml/**
   ```bash
   # ❌ MAL - Se perderán los cambios
   vim vacantes_yaml/mi_vacante.yaml
   ```

2. **No regenerar si tienes ediciones pendientes**
   ```bash
   # ❌ Si editaste manualmente vacantes_yaml_manual/
   # y luego actualizas vacantes.txt, perderás tus ediciones
   ```

3. **No confundir las carpetas**
   - `vacantes_yaml/` = Original (solo lectura)
   - `vacantes_yaml_manual/` = Editable

---

## 🔍 Verificación

### Verificar que ambas carpetas tienen el archivo
```bash
ls -la vacantes_yaml/2025-10-29_*.yaml
ls -la vacantes_yaml_manual/2025-10-29_*.yaml
```

### Verificar que son idénticos (después de generar)
```bash
diff vacantes_yaml/2025-10-29_Test.yaml \
     vacantes_yaml_manual/2025-10-29_Test.yaml
# No debería mostrar diferencias
```

### Ver el workflow en acción
1. Ve a GitHub → Actions
2. Busca "Process vacantes and generate YAML files"
3. Ver que genera en ambas carpetas

---

## 📊 Ejemplo Completo

### Paso 1: Crear vacante nueva

```bash
cat > vacantes.txt << 'EOF'
cargo: Data Scientist
empresa: AI Innovations
fecha: 2025-10-29
descripcion: |
  Científico de datos para proyectos de ML en producción.
  Trabajarás con modelos de clasificación y regresión.
requerimientos: |
  - Python (pandas, sklearn, tensorflow)
  - SQL avanzado
  - 3+ años de experiencia en ML
  - Inglés intermedio
ubicacion: Remote (LATAM)
tipo_contrato: Full-time
EOF
```

### Paso 2: Subir al repositorio

```bash
git add vacantes.txt
git commit -m "Agregar vacante: Data Scientist en AI Innovations"
git push
```

### Paso 3: Verificar generación automática

```bash
# Esperar ~1 minuto para que GitHub Actions complete

# Actualizar repo local
git pull

# Verificar archivos generados
ls -la vacantes_yaml/2025-10-29_Data_Scientist_AI_Innovations.yaml
ls -la vacantes_yaml_manual/2025-10-29_Data_Scientist_AI_Innovations.yaml

# ✅ Ambos archivos deben existir
```

### Paso 4: Ajustar manualmente (si es necesario)

```bash
# Editar solo en vacantes_yaml_manual/
vim vacantes_yaml_manual/2025-10-29_Data_Scientist_AI_Innovations.yaml

# Por ejemplo, agregar más detalles en la descripción:
descripcion: |
  Científico de datos para proyectos de ML en producción.
  Trabajarás con modelos de clasificación y regresión.
  
  Beneficios:
  - Trabajo 100% remoto
  - Horario flexible
  - Capacitación continua

# Guardar y commit
git add vacantes_yaml_manual/2025-10-29_Data_Scientist_AI_Innovations.yaml
git commit -m "Ajustar descripción con beneficios"
git push
```

### Paso 5: Verificar en aplicaciones_laborales

```bash
# Ir al repo aplicaciones_laborales
cd ../aplicaciones_laborales

# Pull para actualizar
git pull

# Verificar que el archivo editado llegó
cat to_process/2025-10-29_Data_Scientist_AI_Innovations.yaml

# ✅ Debería tener tus ediciones (beneficios)
```

---

## 🆘 Troubleshooting

### Problema: Solo se generó en una carpeta

**Solución:**
```bash
# Verificar el workflow
cat .github/workflows/process_vacantes.yml

# Debería tener dos llamadas a process_vacantes.py:
# - Una para vacantes_yaml/
# - Otra para vacantes_yaml_manual/
```

### Problema: Edité vacantes_yaml/ por error

**Solución:**
```bash
# Regenerar desde vacantes.txt
git add vacantes.txt
git commit -m "Regenerar YAMLs" --allow-empty
git push

# O restaurar manualmente
git checkout HEAD -- vacantes_yaml/
```

### Problema: Perdí mis ediciones en vacantes_yaml_manual/

**Solución:**
```bash
# Si hiciste commit antes:
git log --all --full-history -- vacantes_yaml_manual/mi_vacante.yaml

# Recuperar de un commit anterior
git checkout <commit-hash> -- vacantes_yaml_manual/mi_vacante.yaml

# Si no hiciste commit, se perdieron :(
# Lección: Siempre hacer commit de tus ediciones
```

---

## ✅ Checklist de Verificación

Antes de usar en producción:

- [ ] Ambas carpetas existen: `vacantes_yaml/` y `vacantes_yaml_manual/`
- [ ] Workflow genera archivos en ambas carpetas
- [ ] Los archivos son idénticos después de generar
- [ ] Puedo editar archivos en `vacantes_yaml_manual/`
- [ ] Los archivos editados se copian a `aplicaciones_laborales`
- [ ] `vacantes_yaml/` mantiene la versión original
- [ ] Entiendo cuándo usar cada carpeta

---

## 🎉 Resumen

**¿Qué tienes ahora?**
- ✅ Generación automática en DOS carpetas
- ✅ Respaldo automático en `vacantes_yaml/`
- ✅ Capacidad de editar en `vacantes_yaml_manual/`
- ✅ Comparación fácil entre original y editado
- ✅ Recuperación simple si editas mal
- ✅ Workflow 100% automatizado

**¿Qué debes recordar?**
- 📝 Editar solo en `vacantes_yaml_manual/`
- 🔒 No tocar `vacantes_yaml/` (es respaldo)
- 💾 Hacer commit de tus ediciones
- 🔄 Regenerar sobrescribe ambas carpetas

**¡Listo para usar!** 🚀

---

_Implementación completada: 2025-10-29_  
_Funcionalidad: Dual folder (original + editable)_  
_Estado: ✅ FUNCIONAL_
