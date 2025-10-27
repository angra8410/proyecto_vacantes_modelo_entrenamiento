#!/usr/bin/env python3
"""
scripts/copy_to_process.py

Script para copiar vacantes desde /vacantes_yaml_manual/ a /to_process/
cuando se detectan cambios en vacantes_yaml_manual.

Este script reemplaza la funcionalidad anterior que copiaba a un repositorio externo.

Uso:
  python scripts/copy_to_process.py
  python scripts/copy_to_process.py --source vacantes_yaml_manual --dest to_process
  python scripts/copy_to_process.py --all  # Copiar todos los archivos, no solo los modificados
"""

import argparse
import shutil
import subprocess
from pathlib import Path
from typing import List, Set
import sys


class VacancyCopier:
    """Copiador de vacantes de manual a to_process."""
    
    def __init__(self, source_dir: str, dest_dir: str, verbose: bool = True):
        """
        Inicializa el copiador.
        
        Args:
            source_dir: Directorio fuente (vacantes_yaml_manual)
            dest_dir: Directorio destino (to_process)
            verbose: Modo verboso
        """
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.verbose = verbose
        self.stats = {
            'copied': 0,
            'failed': 0,
            'total': 0
        }
    
    def log(self, message: str):
        """Imprime mensaje si verbose está activado."""
        if self.verbose:
            print(message)
    
    def get_modified_or_added_yaml_files(self) -> List[str]:
        """
        Obtiene archivos YAML modificados o agregados en el último commit.
        
        Returns:
            Lista de rutas relativas de archivos modificados/agregados
        """
        try:
            # Intentar obtener archivos modificados del último commit
            result = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD^", "HEAD"],
                capture_output=True, 
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                self.log("⚠️  No se pudo ejecutar git diff-tree (quizás es el primer commit)")
                return []
            
            files = []
            for line in result.stdout.splitlines():
                if '\t' not in line:
                    continue
                
                status, fname = line.split('\t', 1)
                # status: 'A' (added) o 'M' (modified)
                if fname.startswith(f"{self.source_dir}/") and fname.endswith(".yaml") and status in ("A", "M"):
                    files.append(fname)
            
            return files
            
        except Exception as e:
            self.log(f"⚠️  Error obteniendo archivos modificados: {e}")
            return []
    
    def get_all_yaml_files(self) -> List[Path]:
        """
        Obtiene todos los archivos YAML del directorio fuente.
        
        Returns:
            Lista de Paths de archivos YAML
        """
        if not self.source_dir.exists():
            return []
        
        return list(self.source_dir.glob('*.yaml'))
    
    def copy_file(self, source_file: Path) -> bool:
        """
        Copia un archivo desde source_dir a dest_dir.
        
        Args:
            source_file: Path al archivo fuente
            
        Returns:
            True si se copió exitosamente, False en caso contrario
        """
        try:
            # Crear directorio destino si no existe
            self.dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar el archivo
            dest_file = self.dest_dir / source_file.name
            shutil.copy2(source_file, dest_file)
            
            self.log(f"✅ Copiado: {source_file.name} → {dest_file}")
            return True
            
        except Exception as e:
            self.log(f"❌ Error copiando {source_file.name}: {str(e)}")
            return False
    
    def copy_modified_files(self) -> dict:
        """
        Copia solo los archivos modificados o agregados en el último commit.
        
        Returns:
            Diccionario con estadísticas
        """
        modified_files = self.get_modified_or_added_yaml_files()
        
        if not modified_files:
            self.log("ℹ️  No hay archivos YAML modificados/agregados en el último commit")
            return self.stats
        
        self.log(f"\n{'='*60}")
        self.log(f"Copiando archivos modificados/agregados")
        self.log(f"{'='*60}\n")
        
        for rel_path in modified_files:
            source_file = Path(rel_path)
            
            if not source_file.exists():
                self.log(f"⚠️  Archivo no existe: {source_file}")
                continue
            
            self.stats['total'] += 1
            
            if self.copy_file(source_file):
                self.stats['copied'] += 1
            else:
                self.stats['failed'] += 1
        
        return self.stats
    
    def copy_all_files(self) -> dict:
        """
        Copia todos los archivos YAML del directorio fuente.
        
        Returns:
            Diccionario con estadísticas
        """
        yaml_files = self.get_all_yaml_files()
        self.stats['total'] = len(yaml_files)
        
        if not yaml_files:
            self.log(f"ℹ️  No hay archivos YAML en {self.source_dir}")
            return self.stats
        
        self.log(f"\n{'='*60}")
        self.log(f"Copiando todos los archivos YAML")
        self.log(f"{'='*60}\n")
        
        for source_file in yaml_files:
            if self.copy_file(source_file):
                self.stats['copied'] += 1
            else:
                self.stats['failed'] += 1
        
        return self.stats
    
    def print_summary(self):
        """Imprime resumen de la operación."""
        if self.stats['total'] == 0:
            return
        
        self.log(f"\n{'='*60}")
        self.log(f"Resumen de Copia")
        self.log(f"{'='*60}")
        self.log(f"Total:      {self.stats['total']}")
        self.log(f"Copiados:   {self.stats['copied']} ✅")
        self.log(f"Fallidos:   {self.stats['failed']} ❌")
        self.log(f"{'='*60}\n")


def main():
    """Función principal."""
    parser = argparse.ArgumentParser(
        description='Copiar vacantes desde vacantes_yaml_manual a to_process'
    )
    parser.add_argument(
        '--source',
        default='vacantes_yaml_manual',
        help='Directorio fuente (default: vacantes_yaml_manual)'
    )
    parser.add_argument(
        '--dest',
        default='to_process',
        help='Directorio destino (default: to_process)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Copiar todos los archivos, no solo los modificados'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso'
    )
    
    args = parser.parse_args()
    
    # Crear copiador
    copier = VacancyCopier(
        source_dir=args.source,
        dest_dir=args.dest,
        verbose=not args.quiet
    )
    
    # Copiar archivos
    if args.all:
        stats = copier.copy_all_files()
    else:
        stats = copier.copy_modified_files()
    
    # Imprimir resumen
    copier.print_summary()
    
    # Código de salida
    if stats['total'] == 0:
        sys.exit(0)  # No hay nada que copiar
    elif stats['failed'] > 0:
        sys.exit(1)  # Hubo errores
    else:
        sys.exit(0)  # Todo bien


if __name__ == '__main__':
    main()
