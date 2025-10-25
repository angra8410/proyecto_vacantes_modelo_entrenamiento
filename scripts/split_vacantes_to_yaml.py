import os
import re
from datetime import datetime

IGNORE_LINES = {
    "easy apply","save","share","show more options","logo","apply",
    "matches your job preferences","about the job","remote","full-time","contract",
    "hybrid","on-site","colombia","capital district","latin america","bogo",
    "promoted by hirer","actively reviewing applicants","over 100 applicants",
    "over 100 people clicked apply","your profile matches some required qualifications",
    "your profile is missing required qualifications","show match details","tailor my resume",
    "help me update my profile","create cover letter","beta","is this information helpful?",
    "people you can reach out to","meet the hiring team","message","show all",
    "job poster"
}
IGNORE_PATTERNS = [
    r"\d+\s+(applicants|people clicked apply)",
    r".*logo$",
    r".*·.*(remote|híbrido|presencial|colombia|latin america|capital district).*",
    r"^promoted by hirer$",
    r"^\s*$",
    r"^[A-Z][a-z]+\slogo$"
]

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

def is_valid(line):
    l = line.strip().lower()
    if l in IGNORE_LINES:
        return False
    for pat in IGNORE_PATTERNS:
        if re.match(pat, l):
            return False
    return bool(l)

def extract_cargo_empresa(text):
    lines = [l.strip() for l in text.splitlines()]
    lines_filtered = [l for l in lines if is_valid(l)]
    cargo, empresa = "", ""
    # 1. Busca el patrón "Empresa logo" seguido de la empresa real y luego el cargo principal
    for i in range(len(lines_filtered)-2):
        if "logo" in lines_filtered[i].lower() and is_valid(lines_filtered[i+1]) and is_valid(lines_filtered[i+2]):
            empresa_candidate = lines_filtered[i+1]
            cargo_candidate = lines_filtered[i+2]
            # Asegúrate que la empresa no sea "Job poster"
            if empresa_candidate.lower() != "job poster" and is_valid(empresa_candidate):
                empresa = empresa_candidate
                cargo = cargo_candidate
                break
    # 2. Busca "Cargo\nEmpresa · Ubicación"
    if not empresa or not cargo:
        for i in range(len(lines_filtered)-1):
            l1, l2 = lines_filtered[i], lines_filtered[i+1]
            if "·" in l2 and is_valid(l2):
                empresa_candidate = l2.split("·")[0].strip()
                if is_valid(empresa_candidate) and empresa_candidate.lower() != "job poster":
                    cargo = l1
                    empresa = empresa_candidate
                    break
    # 3. Fallback: primer línea válida no ubicación ni acción para empresa
    if not empresa:
        for line in lines_filtered:
            if is_valid(line) and line.lower() != "job poster":
                empresa = line
                break
    # 4. Fallback para cargo
    if not cargo:
        for line in lines_filtered:
            if is_valid(line) and any(x in line.lower() for x in [
                "analista","business","developer","specialist","coordinator","manager",
                "consultant","support","administration","data management","power bi","bi",
                "desarrollador","funcional","calypso","back office","freight","administrador",
                "procesos comerciales","analyst"]):
                cargo = line
                break
    cargo = cargo.replace("·", "").strip()
    empresa = empresa.replace("·", "").strip()
    # Si empresa es ubicación, ignora
    if empresa.lower() in IGNORE_LINES or not empresa or empresa == cargo:
        empresa = ""
    return cargo, empresa

def extract_requerimientos(text):
    requerimientos = []
    req_match = re.findall(
        r'(?:Requerimientos|Requirements|Responsabilidades Clave|Key Responsibilities|Qualifications|Responsabilidades|Responsabilidades principales|What We’re Looking For|Lo que buscamos en ti|Condiciones de trabajo|Skills|Required Skills|Responsabilidades:|Requisitos:|Requisitos y conocimientos del Rol:|Qué buscamos en ti:|Lo que harás:|What You’ll Do:)\s*[\n:]*([\s\S]*?)(?:\n{2,}|$)',
        text, re.IGNORECASE)
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