import os
import re
from datetime import datetime

def normalize_filename(s):
    s = s.lower()
    s = re.sub(r"[áéíóúü]", lambda m: "aeiouu"["áéíóúü".index(m.group(0))], s)
    s = re.sub(r"[^a-z0-9]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def detect_modalidad(text):
    for modalidad in ["remoto", "remote", "híbrido", "hybrid", "presencial", "on-site"]:
        if modalidad.lower() in text.lower():
            if "remote" in modalidad.lower():
                return "remoto"
            elif "hybrid" in modalidad.lower() or "híbrido" in modalidad.lower():
                return "híbrido"
            elif "on-site" in modalidad.lower() or "presencial" in modalidad.lower():
                return "presencial"
    return ""

def extract_cargo_empresa(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cargo = ""
    empresa = ""
    # Busca patrón cargo/empresa en bloques
    for i in range(len(lines)-1):
        # Cargo: línea con palabras clave de cargos
        if re.search(r'(analista|business|developer|specialist|coordinator|manager|consultant|support|administration|data management|power bi|bi|desarrollador|funcional|calypso|back office|freight|administrador|procesos comerciales)', lines[i].lower()) and "logo" not in lines[i].lower():
            # Empresa: siguiente línea con mayúscula, sin palabras de ubicación ni cargos
            next_line = lines[i+1]
            if (
                re.match(r'^[A-Z][a-zA-Z0-9\s&\-\.,]+$', next_line)
                and "logo" not in next_line.lower()
                and not any(x in next_line.lower() for x in ["colombia","remote","híbrido","presencial","analista","business"])
            ):
                cargo = lines[i]
                empresa = next_line
                break
    # Si no encontró, busca línea con "·" y toma lo anterior
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
    # Fallback: primer nombre propio que no sea ubicación/cargo
    if not empresa:
        for line in lines:
            if (
                re.match(r'^[A-Z][a-zA-Z0-9\s&\-\.,]+$', line)
                and "colombia" not in line.lower()
                and "remote" not in line.lower()
                and "híbrido" not in line.lower()
                and "presencial" not in line.lower()
                and "analista" not in line.lower()
                and "business" not in line.lower()
            ):
                empresa = line
                break
    # Cargo fallback
    if not cargo:
        m = re.search(r'(analista|business|developer|specialist|coordinator|manager|consultant|support|administration|data management|power bi|bi|desarrollador|funcional|calypso|back office|freight|administrador|procesos comerciales)[^\n]*', text, re.IGNORECASE)
        if m:
            cargo = m.group(0).strip()
    return cargo, empresa

def extract_requerimientos(text):
    requerimientos = []
    req_match = re.findall(r'(?:Requerimientos|Requirements|Responsabilidades Clave|Key Responsibilities|Qualifications|Responsabilidades|Responsabilidades principales|What We’re Looking For|Lo que buscamos en ti|Condiciones de trabajo|Skills|Required Skills|Responsabilidades:|Requisitos:|Requisitos y conocimientos del Rol:|Qué buscamos en ti:|Lo que harás:|What You’ll Do:)\s*[\n:]*([\s\S]*?)(?:\n{2,}|$)', text, re.IGNORECASE)
    for req_block in req_match:
        for line in req_block.splitlines():
            line = line.strip('-• \n\t')
            if line and len(line) > 4:
                requerimientos.append(line)
    return requerimientos

def split_vacantes(input_file, output_dir):
    with open(input_file, encoding='utf-8') as f:
        content = f.read()

    vacantes = content.split('---')
    for idx, vacante in enumerate(vacantes):
        vacante = vacante.strip()
        if not vacante:
            continue

        cargo, empresa = extract_cargo_empresa(vacante)
        fecha = datetime.now().strftime('%Y-%m-%d')
        modalidad = detect_modalidad(vacante)
        requerimientos = extract_requerimientos(vacante)
        descripcion = vacante.replace('\r', '')  # Todo el texto plano

        cargo_norm = normalize_filename(cargo) if cargo else f"vacante_{idx+1}"
        empresa_norm = normalize_filename(empresa) if empresa else "empresa"
        filename = f"{cargo_norm}_{empresa_norm}_{fecha}.yaml"
        filepath = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)

        yaml_content = f'''cargo: "{cargo}"
empresa: "{empresa}"
fecha: "{fecha}"
modalidad: "{modalidad}"
descripcion: |
  {descripcion.replace("\n", "\n  ")}
requerimientos:
'''
        for req in requerimientos:
            yaml_content += f"  - {req}\n"
        with open(filepath, 'w', encoding='utf-8') as out:
            out.write(yaml_content)
        print(f'Escribiendo: {filepath}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Uso: python scripts/split_vacantes_to_yaml.py vacantes.txt vacantes_yaml")
        sys.exit(1)
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    split_vacantes(input_file, output_dir)