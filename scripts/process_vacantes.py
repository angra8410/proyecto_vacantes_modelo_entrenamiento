#!/usr/bin/env python3
"""
scripts/process_vacantes.py

Módulo para procesar y validar un archivo vacantes.txt con múltiples vacantes 
en formato YAML separadas por '---', generar archivos .yaml individuales por 
cada vacante, y reportar inconsistencias en la estructura o campos esenciales.

Campos requeridos:
  - cargo
  - empresa
  - fecha
  - descripcion
  - requerimientos

Uso:
  python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes
  python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl
  python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl --jsonl-file vacantes.jsonl

"""
import argparse
import json
import re
import yaml
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Tuple, Optional


class VacancyProcessor:
    """Procesador de vacantes en formato YAML."""
    
    REQUIRED_FIELDS = ['cargo', 'empresa', 'fecha', 'descripcion', 'requerimientos']
    
    def __init__(self, input_file: Path, output_dir: Path, verbose: bool = True):
        """
        Inicializa el procesador de vacantes.
        
        Args:
            input_file: Ruta al archivo vacantes.txt
            output_dir: Directorio de salida para archivos .yaml individuales
            verbose: Si debe imprimir información detallada
        """
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
        
    def read_vacantes_file(self) -> List[str]:
        """
        Lee el archivo de vacantes y lo divide por el delimitador '---'.
        
        Returns:
            Lista de bloques YAML como strings
        """
        if not self.input_file.exists():
            raise FileNotFoundError(f"El archivo {self.input_file} no existe")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dividir por '---' y filtrar bloques vacíos
        blocks = [block.strip() for block in content.split('---') if block.strip()]
        
        if self.verbose:
            print(f"📄 Archivo leído: {self.input_file}")
            print(f"📊 Bloques encontrados: {len(blocks)}")
        
        return blocks
    
    def validate_vacancy(self, vacancy: Dict, block_num: int) -> Tuple[bool, List[str]]:
        """
        Valida que una vacante contenga todos los campos requeridos.
        
        Args:
            vacancy: Diccionario con los datos de la vacante
            block_num: Número de bloque para reportar errores
            
        Returns:
            Tupla (es_valido, lista_de_errores)
        """
        errors = []
        
        # Validar campos requeridos
        for field in self.REQUIRED_FIELDS:
            if field not in vacancy:
                errors.append(f"Campo faltante: '{field}'")
            elif not vacancy[field] or (isinstance(vacancy[field], str) and not vacancy[field].strip()):
                errors.append(f"Campo vacío: '{field}'")
        
        # Validaciones adicionales
        if 'fecha' in vacancy:
            if not self._validate_date_format(vacancy['fecha']):
                errors.append(f"Formato de fecha inválido: '{vacancy['fecha']}' (esperado: YYYY-MM-DD)")
        
        return len(errors) == 0, errors
    
    def _validate_date_format(self, date_value) -> bool:
        """
        Valida que la fecha tenga formato correcto (YYYY-MM-DD) o sea un objeto date válido.
        
        Args:
            date_value: String con la fecha o objeto datetime.date
            
        Returns:
            True si el formato es válido
        """
        # Si es un objeto datetime.date o datetime.datetime, es válido
        if isinstance(date_value, (datetime, date)):
            return True
        
        # Si es un string, intentar parsearlo
        if isinstance(date_value, str):
            try:
                datetime.strptime(date_value, '%Y-%m-%d')
                return True
            except ValueError:
                return False
        
        return False
    
    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Sanitiza un texto para usar como nombre de archivo.
        
        Args:
            text: Texto a sanitizar
            max_length: Longitud máxima
            
        Returns:
            Texto sanitizado
        """
        # Remover caracteres especiales y espacios
        text = re.sub(r'[^\w\s-]', '', str(text))
        text = re.sub(r'[\s]+', '_', text)
        # Truncar si es muy largo
        if len(text) > max_length:
            text = text[:max_length]
        return text.strip('_')
    
    def generate_filename(self, vacancy: Dict) -> str:
        """
        Genera el nombre de archivo para una vacante.
        Formato: {fecha}_{cargo}_{empresa}.yaml
        
        Args:
            vacancy: Diccionario con los datos de la vacante
            
        Returns:
            Nombre de archivo generado
        """
        # Convertir fecha a string si es necesario
        fecha_value = vacancy.get('fecha', 'sin_fecha')
        if isinstance(fecha_value, (datetime, date)):
            fecha_value = fecha_value.strftime('%Y-%m-%d')
        
        fecha = self._sanitize_filename(fecha_value, 10)
        cargo = self._sanitize_filename(vacancy.get('cargo', 'sin_cargo'), 30)
        empresa = self._sanitize_filename(vacancy.get('empresa', 'sin_empresa'), 30)
        
        return f"{fecha}_{cargo}_{empresa}.yaml"
    
    def save_yaml_file(self, vacancy: Dict, filename: str) -> bool:
        """
        Guarda una vacante en un archivo YAML individual.
        
        Args:
            vacancy: Diccionario con los datos de la vacante
            filename: Nombre del archivo de salida
            
        Returns:
            True si se guardó exitosamente
        """
        try:
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(vacancy, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            return True
        except Exception as e:
            if self.verbose:
                print(f"❌ Error al guardar {filename}: {e}")
            return False
    
    def process_all(self) -> Dict:
        """
        Procesa todas las vacantes del archivo.
        
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        # Crear directorio de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Leer bloques YAML
        blocks = self.read_vacantes_file()
        self.stats['total'] = len(blocks)
        
        valid_vacancies = []
        
        if self.verbose:
            print("\n" + "="*70)
            print("PROCESAMIENTO DE VACANTES")
            print("="*70 + "\n")
        
        # Procesar cada bloque
        for i, block in enumerate(blocks, start=1):
            if self.verbose:
                print(f"\n📋 Procesando bloque {i}/{len(blocks)}...")
            
            try:
                # Parsear YAML
                vacancy = yaml.safe_load(block)
                
                if not isinstance(vacancy, dict):
                    error_msg = f"Bloque {i}: No es un diccionario YAML válido"
                    self.stats['errors'].append({'bloque': i, 'error': error_msg})
                    self.stats['invalid'] += 1
                    if self.verbose:
                        print(f"   ❌ {error_msg}")
                    continue
                
                # Validar campos
                is_valid, errors = self.validate_vacancy(vacancy, i)
                
                if is_valid:
                    # Generar nombre de archivo
                    filename = self.generate_filename(vacancy)
                    
                    # Guardar archivo YAML
                    if self.save_yaml_file(vacancy, filename):
                        self.stats['valid'] += 1
                        valid_vacancies.append(vacancy)
                        if self.verbose:
                            print(f"   ✅ Guardado: {filename}")
                    else:
                        self.stats['invalid'] += 1
                        error_msg = f"Error al guardar archivo"
                        self.stats['errors'].append({'bloque': i, 'error': error_msg})
                else:
                    self.stats['invalid'] += 1
                    error_detail = {
                        'bloque': i,
                        'errores': errors,
                        'cargo': vacancy.get('cargo', 'N/A'),
                        'empresa': vacancy.get('empresa', 'N/A')
                    }
                    self.stats['errors'].append(error_detail)
                    
                    if self.verbose:
                        print(f"   ❌ Vacante inválida:")
                        for error in errors:
                            print(f"      • {error}")
                        print(f"      Cargo: {vacancy.get('cargo', 'N/A')}")
                        print(f"      Empresa: {vacancy.get('empresa', 'N/A')}")
            
            except yaml.YAMLError as e:
                error_msg = f"Error al parsear YAML: {str(e)}"
                self.stats['errors'].append({'bloque': i, 'error': error_msg})
                self.stats['invalid'] += 1
                if self.verbose:
                    print(f"   ❌ {error_msg}")
            
            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                self.stats['errors'].append({'bloque': i, 'error': error_msg})
                self.stats['invalid'] += 1
                if self.verbose:
                    print(f"   ❌ {error_msg}")
        
        # Mostrar resumen
        if self.verbose:
            self._print_summary()
        
        return {
            'stats': self.stats,
            'valid_vacancies': valid_vacancies
        }
    
    def _print_summary(self):
        """Imprime un resumen del procesamiento."""
        print("\n" + "="*70)
        print("RESUMEN DEL PROCESAMIENTO")
        print("="*70)
        print(f"📊 Total de bloques procesados: {self.stats['total']}")
        print(f"✅ Vacantes válidas: {self.stats['valid']}")
        print(f"❌ Vacantes inválidas: {self.stats['invalid']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  ERRORES DETECTADOS ({len(self.stats['errors'])}):")
            print("-"*70)
            for i, error in enumerate(self.stats['errors'], start=1):
                print(f"\n{i}. Bloque {error.get('bloque', 'N/A')}:")
                if 'errores' in error:
                    for err in error['errores']:
                        print(f"   • {err}")
                    print(f"   Cargo: {error.get('cargo', 'N/A')}")
                    print(f"   Empresa: {error.get('empresa', 'N/A')}")
                else:
                    print(f"   • {error.get('error', 'Error desconocido')}")
        
        print("\n" + "="*70)
        print(f"💾 Archivos guardados en: {self.output_dir.absolute()}")
        print("="*70 + "\n")
    
    def convert_to_jsonl(self, valid_vacancies: List[Dict], output_file: Path):
        """
        Convierte las vacantes válidas a formato JSONL.
        
        Args:
            valid_vacancies: Lista de vacantes válidas
            output_file: Ruta del archivo JSONL de salida
        """
        if not valid_vacancies:
            if self.verbose:
                print("⚠️  No hay vacantes válidas para convertir a JSONL")
            return
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for vacancy in valid_vacancies:
                    # Convertir objetos date a string para JSON
                    vacancy_copy = vacancy.copy()
                    if 'fecha' in vacancy_copy and isinstance(vacancy_copy['fecha'], (datetime, date)):
                        vacancy_copy['fecha'] = vacancy_copy['fecha'].strftime('%Y-%m-%d')
                    
                    json_line = json.dumps(vacancy_copy, ensure_ascii=False)
                    f.write(json_line + '\n')
            
            if self.verbose:
                print(f"\n✅ Archivo JSONL creado: {output_file.absolute()}")
                print(f"   Vacantes exportadas: {len(valid_vacancies)}")
        
        except Exception as e:
            if self.verbose:
                print(f"\n❌ Error al crear archivo JSONL: {e}")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description='Procesa vacantes en formato YAML y genera archivos individuales',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Procesar vacantes y generar archivos YAML
  python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes
  
  # Procesar y convertir a JSONL
  python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl
  
  # Especificar nombre del archivo JSONL
  python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --to-jsonl --jsonl-file mis_vacantes.jsonl
  
  # Modo silencioso (sin output detallado)
  python scripts/process_vacantes.py --input vacantes.txt --output output/vacantes --quiet
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='vacantes.txt',
        help='Archivo de entrada con vacantes en formato YAML separadas por ---'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='output/vacantes',
        help='Directorio de salida para archivos YAML individuales'
    )
    
    parser.add_argument(
        '--to-jsonl',
        action='store_true',
        help='Convertir las vacantes válidas a formato JSONL'
    )
    
    parser.add_argument(
        '--jsonl-file',
        type=str,
        default='vacantes.jsonl',
        help='Nombre del archivo JSONL de salida (solo si --to-jsonl está activo)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso (sin output detallado)'
    )
    
    args = parser.parse_args()
    
    # Crear procesador
    processor = VacancyProcessor(
        input_file=Path(args.input),
        output_dir=Path(args.output),
        verbose=not args.quiet
    )
    
    # Procesar vacantes
    result = processor.process_all()
    
    # Convertir a JSONL si se solicita
    if args.to_jsonl:
        jsonl_path = Path(args.output) / args.jsonl_file
        processor.convert_to_jsonl(result['valid_vacancies'], jsonl_path)
    
    # Retornar código de salida apropiado
    if result['stats']['invalid'] > 0:
        return 1
    return 0


if __name__ == '__main__':
    exit(main())
