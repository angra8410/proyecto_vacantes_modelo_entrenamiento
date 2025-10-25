import os
import yaml
import json
from pathlib import Path

def yaml_folder_to_jsonl(yaml_dir, out_jsonl):
    yaml_dir = Path(yaml_dir)
    files = list(yaml_dir.glob("*.yaml"))
    with open(out_jsonl, "w", encoding="utf-8") as fout:
        for f in files:
            with open(f, "r", encoding="utf-8") as fin:
                content = fin.read()
                try:
                    data = yaml.safe_load(content)
                except Exception as e:
                    print(f"Error en archivo {f}: {e}")
                    continue
                text = ""
                # Puedes ajustar esta lógica para concatenar los campos que quieras en "text"
                # Por ejemplo, unir la descripción y los requerimientos
                descripcion = data.get("descripcion", "")
                requerimientos = data.get("requerimientos", [])
                text = descripcion
                if requerimientos:
                    if isinstance(requerimientos, list):
                        text += "\n" + "\n".join(requerimientos)
                    else:
                        text += "\n" + str(requerimientos)
                obj = {
                    "text": text.strip(),
                    "yaml": content.strip()
                }
                fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"Generado: {out_jsonl} con {len(files)} vacantes.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python scripts/yaml_to_training_data_jsonl.py vacantes_yaml data/training_data.jsonl")
        sys.exit(1)
    yaml_folder_to_jsonl(sys.argv[1], sys.argv[2])