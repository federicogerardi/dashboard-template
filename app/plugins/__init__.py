from importlib import import_module
from pathlib import Path
from flask import Blueprint
from typing import List, Dict
from app.extensions.base import DashboardExtension
from app.core.utils.plugin_manager import load_plugin_status

def discover_plugins() -> List[DashboardExtension]:
    """Scopre automaticamente i plugin installati"""
    plugins = []
    plugins_dir = Path(__file__).parent
    
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
            try:
                # Importa il modulo principale del plugin
                module = import_module(f'app.plugins.{plugin_dir.name}')
                if hasattr(module, 'plugin'):
                    plugins.append(module.plugin)
            except Exception as e:
                print(f"Errore nel caricamento del plugin {plugin_dir.name}: {e}")
    
    return plugins

def init_plugins(app):
    """Inizializza tutti i plugin trovati"""
    plugins = discover_plugins()
    plugin_status = load_plugin_status()
    
    for plugin in plugins:
        try:
            # Carica lo stato salvato o usa il default (True)
            plugin.is_active = plugin_status.get(plugin.name, True)
            
            if plugin.is_active:
                plugin.init_app(app)
                app.logger.info(f"Plugin {plugin.name} inizializzato con successo")
            else:
                app.logger.info(f"Plugin {plugin.name} disattivato")
                
        except Exception as e:
            app.logger.error(f"Errore nell'inizializzazione del plugin {plugin.name}: {e}")
