import json
import os
from pathlib import Path

def get_plugin_status_file():
    """Restituisce il percorso del file di stato dei plugin"""
    config_dir = Path('instance')
    config_dir.mkdir(exist_ok=True)
    return config_dir / 'plugin_status.json'

def load_plugin_status():
    """Carica lo stato dei plugin dal file di configurazione"""
    status_file = get_plugin_status_file()
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    return {}

def save_plugin_status(status):
    """Salva lo stato dei plugin nel file di configurazione"""
    status_file = get_plugin_status_file()
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=4) 