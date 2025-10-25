import os
import re
from datetime import datetime

# Palabras que NO deben ser empresa ni cargo
IGNORE_LINES = {
    "easy apply","save","share","show more options","logo",
    "matches your job preferences","apply","about the job",
    "remote","full-time","contract","hybrid","on-site",
    "colombia","capital district","latin america","bogo"
}

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

def clean_line(line):
    return line.strip().lower()

def is_valid(line):
    l = clean_line(line)
    return l and l not in IGNORE_LINES and not l.endswith("logo") and not re.match(r"\s*[\d]+ (applicants|people clicked apply)", l)

def extract_cargo_empresa(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cargo, empresa = "", ""
    # 1. Busca patrón típico: "Cargo\nEmpresa · Ubicación"
    for i in range(len(lines)-1):
        l1, l2 = lines[i], lines[i+1]
        if is_valid(l1) and is_valid(l2):
            # Si la segunda línea contiene "·", lo que va antes suele ser empresa
            if "·" in l2 and not any(x in l2.lower() for x in IGNORE_LINES):
                empresa_candidate = l2.split("·")[0].strip()
                if is_valid(empresa_candidate):
                    cargo = l1
                    empresa = empresa_candidate
                    break
    # 2. Busca la primera línea válida después de "logo" que no sea acción/ubicación
    if not empresa:
        for i in range(len(lines)):
            if "logo" in lines[i].lower():
                for k in range(i+1, len(lines)):
                    if is_valid(lines[k]) and not any(x in lines[k].lower() for x in IGNORE_LINES):
                        empresa = lines[k]
                        # Cargo suele estar en la siguiente línea válida después de empresa
                        for m in range(k+1, len(lines)):
                            if is_valid(lines[m]):
                                cargo = lines[m]
                                break
                        break
                break
    # 3. Fallback: primer línea válida que no sea acción/ubicación
    if not empresa:
        for line in lines:
            if is_valid(line) and not any(x in line.lower() for x in IGNORE_LINES):
                empresa = line
                break
    if not cargo:
        # Busca el primer cargo por heurística
        for line in lines:
            if is_valid(line) and any(x in line.lower() for x in ["analista","business","developer","specialist","coordinator","manager","consultant","support","administration","data management","power bi","bi","desarrollador","funcional","calypso","back office","freight","administrador","procesos comerciales"]):
                cargo = line
                break
    # Limpieza final
    cargo = cargo.replace("·", "").strip()
    empresa = empresa.replace("·", "").strip()
    return cargo, empresa

def extract_requerimientos(text):
    requerimientos = []
    req_match = re.findall(r'(?:Requerimientos|Requirements|Responsabilidades Clave|Key Responsibilities|Qualifications|Responsabilidades|Responsabilidades principales|What We’re Looking For|Lo que buscamos en ti|Condiciones de trabajo|Skills|Required Skills|Responsabilidades:|Requisitos:|Requisitos y conocimientos del Rol:|Qué buscamos en ti:|Lo que harás:|What You’ll Do:)\s*[\n:]*([\s\S]*?)(?:\n{2,}|$)', text, re.IGNORECASE)
    for req_block in req_match:
        for line in req_block.splitlines():
            line = line.strip('-• \n\t')
            if line and len(line) > 4 and is_valid(line):
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