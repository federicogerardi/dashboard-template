import json
import os
from flask import current_app

def save_plugin_status(plugin_name: str, status: bool):
    """Salva lo stato del plugin in un file JSON"""
    config_file = os.path.join(current_app.instance_path, 'plugin_status.json')
    
    # Assicurati che la directory instance esista
    os.makedirs(current_app.instance_path, exist_ok=True)
    
    try:
        # Leggi la configurazione esistente o crea un nuovo dict
        config = {}
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        # Aggiorna lo stato del plugin
        config[plugin_name] = status
        
        # Salva la configurazione aggiornata
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
            
        current_app.logger.info(f"Stato del plugin {plugin_name} salvato con successo")
        
    except Exception as e:
        current_app.logger.error(f"Errore nel salvataggio stato plugin: {e}")
        raise

def load_plugin_status():
    """Carica gli stati dei plugin dal file JSON"""
    config_file = os.path.join(current_app.instance_path, 'plugin_status.json')
    
    if not os.path.exists(config_file):
        return {}
        
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        current_app.logger.error(f"Errore nel caricamento stati plugin: {e}")
        return {} 