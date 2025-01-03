import sys
from pathlib import Path

def update_requirements():
    """Aggiorna requirements.txt mantenendo le dipendenze personalizzate"""
    req_file = Path('requirements.txt')
    if not req_file.exists():
        print("Creating new requirements.txt...")
        with open(req_file, 'w') as f:
            f.write('-r requirements-base.txt\n\n# Add your custom dependencies here\n')
        return

    # Leggi il file esistente
    with open(req_file) as f:
        lines = f.readlines()

    # Separa le dipendenze base da quelle personalizzate
    custom_deps = []
    for line in lines:
        if not line.startswith('-r') and line.strip():
            custom_deps.append(line)

    # Ricrea il file
    with open(req_file, 'w') as f:
        f.write('-r requirements-base.txt\n\n')
        if custom_deps:
            f.write('# Custom dependencies\n')
            f.writelines(custom_deps)

if __name__ == '__main__':
    update_requirements() 