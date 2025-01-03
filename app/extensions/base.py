from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class NavigationItem:
    """Rappresenta una voce nel menu di navigazione"""
    name: str
    icon: str
    url: str
    permission: str = None
    children: List['NavigationItem'] = None

    def __init__(self, name, icon, url, permission=None, subitems=None):
        self.name = name
        self.icon = icon
        self.url = url
        self.permission = permission
        self.subitems = subitems or []  # Se non specificato, lista vuota

class DashboardExtension:
    """Classe base per le estensioni della dashboard"""
    
    def __init__(self, name: str):
        self.name = name
        self.blueprint = None
        self.index_priority = 0  # Priorità default per l'index
        self.provides_index = False  # Flag per indicare se fornisce un index
        self.is_active = True  # Nuovo attributo per lo stato
    
    def init_app(self, app):
        """Inizializza l'estensione con l'app Flask"""
        if self.blueprint:
            app.register_blueprint(self.blueprint)
    
    def get_navigation_items(self) -> List[NavigationItem]:
        """Restituisce le voci di navigazione per la sidebar"""
        return []
    
    def get_admin_views(self) -> List[Dict[str, Any]]:
        """Restituisce le estensioni del pannello admin"""
        return [] 
    
    def get_index_template(self) -> str:
        """Restituisce il template da usare per l'index"""
        if self.provides_index:
            # Usa il namespace del blueprint per trovare il template
            return f"{self.blueprint.name}/index.html"
        return None
    
    def get_index_context(self) -> dict:
        """Restituisce il contesto da passare al template dell'index"""
        return {} 
    
    def toggle_status(self):
        """Attiva/disattiva il plugin"""
        self.is_active = not self.is_active
        return self.is_active 