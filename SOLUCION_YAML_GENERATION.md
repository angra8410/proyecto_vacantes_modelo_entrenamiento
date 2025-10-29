# Guía de Solución - Generación Automática de YAML

## Problema Identificado

El flujo automatizado NO generaba archivos YAML al subir `vacantes.txt` porque:

1. **Causa raíz**: El workflow usaba `process_vacantes.py` que espera archivos en formato YAML estructurado
2. **Realidad**: El archivo `vacantes.txt` contiene texto plano (formato LinkedIn, texto desestructurado)
3. **Script correcto existe**: `extract_vacantes_from_text.py` ya existe y maneja texto plano, pero NO estaba siendo llamado por el workflow

## Solución Implementada

### 1. Workflow Inteligente
El workflow ahora detecta automáticamente el formato del archivo:

```bash
# Detecta si es YAML o texto plano
is_yaml_format() {
  if grep -q "^---$" "$1" && grep -q "^cargo:" "$1" && grep -q "^empresa:" "$1"; then
    return 0  # Es YAML
  else
    return 1  # Es texto plano
  fi
}
```

### 2. Procesamiento Adaptativo
- **Texto plano** → usa `extract_vacantes_from_text.py`
- **YAML estructurado** → usa `process_vacantes.py`

### 3. Generación en Dos Carpetas
Ambos scripts generan YAML en:
- `vacantes_yaml/` - Copia original (respaldo)
- `vacantes_yaml_manual/` - Copia editable

## Cómo Usar

### Para Texto Plano (LinkedIn, texto desestructurado)
Simplemente copia y pega el texto de la vacante en `vacantes.txt`:

```text
Digital Analytics Engineer
Insight Global
Colombia · Remote

Required Skills & Experience:
- 3 years of experience...
- Expertise creating JSON files...

Job Description:
Our client is looking for...
```

**Resultado**: Se generarán automáticamente archivos YAML estructurados.

### Para YAML Estructurado
Si prefieres subir YAML ya estructurado, usa el formato:

```yaml
cargo: Digital Analytics Engineer
empresa: Insight Global
fecha: 2025-10-29
descripcion: |
  Our client is looking for...
requerimientos: |
  - 3 years of experience
  - Expertise creating JSON files
---
cargo: Otra Vacante
empresa: Otra Empresa
...
```

## Validación Automática

Se ha creado un script de pruebas automáticas: `tests/test_yaml_generation.sh`

```bash
# Ejecutar todas las pruebas
./tests/test_yaml_generation.sh
```

**Las pruebas validan**:
- ✅ Workflow YAML es válido
- ✅ Scripts Python tienen sintaxis correcta
- ✅ Directorios requeridos existen
- ✅ Detección de formato funciona
- ✅ Procesamiento YAML funciona
- ✅ Procesamiento texto plano funciona
- ✅ Lógica completa del workflow
- ✅ Integración end-to-end

## Flujo Completo

```
Usuario sube vacantes.txt
         ↓
GitHub Actions detecta cambio
         ↓
Workflow identifica formato
         ↓
    ┌────────┴────────┐
    ↓                 ↓
Texto plano      YAML formato
    ↓                 ↓
extract_...     process_...
    ↓                 ↓
    └────────┬────────┘
             ↓
   Genera YAML en ambas carpetas
   - vacantes_yaml/
   - vacantes_yaml_manual/
             ↓
   Commit y push automático
             ↓
   YAMLs disponibles
```

## Archivos Modificados

1. `.github/workflows/process_vacantes.yml` - Workflow actualizado con detección de formato
2. `tests/test_yaml_generation.sh` - Suite de pruebas automáticas (NUEVO)
3. `SOLUCION_YAML_GENERATION.md` - Esta guía (NUEVO)
4. `README.md` - Actualizado con nueva información

## Verificación

Para verificar que todo funciona:

1. Ejecuta las pruebas:
   ```bash
   ./tests/test_yaml_generation.sh
   ```

2. Modifica `vacantes.txt` y haz push:
   ```bash
   git add vacantes.txt
   git commit -m "Add new vacancy"
   git push
   ```

3. Verifica que GitHub Actions genera los YAMLs automáticamente

## Beneficios

✅ **Automático**: Solo sube el archivo, todo lo demás es automático  
✅ **Inteligente**: Detecta el formato automáticamente  
✅ **Robusto**: Funciona con cualquier formato de entrada  
✅ **Validado**: Suite de pruebas garantiza funcionamiento  
✅ **Trazable**: Commits automáticos con historial completo  
✅ **Confiable**: Respaldo en dos carpetas (original + editable)

## Soporte para Múltiples Formatos

El extractor de texto plano (`extract_vacantes_from_text.py`) soporta:
- Texto libre de LinkedIn
- Copias de ofertas de trabajo de sitios web
- Emails con ofertas
- PDFs convertidos a texto
- Cualquier texto desestructurado con información de vacantes

**Campos que extrae automáticamente**:
- Cargo
- Empresa
- Fecha
- Descripción
- Requerimientos
- Modalidad (remoto/híbrido/presencial)

## Troubleshooting

### No se generan YAMLs
1. Verifica que el archivo tenga contenido
2. Ejecuta las pruebas: `./tests/test_yaml_generation.sh`
3. Revisa los logs de GitHub Actions

### YAMLs con datos incorrectos
- El extractor hace su mejor esfuerzo con texto desestructurado
- Para mayor precisión, usa formato YAML estructurado
- Los YAMLs generados en `vacantes_yaml_manual/` son editables

### Workflow no se dispara
- Verifica que el cambio sea en `vacantes.txt` o `vacantes_sample.txt`
- Revisa la configuración del workflow en `.github/workflows/process_vacantes.yml`
