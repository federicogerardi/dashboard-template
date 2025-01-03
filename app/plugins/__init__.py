from importlib import import_module
from pathlib import Path
from flask import Blueprint
from typing import List, Dict
from app.extensions.base import DashboardExtension

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
    
    for plugin in plugins:
        try:
            plugin.init_app(app)
            app.logger.info(f"Plugin {plugin.name} inizializzato con successo")
        except Exception as e:
            app.logger.error(f"Errore nell'inizializzazione del plugin {plugin.name}: {e}")
