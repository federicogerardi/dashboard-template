from importlib import import_module
from pathlib import Path
from flask import Blueprint
from app.core.utils.decorators import plugin_required
from app.core.utils.plugin_manager import load_plugin_status

def discover_plugins():
    """Scopre e carica tutti i plugin disponibili"""
    plugins = []
    plugins_dir = Path(__file__).parent
    
    for plugin_dir in plugins_dir.iterdir():
        if plugin_dir.is_dir() and not plugin_dir.name.startswith('__'):
            try:
                # Forza il reload del modulo in debug mode
                module = import_module(f'app.plugins.{plugin_dir.name}')
                if hasattr(module, 'plugin'):
                    plugins.append(module.plugin)
            except Exception as e:
                print(f"Errore nel caricamento del plugin {plugin_dir.name}: {e}")
    
    return plugins

def init_plugins(app):
    """Inizializza tutti i plugin trovati"""
    if not hasattr(app, '_plugin_initialized'):
        app._plugin_initialized = False
        
    if app._plugin_initialized and not app.debug:
        return getattr(app, 'plugins', [])
        
    plugins = discover_plugins()
    plugin_status = load_plugin_status()
    
    for plugin in plugins:
        try:
            # Reset del blueprint se esiste già
            if hasattr(plugin, 'blueprint') and plugin.blueprint:
                if plugin.blueprint.name in app.blueprints:
                    app.blueprints.pop(plugin.blueprint.name)
                    
            # Carica lo stato salvato o usa il default (True)
            plugin.is_active = plugin_status.get(plugin.name, True)
            
            if plugin.blueprint:
                # Applica il decorator plugin_required a tutte le route
                for endpoint, view_func in plugin.blueprint.view_functions.items():
                    decorated_view = plugin_required()(view_func)
                    plugin.blueprint.view_functions[endpoint] = decorated_view
                
                if plugin.is_active:
                    app.register_blueprint(plugin.blueprint)
                    app.logger.info(f"Plugin {plugin.name} inizializzato e attivato")
                else:
                    app.logger.info(f"Plugin {plugin.name} inizializzato ma disattivato")
                    
        except Exception as e:
            app.logger.error(f"Errore nell'inizializzazione del plugin {plugin.name}: {e}")
    
    app.plugins = plugins
    app._plugin_initialized = True
    return plugins
