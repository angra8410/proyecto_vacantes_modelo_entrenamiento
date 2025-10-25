import os
import re
from datetime import datetime

def extract_cargo_empresa(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cargo = ""
    empresa = ""
    # Busca líneas tipo "Cargo" y "Empresa"
    # Busca el primer bloque donde la línea anterior es el cargo y la siguiente es la empresa
    for i in range(len(lines)-1):
        if re.match(r'^[A-Z][a-zA-Z\s/&\-\.]+$', lines[i]) and "logo" not in lines[i].lower() and "apply" not in lines[i].lower() and "save" not in lines[i].lower():
            # La empresa suele estar en la línea siguiente si comienza por mayúscula y contiene palabras típicas
            if re.match(r'^[A-Z][a-zA-Z\s&\-\.,]+$', lines[i+1]) and "logo" not in lines[i+1].lower() and not any(x in lines[i+1].lower() for x in ["colombia","remote","híbrido","presencial"]):
                cargo = lines[i]
                empresa = lines[i+1]
                break
    # Si no encuentra, busca la línea que contenga "·" y tome lo anterior
    if not empresa:
        for line in lines:
            if "·" in line:
                parts = line.split("·")
                empresa_candidate = parts[0].strip()
                if (
                    empresa_candidate
                    and "colombia" not in empresa_candidate.lower()
                    and "remote" not in empresa_candidate.lower()
                ):
                    empresa = empresa_candidate
                    break
    # Fallback: busca primer nombre propio que no sea ubicación
    if not empresa:
        for line in lines:
            if (
                re.match(r'^[A-Z][a-zA-Z\s&\-\.,]+$', line)
                and "colombia" not in line.lower()
                and "remote" not in line.lower()
                and "híbrido" not in line.lower()
                and "presencial" not in line.lower()
                and "analista" not in line.lower()
                and "business" not in line.lower()
            ):
                empresa = line
                break
    return cargo, empresa

# El resto del script igual...