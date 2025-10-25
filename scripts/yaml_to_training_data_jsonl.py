import os
import yaml
import json
from pathlib import Path

def yaml_folder_to_jsonl(yaml_dir, out_jsonl):
    yaml_dir = Path(yaml_dir)
    files = list(yaml_dir.glob("*.yaml"))
    vacantes_ok = 0
    vacantes_err = 0
    with open(out_jsonl, "w", encoding="utf-8") as fout:
        for f in files:
            with open(f, "r", encoding="utf-8") as fin:
                content = fin.read()
                try:
                    data = yaml.safe_load(content)
                except Exception as e:
                    print(f"Error en archivo {f}: {e}")
                    vacantes_err += 1
                    continue
                if not isinstance(data, dict):
                    print(f"Archivo {f} no es YAML válido tipo dict, se ignora.")
                    vacantes_err += 1
                    continue
                text = ""
                descripcion = data.get("descripcion", "")
                requerimientos = data.get("requerimientos", [])
                text = descripcion
                if requerimientos:
                    if isinstance(requerimientos, list):
                        text += "\n" + "\n".join(map(str, requerimientos))
                    else:
                        text += "\n" + str(requerimientos)
                obj = {
                    "text": text.strip(),
                    "yaml": content.strip()
                }
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                vacantes_ok += 1
    print(f"Generado: {out_jsonl} con {vacantes_ok} vacantes válidas. {vacantes_err} archivos ignorados por error.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python scripts/yaml_to_training_data_jsonl.py vacantes_yaml data/training_data.jsonl")
        sys.exit(1)
    yaml_folder_to_jsonl(sys.argv[1], sys.argv[2])