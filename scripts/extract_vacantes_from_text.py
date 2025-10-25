#!/usr/bin/env python3
"""
scripts/extract_vacantes_from_text.py

Módulo para procesar vacantes en texto plano/desestructurado y extraer automáticamente
los campos clave (cargo, empresa, fecha, descripcion, requerimientos, modalidad).

Genera archivos YAML estructurados con nomenclatura normalizada: cargo_empresa_fecha.yaml

Uso:
  python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted
  python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --run-dataset-conversion
  python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --generate-report
"""

import argparse
import json
import re
import yaml
import unicodedata
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class VacancyExtractor:
    """Extractor de campos de vacantes desde texto desestructurado."""
    
    # Patrones para detectar campos clave
    # Nota: Se usa $ para coincidir con fin de línea (no \Z) ya que procesamos texto multilínea
    PATTERNS = {
        'cargo': [
            r'(?:cargo|puesto|posición|position|rol|role|título|title):\s*(.+?)(?:\n|$)',
            r'^([^\n]+?(?:developer|analyst|engineer|specialist|manager|coordinator|consultor|desarrollador|analista|ingeniero)[^\n]*?)(?:\s*[-–—]\s*|\n)',
            r'(?:buscamos|seeking|looking for|hiring|contratamos)\s+(?:un|una|a|an)?\s*([^\n]+?)(?:\s+para|\s+en|\s+at|$)',
        ],
        'empresa': [
            r'(?:empresa|company|organization|organización|cliente):\s*(.+?)(?:\n|$)',
            r'(?:en|at|para|for)\s+([A-Z][A-Za-z0-9\s&\.]{2,40}(?:Inc\.?|Corp\.?|Ltd\.?|S\.?A\.?|SAS|Group|Solutions|Services|Technologies|Global))',
            r'([A-Z][A-Za-z0-9\s&\.]{2,40}(?:Inc\.?|Corp\.?|Ltd\.?|S\.?A\.?|SAS|Group|Solutions|Services|Technologies|Global))\s+(?:está|is|busca|looking)',
        ],
        'fecha': [
            r'(?:fecha|date|publicado|published|start date):\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(?:fecha|date|publicado|published|start date):\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',
        ],
        'modalidad': [
            r'(?:modalidad|work mode|modo de trabajo):\s*([^\n]+)',
            r'\b((?:remoto|remote|híbrido|hybrid|presencial|on-?site)[^\n]*)\b',
        ],
        'requerimientos': [
            r'(?:requerimientos|requirements|requisitos|qualifications|skills|must have):\s*(.+?)(?=\n\n|$)',
        ],
        'descripcion': [
            r'(?:descripción|description|sobre el puesto|about the (?:role|position)|job description|what you\'ll do):\s*(.+?)(?=\n\n|$)',
        ],
    }
    
    def __init__(self, verbose: bool = True):
        """
        Inicializa el extractor.
        
        Args:
            verbose: Si debe imprimir información detallada
        """
        self.verbose = verbose
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'fields_extracted': {},
            'fields_missing': {},
        }
    
    def normalize_for_filename(self, text: str, max_length: int = 50) -> str:
        """
        Normaliza texto para usar en nombres de archivo.
        Aplica: minúsculas, sin tildes, sin espacios, sin caracteres especiales.
        
        Args:
            text: Texto a normalizar
            max_length: Longitud máxima
            
        Returns:
            Texto normalizado
        """
        if not text:
            return "sin_dato"
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover acentos/tildes
        text = unicodedata.normalize('NFKD', text)
        text = ''.join([c for c in text if not unicodedata.combining(c)])
        
        # Mantener solo letras, números y espacios
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        # Reemplazar espacios por guiones bajos
        text = re.sub(r'\s+', '_', text.strip())
        
        # Truncar si es muy largo
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip('_') or "sin_dato"
    
    def extract_field(self, text: str, field_name: str) -> Optional[str]:
        """
        Extrae un campo específico del texto usando patrones regex.
        
        Args:
            text: Texto completo de la vacante
            field_name: Nombre del campo a extraer
            
        Returns:
            Valor extraído o None
        """
        patterns = self.PATTERNS.get(field_name, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                if value:
                    # Limpiar el valor extraído
                    value = re.sub(r'\s+', ' ', value)
                    if len(value) > 5 or field_name in ['fecha', 'modalidad']:
                        return value
        
        return None
    
    def extract_description(self, text: str, found_fields: Dict) -> str:
        """
        Extrae la descripción del puesto. Si no se encuentra con patrones,
        usa el texto completo excluyendo otros campos ya extraídos.
        
        Args:
            text: Texto completo
            found_fields: Campos ya extraídos
            
        Returns:
            Descripción extraída
        """
        # Intentar con patrones primero
        desc = self.extract_field(text, 'descripcion')
        if desc and len(desc) > 50:
            return desc
        
        # Si no, usar una heurística: tomar el bloque más grande de texto
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
        if paragraphs:
            return max(paragraphs, key=len)
        
        # Como último recurso, tomar las primeras líneas
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 3:
            return '\n'.join(lines[:min(10, len(lines))])
        
        return text[:500] if text else "Sin descripción disponible"
    
    def extract_requirements(self, text: str) -> str:
        """
        Extrae los requerimientos de la vacante.
        
        Args:
            text: Texto completo
            
        Returns:
            Requerimientos extraídos
        """
        # Intentar con patrones primero
        reqs = self.extract_field(text, 'requerimientos')
        if reqs and len(reqs) > 20:
            # Normalizar formato de bullets si es necesario
            reqs = re.sub(r'(?:^|\n)(\d+\.)\s*', r'\n- ', reqs, flags=re.MULTILINE)
            return reqs
        
        # Buscar listas con bullets
        bullet_pattern = r'(?:^|\n)[\-•*]\s*(.+)'
        bullets = re.findall(bullet_pattern, text, re.MULTILINE)
        if bullets and len(bullets) >= 2:
            return '\n'.join([f"- {b.strip()}" for b in bullets])
        
        # Buscar secciones numeradas
        numbered_pattern = r'(?:^|\n)(\d+[.\)]\s*.+?)(?=\n\d+[.\)]|\n\n|$)'
        numbered_matches = re.findall(numbered_pattern, text, re.MULTILINE | re.DOTALL)
        if numbered_matches and len(numbered_matches) >= 2:
            reqs_list = []
            for match in numbered_matches:
                # Limpiar y formatear
                clean = re.sub(r'^\d+[.\)]\s*', '', match.strip())
                if clean:
                    reqs_list.append(f"- {clean}")
            if reqs_list:
                return '\n'.join(reqs_list)
        
        # Buscar sección "Must have" o similar
        must_have_pattern = r'(?:must have|requirements|requisitos):\s*(.+?)(?=\n\n|$)'
        must_have = re.search(must_have_pattern, text, re.IGNORECASE | re.DOTALL)
        if must_have:
            return must_have.group(1).strip()
        
        return "No se pudieron extraer requerimientos específicos"
    
    def normalize_date(self, date_str: str) -> str:
        """
        Normaliza la fecha al formato YYYY-MM-DD.
        
        Args:
            date_str: Fecha en formato variable
            
        Returns:
            Fecha en formato YYYY-MM-DD
        """
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Intentar varios formatos
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%m-%d-%Y',
            '%m/%d/%Y',
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Si no se puede parsear, usar fecha actual
        if self.verbose:
            print(f"   ⚠️  No se pudo parsear fecha '{date_str}', usando fecha actual")
        return datetime.now().strftime('%Y-%m-%d')
    
    def extract_vacancy_fields(self, text: str) -> Dict:
        """
        Extrae todos los campos clave de una vacante.
        
        Args:
            text: Texto completo de la vacante
            
        Returns:
            Diccionario con los campos extraídos
        """
        fields = {}
        
        # Extraer campos básicos
        fields['cargo'] = self.extract_field(text, 'cargo')
        fields['empresa'] = self.extract_field(text, 'empresa')
        
        # Si no se encontró cargo, intentar con la primera línea no vacía
        if not fields['cargo']:
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if lines:
                first_line = lines[0]
                # Si la primera línea es corta y parece un título, usarla
                if len(first_line) < 100 and not first_line.endswith('.'):
                    fields['cargo'] = first_line.strip()
        
        # Si no se encontró empresa, buscar en las primeras líneas
        if not fields['empresa']:
            # Buscar patrones como "TechCorp Solutions", "DataMind Inc"
            empresa_match = re.search(r'\b([A-Z][A-Za-z0-9]+(?:\s+[A-Z][A-Za-z0-9]+){0,3}(?:\s+(?:Inc|Corp|Ltd|SA|SAS|Group|Solutions|Services|Technologies|Global))?)\b', text)
            if empresa_match:
                candidate = empresa_match.group(1).strip()
                # Validar que no sea un cargo común
                if not re.search(r'\b(developer|engineer|analyst|manager|specialist|coordinator)\b', candidate, re.IGNORECASE):
                    fields['empresa'] = candidate
        
        fecha_raw = self.extract_field(text, 'fecha')
        fields['fecha'] = self.normalize_date(fecha_raw) if fecha_raw else datetime.now().strftime('%Y-%m-%d')
        fields['modalidad'] = self.extract_field(text, 'modalidad')
        
        # Extraer descripción y requerimientos (más complejos)
        fields['descripcion'] = self.extract_description(text, fields)
        fields['requerimientos'] = self.extract_requirements(text)
        
        # Actualizar estadísticas
        for field, value in fields.items():
            if value and value != "Sin descripción disponible":
                self.stats['fields_extracted'][field] = self.stats['fields_extracted'].get(field, 0) + 1
            else:
                self.stats['fields_missing'][field] = self.stats['fields_missing'].get(field, 0) + 1
        
        return fields
    
    def generate_filename(self, fields: Dict) -> str:
        """
        Genera el nombre de archivo normalizado: cargo_empresa_fecha.yaml
        
        Args:
            fields: Campos extraídos de la vacante
            
        Returns:
            Nombre de archivo normalizado
        """
        cargo = self.normalize_for_filename(fields.get('cargo') or 'sin_cargo', 30)
        empresa = self.normalize_for_filename(fields.get('empresa') or 'sin_empresa', 30)
        fecha = fields.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        
        return f"{cargo}_{empresa}_{fecha}.yaml"
    
    def save_yaml(self, fields: Dict, output_path: Path) -> bool:
        """
        Guarda los campos extraídos en un archivo YAML.
        
        Args:
            fields: Campos extraídos
            output_path: Ruta del archivo de salida
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(fields, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            if self.verbose:
                print(f"   ❌ Error al guardar {output_path}: {e}")
            return False
    
    def process_text_file(self, input_file: Path, output_dir: Path) -> List[Dict]:
        """
        Procesa un archivo de texto con una o más vacantes.
        Las vacantes pueden estar separadas por líneas vacías dobles o '---'.
        
        Args:
            input_file: Archivo de entrada
            output_dir: Directorio de salida
            
        Returns:
            Lista de vacantes procesadas
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir por '---' o por bloques separados por líneas vacías dobles
        if '---' in content:
            blocks = [b.strip() for b in content.split('---') if b.strip()]
        else:
            blocks = [b.strip() for b in re.split(r'\n\s*\n\s*\n', content) if b.strip()]
        
        if not blocks:
            blocks = [content.strip()]
        
        if self.verbose:
            print(f"\n📄 Archivo: {input_file}")
            print(f"📊 Bloques detectados: {len(blocks)}")
            print("\n" + "="*70)
            print("EXTRACCIÓN DE CAMPOS")
            print("="*70 + "\n")
        
        processed_vacancies = []
        
        for i, block in enumerate(blocks, 1):
            if len(block) < 50:  # Ignorar bloques muy pequeños
                continue
            
            self.stats['processed'] += 1
            
            if self.verbose:
                print(f"📋 Procesando vacante {i}/{len(blocks)}...")
            
            # Extraer campos
            fields = self.extract_vacancy_fields(block)
            
            # Generar nombre de archivo
            filename = self.generate_filename(fields)
            output_path = output_dir / filename
            
            # Guardar YAML
            if self.save_yaml(fields, output_path):
                self.stats['successful'] += 1
                processed_vacancies.append({
                    'fields': fields,
                    'filename': filename,
                    'original_text': block
                })
                if self.verbose:
                    print(f"   ✅ Guardado: {filename}")
                    print(f"   📌 Cargo: {fields.get('cargo') or 'NO EXTRAÍDO'}")
                    print(f"   🏢 Empresa: {fields.get('empresa') or 'NO EXTRAÍDO'}")
                    print(f"   📅 Fecha: {fields.get('fecha')}")
                    if fields.get('modalidad'):
                        print(f"   🌐 Modalidad: {fields.get('modalidad')}")
            else:
                self.stats['failed'] += 1
        
        return processed_vacancies
    
    def generate_report(self, vacancies: List[Dict], output_dir: Path, dataset_result: Optional[Dict] = None):
        """
        Genera un reporte de la extracción con comparación y sugerencias.
        
        Args:
            vacancies: Lista de vacantes procesadas
            output_dir: Directorio de salida
            dataset_result: Resultado de la conversión a dataset (opcional)
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_processed': self.stats['processed'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'fields_extracted_counts': self.stats['fields_extracted'],
            'fields_missing_counts': self.stats['fields_missing'],
            'vacancies': []
        }
        
        # Agregar información detallada de cada vacante
        for v in vacancies:
            vacancy_info = {
                'filename': v['filename'],
                'cargo': v['fields'].get('cargo'),
                'empresa': v['fields'].get('empresa'),
                'fecha': v['fields'].get('fecha'),
                'modalidad': v['fields'].get('modalidad'),
                'has_descripcion': bool(v['fields'].get('descripcion')),
                'has_requerimientos': bool(v['fields'].get('requerimientos')),
                'original_length': len(v['original_text']),
                'descripcion_length': len(v['fields'].get('descripcion', '')),
                'requerimientos_length': len(v['fields'].get('requerimientos', '')),
            }
            
            # Calcular métricas de calidad
            quality_score = 0
            quality_notes = []
            
            if v['fields'].get('cargo'):
                quality_score += 20
            else:
                quality_notes.append("Cargo no extraído o incompleto")
            
            if v['fields'].get('empresa'):
                quality_score += 20
            else:
                quality_notes.append("Empresa no extraída")
            
            if v['fields'].get('descripcion') and len(v['fields'].get('descripcion', '')) > 50:
                quality_score += 20
            else:
                quality_notes.append("Descripción ausente o muy corta")
            
            if v['fields'].get('requerimientos') and len(v['fields'].get('requerimientos', '')) > 20:
                quality_score += 20
            else:
                quality_notes.append("Requerimientos ausentes o muy cortos")
            
            if v['fields'].get('modalidad'):
                quality_score += 10
            else:
                quality_notes.append("Modalidad no detectada")
            
            if v['fields'].get('fecha'):
                quality_score += 10
            
            vacancy_info['quality_score'] = quality_score
            vacancy_info['quality_notes'] = quality_notes
            
            report['vacancies'].append(vacancy_info)
        
        # Agregar información del dataset si está disponible
        if dataset_result:
            report['dataset_conversion'] = dataset_result
        
        # Calcular estadísticas generales
        avg_quality = sum(v['quality_score'] for v in report['vacancies']) / len(report['vacancies']) if report['vacancies'] else 0
        report['average_quality_score'] = round(avg_quality, 2)
        
        # Generar sugerencias
        suggestions = []
        
        if self.stats['fields_missing'].get('cargo', 0) > 0:
            suggestions.append({
                'field': 'cargo',
                'issue': f"{self.stats['fields_missing']['cargo']} vacantes sin cargo extraído",
                'suggestion': "Mejorar patrones de detección de cargo o estructurar mejor el texto original con etiquetas claras como 'Cargo:' o 'Posición:'"
            })
        
        if self.stats['fields_missing'].get('empresa', 0) > 0:
            suggestions.append({
                'field': 'empresa',
                'issue': f"{self.stats['fields_missing']['empresa']} vacantes sin empresa extraída",
                'suggestion': "Incluir el nombre de la empresa al inicio del texto o usar formato 'Empresa:' explícitamente"
            })
        
        if self.stats['fields_missing'].get('modalidad', 0) > 0:
            suggestions.append({
                'field': 'modalidad',
                'issue': f"{self.stats['fields_missing']['modalidad']} vacantes sin modalidad",
                'suggestion': "Especificar modalidad (remoto/híbrido/presencial) de forma explícita en el texto"
            })
        
        # Sugerencias basadas en calidad promedio
        if avg_quality < 60:
            suggestions.append({
                'field': 'general',
                'issue': f"Calidad promedio de extracción baja ({avg_quality:.1f}/100)",
                'suggestion': "Considere estructurar mejor las vacantes usando formato YAML o incluir etiquetas claras para cada campo"
            })
        elif avg_quality < 80:
            suggestions.append({
                'field': 'general',
                'issue': f"Calidad promedio de extracción moderada ({avg_quality:.1f}/100)",
                'suggestion': "Algunos campos no se están extrayendo correctamente. Revise el formato del texto original"
            })
        
        report['suggestions'] = suggestions
        
        # Guardar reporte JSON
        report_path = output_dir / 'extraction_report.json'
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Guardar reporte legible en texto
        text_report_path = output_dir / 'extraction_report.txt'
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("REPORTE DE EXTRACCIÓN DE VACANTES\n")
            f.write("="*70 + "\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("RESUMEN\n")
            f.write("-"*70 + "\n")
            f.write(f"Total procesadas: {self.stats['processed']}\n")
            f.write(f"Exitosas: {self.stats['successful']}\n")
            f.write(f"Fallidas: {self.stats['failed']}\n")
            f.write(f"Calidad promedio: {avg_quality:.1f}/100\n\n")
            
            f.write("CAMPOS EXTRAÍDOS\n")
            f.write("-"*70 + "\n")
            for field, count in sorted(self.stats['fields_extracted'].items()):
                f.write(f"  ✓ {field}: {count}\n")
            
            if self.stats['fields_missing']:
                f.write("\nCAMPOS NO EXTRAÍDOS\n")
                f.write("-"*70 + "\n")
                for field, count in sorted(self.stats['fields_missing'].items()):
                    f.write(f"  ✗ {field}: {count}\n")
            
            f.write("\nDETALLE POR VACANTE\n")
            f.write("-"*70 + "\n")
            for i, v in enumerate(report['vacancies'], 1):
                f.write(f"\n{i}. {v['filename']}\n")
                f.write(f"   Calidad: {v['quality_score']}/100\n")
                f.write(f"   Cargo: {v['cargo'] or 'NO EXTRAÍDO'}\n")
                f.write(f"   Empresa: {v['empresa'] or 'NO EXTRAÍDO'}\n")
                f.write(f"   Modalidad: {v['modalidad'] or 'NO EXTRAÍDO'}\n")
                if v['quality_notes']:
                    f.write(f"   Observaciones:\n")
                    for note in v['quality_notes']:
                        f.write(f"     - {note}\n")
            
            if suggestions:
                f.write("\n\nSUGERENCIAS DE MEJORA\n")
                f.write("="*70 + "\n")
                for i, sug in enumerate(suggestions, 1):
                    f.write(f"\n{i}. Campo: {sug['field']}\n")
                    f.write(f"   Problema: {sug['issue']}\n")
                    f.write(f"   Sugerencia: {sug['suggestion']}\n")
            
            if dataset_result and dataset_result.get('success'):
                f.write("\n\nCONVERSIÓN A DATASET\n")
                f.write("="*70 + "\n")
                f.write(f"Archivos generados: {', '.join(dataset_result.get('files_generated', []))}\n")
                f.write("\nUso del dataset:\n")
                f.write("  python scripts/train_line_classifier.py data/line_dataset.jsonl\n")
                f.write("  python scripts/train_tfidf_baseline.py data/line_dataset.jsonl\n")
        
        # Imprimir resumen en consola
        if self.verbose:
            print("\n" + "="*70)
            print("REPORTE DE EXTRACCIÓN")
            print("="*70)
            print(f"✅ Vacantes procesadas exitosamente: {self.stats['successful']}")
            print(f"❌ Vacantes fallidas: {self.stats['failed']}")
            print(f"📊 Calidad promedio: {avg_quality:.1f}/100")
            print(f"\n📊 Campos extraídos:")
            for field, count in sorted(self.stats['fields_extracted'].items()):
                print(f"   • {field}: {count}")
            if self.stats['fields_missing']:
                print(f"\n⚠️  Campos no extraídos:")
                for field, count in sorted(self.stats['fields_missing'].items()):
                    print(f"   • {field}: {count}")
            
            if suggestions:
                print(f"\n💡 SUGERENCIAS DE MEJORA:")
                for i, sug in enumerate(suggestions, 1):
                    print(f"   {i}. {sug['issue']}")
                    print(f"      → {sug['suggestion']}")
            
            print(f"\n💾 Reportes guardados:")
            print(f"   • JSON: {report_path}")
            print(f"   • Texto: {text_report_path}")
            print("="*70 + "\n")
        
        return report
    
    def run_dataset_conversion(self, yaml_dir: Path, output_dir: Path, vacancies: List[Dict]) -> Dict:
        """
        Ejecuta convert_to_line_dataset.py sobre los YAMLs generados.
        
        Args:
            yaml_dir: Directorio con archivos YAML
            output_dir: Directorio de salida para datasets
            vacancies: Lista de vacantes procesadas con texto original
            
        Returns:
            Resultado de la conversión
        """
        if self.verbose:
            print("\n" + "="*70)
            print("CONVERSIÓN A DATASET DE LÍNEAS")
            print("="*70 + "\n")
        
        # Crear JSONL en el formato esperado por convert_to_line_dataset.py
        # Formato: {"text": "...", "yaml": "cargo: ...\nempresa: ..."}
        jsonl_path = yaml_dir / 'training_data.jsonl'
        
        try:
            with open(jsonl_path, 'w', encoding='utf-8') as f:
                for vacancy in vacancies:
                    fields = vacancy['fields']
                    original_text = vacancy['original_text']
                    
                    # Crear representación YAML como string
                    yaml_str = yaml.dump(fields, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    
                    # Crear el objeto en formato esperado
                    item = {
                        'text': original_text,
                        'yaml': yaml_str
                    }
                    
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            if self.verbose:
                print(f"✅ Archivo JSONL para conversión creado: {jsonl_path}")
                print(f"   Vacantes: {len(vacancies)}\n")
        
        except Exception as e:
            if self.verbose:
                print(f"❌ Error al crear JSONL: {e}")
            return {'success': False, 'error': str(e)}
        
        # Ejecutar convert_to_line_dataset.py
        script_path = Path(__file__).parent / 'convert_to_line_dataset.py'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            cmd = [
                'python', str(script_path),
                '--input', str(jsonl_path),
                '--outdir', str(output_dir)
            ]
            
            if self.verbose:
                print(f"🔧 Ejecutando: {' '.join(cmd)}\n")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if self.verbose:
                print(result.stdout)
                if result.stderr:
                    print(f"⚠️  Stderr: {result.stderr}")
            
            # Verificar archivos generados
            expected_files = ['line_dataset.jsonl', 'line_dataset.csv', 'line_dataset_review.jsonl']
            generated = [f for f in expected_files if (output_dir / f).exists()]
            
            if self.verbose:
                print(f"\n✅ Archivos de dataset generados: {', '.join(generated)}")
            
            return {
                'success': True,
                'files_generated': generated
            }
        
        except subprocess.CalledProcessError as e:
            if self.verbose:
                print(f"❌ Error al ejecutar convert_to_line_dataset.py:")
                print(f"   {e.stderr}")
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Extrae campos de vacantes en texto plano y genera archivos YAML estructurados',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Extraer campos y generar YAMLs
  python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted
  
  # Extraer, generar YAMLs y ejecutar conversión a dataset
  python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --run-dataset-conversion
  
  # Extraer y generar reporte detallado
  python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --generate-report
  
  # Modo silencioso
  python scripts/extract_vacantes_from_text.py --input vacante.txt --output output/extracted --quiet
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=True,
        help='Archivo de entrada con vacantes en texto plano'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output/extracted_vacantes',
        help='Directorio de salida para archivos YAML'
    )
    
    parser.add_argument(
        '--run-dataset-conversion',
        action='store_true',
        help='Ejecutar convert_to_line_dataset.py después de la extracción'
    )
    
    parser.add_argument(
        '--dataset-output',
        type=str,
        default='data',
        help='Directorio de salida para datasets (usado con --run-dataset-conversion)'
    )
    
    parser.add_argument(
        '--generate-report',
        action='store_true',
        help='Generar reporte detallado de la extracción'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso (sin output detallado)'
    )
    
    args = parser.parse_args()
    
    # Crear extractor
    extractor = VacancyExtractor(verbose=not args.quiet)
    
    # Procesar archivo
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"❌ Error: El archivo {input_path} no existe")
        return 1
    
    vacancies = extractor.process_text_file(input_path, output_path)
    
    # Ejecutar conversión a dataset si se solicita
    dataset_result = None
    if args.run_dataset_conversion:
        dataset_result = extractor.run_dataset_conversion(
            output_path,
            Path(args.dataset_output),
            vacancies
        )
        
        if not dataset_result.get('success', False):
            print(f"⚠️  Advertencia: La conversión a dataset no se completó exitosamente")
    
    # Generar reporte si se solicita
    if args.generate_report or not args.quiet:
        extractor.generate_report(vacancies, output_path, dataset_result)
    
    return 0


if __name__ == '__main__':
    exit(main())
