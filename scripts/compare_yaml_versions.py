import yaml
import glob
import os

def compare_yaml_folders(auto_dir, manual_dir):
    auto_files = glob.glob(f"{auto_dir}/*.yaml")
    manual_files = glob.glob(f"{manual_dir}/*.yaml")
    auto_map = {os.path.basename(f): f for f in auto_files}
    manual_map = {os.path.basename(f): f for f in manual_files}
    all_files = set(auto_map) | set(manual_map)
    count_diffs = 0
    count_same = 0
    count_missing = 0

    for fname in sorted(all_files):
        if fname in auto_map and fname in manual_map:
            with open(auto_map[fname], encoding="utf-8") as fa, open(manual_map[fname], encoding="utf-8") as fm:
                auto_yaml = yaml.safe_load(fa)
                manual_yaml = yaml.safe_load(fm)
                diffs = []
                for field in ["cargo", "empresa", "modalidad"]:
                    if auto_yaml.get(field) != manual_yaml.get(field):
                        diffs.append(field)
                if diffs:
                    print(f"{fname}:")
                    for field in diffs:
                        print(f"  CAMPO '{field}' DIFERENTE")
                        print(f"    AUTO:   {auto_yaml.get(field)}")
                        print(f"    MANUAL: {manual_yaml.get(field)}")
                    print()
                    count_diffs += 1
                else:
                    count_same += 1
        elif fname in auto_map:
            print(f"{fname}: Solo en carpeta automática (no corregido)")
            count_missing += 1
        elif fname in manual_map:
            print(f"{fname}: Solo en carpeta manual (nuevo o renombrado)")
            count_missing += 1

    print(f"\nResumen:")
    print(f"Diferencias encontradas en {count_diffs} archivos.")
    print(f"Archivos idénticos en campos clave: {count_same}.")
    print(f"Archivos solo en una carpeta: {count_missing}.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python scripts/compare_yaml_versions.py vacantes_yaml vacantes_yaml_manual")
        sys.exit(1)
    compare_yaml_folders(sys.argv[1], sys.argv[2])