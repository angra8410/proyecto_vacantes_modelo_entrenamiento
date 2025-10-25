import yaml
import glob

def compare_yaml_folders(auto_dir, manual_dir):
    auto_files = glob.glob(f"{auto_dir}/*.yaml")
    manual_files = glob.glob(f"{manual_dir}/*.yaml")
    auto_map = {os.path.basename(f): f for f in auto_files}
    manual_map = {os.path.basename(f): f for f in manual_files}
    for fname in sorted(auto_map.keys()):
        if fname in manual_map:
            with open(auto_map[fname], encoding="utf-8") as fa, open(manual_map[fname], encoding="utf-8") as fm:
                auto_yaml = yaml.safe_load(fa)
                manual_yaml = yaml.safe_load(fm)
                for field in ["cargo", "empresa", "modalidad"]:
                    if auto_yaml.get(field) != manual_yaml.get(field):
                        print(f"{fname}: CAMPO '{field}' DIFERENTE\n  AUTO: {auto_yaml.get(field)}\n  MANUAL: {manual_yaml.get(field)}\n")