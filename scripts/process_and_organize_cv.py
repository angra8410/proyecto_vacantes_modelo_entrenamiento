#!/usr/bin/env python3
"""
scripts/process_and_organize_cv.py

Script para procesar vacantes desde /to_process/ y organizar CVs generados
en /aplicaciones/ por fecha (mes y día).

Flujo:
1. Lee vacantes desde /to_process/*.yaml
2. Genera documentos/CVs requeridos
3. Organiza CVs en /aplicaciones/YYYY/MM/DD/
4. Mueve vacantes procesadas a un subdirectorio de respaldo

Uso:
  python scripts/process_and_organize_cv.py
  python scripts/process_and_organize_cv.py --to-process-dir to_process --aplicaciones-dir aplicaciones
"""

import argparse
import shutil
import yaml
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional
import sys


class CVProcessor:
    """Procesador de CVs y organizador por fecha."""
    
    def __init__(self, to_process_dir: Path, aplicaciones_dir: Path, verbose: bool = True):
        """
        Inicializa el procesador de CVs.
        
        Args:
            to_process_dir: Directorio con vacantes a procesar
            aplicaciones_dir: Directorio base para almacenar CVs
            verbose: Modo verboso
        """
        self.to_process_dir = Path(to_process_dir)
        self.aplicaciones_dir = Path(aplicaciones_dir)
        self.verbose = verbose
        self.stats = {
            'processed': 0,
            'failed': 0,
            'total': 0
        }
    
    def log(self, message: str):
        """Imprime mensaje si verbose está activado."""
        if self.verbose:
            print(message)
    
    def parse_date_from_yaml(self, data: Dict) -> Optional[date]:
        """
        Extrae y normaliza la fecha desde el YAML.
        
        Args:
            data: Diccionario con datos de la vacante
            
        Returns:
            Objeto date o None si no se puede parsear
        """
        fecha = data.get('fecha')
        
        if not fecha:
            return None
        
        # Si ya es un objeto date
        if isinstance(fecha, date):
            return fecha
        
        # Si es string, intentar parsear
        if isinstance(fecha, str):
            # Formato YYYY-MM-DD
            try:
                return datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                pass
            
            # Formato DD/MM/YYYY
            try:
                return datetime.strptime(fecha, '%d/%m/%Y').date()
            except ValueError:
                pass
            
            # Formato MM/DD/YYYY
            try:
                return datetime.strptime(fecha, '%m/%d/%Y').date()
            except ValueError:
                pass
        
        return None
    
    def get_destination_path(self, vacancy_date: date, filename: str) -> Path:
        """
        Genera la ruta de destino para un CV basado en la fecha.
        
        Args:
            vacancy_date: Fecha de la vacante
            filename: Nombre del archivo
            
        Returns:
            Path completo para el archivo de destino
        """
        year = str(vacancy_date.year)
        month = f"{vacancy_date.month:02d}"
        day = f"{vacancy_date.day:02d}"
        
        dest_dir = self.aplicaciones_dir / year / month / day
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        return dest_dir / filename
    
    def generate_cv_document(self, vacancy_data: Dict, vacancy_file: Path) -> Optional[Path]:
        """
        Genera el documento CV/aplicación para una vacante.
        
        Por ahora, copia el YAML de la vacante como el CV.
        En el futuro, aquí se puede implementar la generación de PDFs,
        Word docs, o cualquier otro formato de documento.
        
        Args:
            vacancy_data: Datos de la vacante
            vacancy_file: Archivo de la vacante
            
        Returns:
            Path al archivo generado o None si falla
        """
        # Por ahora, el "CV" es el mismo archivo YAML
        # En el futuro, aquí se puede integrar con generadores de PDF, etc.
        return vacancy_file
    
    def process_vacancy(self, vacancy_file: Path) -> bool:
        """
        Procesa una vacante individual.
        
        Args:
            vacancy_file: Path al archivo YAML de la vacante
            
        Returns:
            True si se procesó exitosamente, False en caso contrario
        """
        try:
            # Leer el YAML
            with open(vacancy_file, 'r', encoding='utf-8') as f:
                vacancy_data = yaml.safe_load(f)
            
            if not vacancy_data:
                self.log(f"⚠️  Archivo vacío: {vacancy_file.name}")
                return False
            
            # Obtener la fecha
            vacancy_date = self.parse_date_from_yaml(vacancy_data)
            if not vacancy_date:
                self.log(f"⚠️  No se pudo extraer fecha de: {vacancy_file.name}")
                # Usar fecha actual como fallback
                vacancy_date = date.today()
                self.log(f"   Usando fecha actual: {vacancy_date}")
            
            # Generar el documento CV
            cv_file = self.generate_cv_document(vacancy_data, vacancy_file)
            if not cv_file:
                self.log(f"❌ Error generando CV para: {vacancy_file.name}")
                return False
            
            # Determinar ruta de destino
            dest_path = self.get_destination_path(vacancy_date, vacancy_file.name)
            
            # Copiar el archivo
            shutil.copy2(cv_file, dest_path)
            self.log(f"✅ CV guardado: {dest_path}")
            
            # Mover el archivo procesado a un subdirectorio de respaldo
            processed_dir = self.to_process_dir / 'processed'
            processed_dir.mkdir(exist_ok=True)
            processed_path = processed_dir / vacancy_file.name
            
            shutil.move(str(vacancy_file), str(processed_path))
            self.log(f"   Vacante movida a: {processed_path}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error procesando {vacancy_file.name}: {str(e)}")
            return False
    
    def process_all(self) -> Dict[str, int]:
        """
        Procesa todas las vacantes en to_process/.
        
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        # Verificar que exista el directorio
        if not self.to_process_dir.exists():
            self.log(f"❌ Directorio no existe: {self.to_process_dir}")
            return self.stats
        
        # Obtener todos los archivos YAML
        yaml_files = list(self.to_process_dir.glob('*.yaml'))
        self.stats['total'] = len(yaml_files)
        
        if not yaml_files:
            self.log(f"ℹ️  No hay vacantes para procesar en {self.to_process_dir}")
            return self.stats
        
        self.log(f"\n{'='*60}")
        self.log(f"Procesando {self.stats['total']} vacante(s)")
        self.log(f"{'='*60}\n")
        
        # Procesar cada archivo
        for vacancy_file in yaml_files:
            if self.process_vacancy(vacancy_file):
                self.stats['processed'] += 1
            else:
                self.stats['failed'] += 1
        
        # Resumen final
        self.log(f"\n{'='*60}")
        self.log(f"Resumen de Procesamiento")
        self.log(f"{'='*60}")
        self.log(f"Total:      {self.stats['total']}")
        self.log(f"Exitosos:   {self.stats['processed']} ✅")
        self.log(f"Fallidos:   {self.stats['failed']} ❌")
        self.log(f"{'='*60}\n")
        
        return self.stats


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Procesar vacantes y organizar CVs por fecha'
    )
    parser.add_argument(
        '--to-process-dir',
        default='to_process',
        help='Directorio con vacantes a procesar (default: to_process)'
    )
    parser.add_argument(
        '--aplicaciones-dir',
        default='aplicaciones',
        help='Directorio base para almacenar CVs (default: aplicaciones)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso (sin salida verbose)'
    )
    
    args = parser.parse_args()
    
    # Crear procesador
    processor = CVProcessor(
        to_process_dir=args.to_process_dir,
        aplicaciones_dir=args.aplicaciones_dir,
        verbose=not args.quiet
    )
    
    # Procesar todas las vacantes
    stats = processor.process_all()
    
    # Código de salida basado en el resultado
    if stats['total'] == 0:
        sys.exit(0)  # No hay nada que procesar
    elif stats['failed'] > 0:
        sys.exit(1)  # Hubo errores
    else:
        sys.exit(0)  # Todo bien


if __name__ == '__main__':
    main()
