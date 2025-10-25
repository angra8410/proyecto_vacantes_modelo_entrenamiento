import os
import re
from datetime import datetime

def extract_field(text, field):
    # Busca el valor del campo cerca del nombre del campo
    pattern = rf"{field}\s*:\s*([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""

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

def normalize_filename(s):
    s = s.lower()
    s = re.sub(r"[áéíóúü]", lambda m: "aeiouu"["áéíóúü".index(m.group(0))], s)
    s = re.sub(r"[^a-z0-9]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def extract_cargo_empresa(text):
    # Heurística mejorada para cargo y empresa
    cargo = ""
    empresa = ""
    # Busca líneas tipo "Cargo Empresa · Ubicación"
    lines = text.splitlines()
    for i, line in enumerate(lines):
        line = line.strip()
        # Busca patrón "Cargo" seguido de "Empresa"
        m = re.match(r"([A-Za-z0-9 &\-/]+)\s*\n([A-Za-z0-9 &\-/]+)\s*·", "\n".join(lines[i:i+2]))
        if m:
            cargo = m.group(1)
            empresa = m.group(2)
            break
        # Alternativamente busca líneas indicativas
        if i < len(lines) - 1 and "Save" not in line and "Apply" not in line and "logo" not in line:
            # Si la siguiente línea tiene "·", probablemente es empresa
            if "·" in lines[i+1]:
                cargo = line
                empresa = lines[i+1].split("·")[0].strip()
                break
    # Fallbacks
    if not cargo:
        m = re.search(r"(senior|jr\.?|analista|developer|analyst|coordinator|specialist|manager|business|track and trace|operations support|workforce|consultant|support|administration|data management|power bi|bi|desarrollador|funcional|calypso|back office|analista|freight|ocean freight|administrador|consultor|procesos comerciales|administración|coordinador)[^\n]*", text, re.IGNORECASE)
        if m:
            cargo = m.group(0).strip()
    if not empresa:
        m = re.search(r"([A-Z][a-zA-Z0-9&.,\-\s]+)(?:\s+logo)?", text)
        if m:
            empresa = m.group(1).strip()
    return cargo, empresa

def extract_requerimientos(text):
    # Extrae requerimientos por heurística
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