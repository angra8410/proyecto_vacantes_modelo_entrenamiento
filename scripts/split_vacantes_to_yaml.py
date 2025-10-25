import os

def split_vacantes(input_file, output_dir):
    with open(input_file, encoding='utf-8') as f:
        content = f.read()

    vacantes = content.split('---\n')
    for idx, vacante in enumerate(vacantes):
        vacante = vacante.strip()
        if not vacante:
            continue
        # Try to get cargo, empresa y fecha para nombre de archivo
        cargo = empresa = fecha = f'vacante_{idx+1}'
        for line in vacante.splitlines():
            if line.startswith('cargo:'):
                cargo = line.split(':',1)[1].strip().replace('"','').replace(' ','_')
            if line.startswith('empresa:'):
                empresa = line.split(':',1)[1].strip().replace('"','').replace(' ','_')
            if line.startswith('fecha:'):
                fecha = line.split(':',1)[1].strip().replace('"','')
        filename = f'{fecha}_{cargo}_{empresa}.yaml'
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as out:
            out.write(vacante)
        print(f'Escribiendo: {filepath}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Uso: python split_vacantes_to_yaml.py vacantes.txt carpeta_salida")
        sys.exit(1)
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)
    split_vacantes(input_file, output_dir)