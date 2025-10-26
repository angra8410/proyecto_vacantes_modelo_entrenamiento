import os
from github import Github
import subprocess

SRC_DIR = "vacantes_yaml_manual"
DEST_REPO = "angra8410/aplicaciones_laborales"
DEST_PATH = "to_process"
BRANCH = "main"
TOKEN = os.getenv("GH_TOKEN")

def get_modified_or_added_yaml_files():
    # Obtiene archivos modificados o agregados en el último commit
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD"],
        capture_output=True, text=True
    )
    files = []
    for line in result.stdout.splitlines():
        status, fname = line.split('\t', 1)
        # status: 'A' (added) o 'M' (modified)
        if fname.startswith(f"{SRC_DIR}/") and fname.endswith(".yaml") and status in ("A", "M"):
            files.append(fname)
    return files

yaml_files = get_modified_or_added_yaml_files()
if not yaml_files:
    print("No hay archivos YAML agregados/modificados en el último commit.")
    exit(0)

g = Github(TOKEN)
repo = g.get_repo(DEST_REPO)

for rel_fname in yaml_files:
    fname = os.path.basename(rel_fname)
    path_src = os.path.join(SRC_DIR, fname)
    path_dest = os.path.join(DEST_PATH, fname)
    if not os.path.exists(path_src):
        print(f"{path_src} no existe, lo salto.")
        continue
    with open(path_src, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        try:
            f_dest = repo.get_contents(path_dest, ref=BRANCH)
            repo.update_file(f_dest.path, f"Update {fname} from modelo_entrenamiento", content, f_dest.sha, branch=BRANCH)
            print(f"Archivo {fname} actualizado en {DEST_REPO}/to_process/")
        except Exception:
            repo.create_file(path_dest, f"Add {fname} from modelo_entrenamiento", content, branch=BRANCH)
            print(f"Archivo {fname} creado en {DEST_REPO}/to_process/")
    except Exception as e:
        print(f"Error procesando {fname}: {e}")