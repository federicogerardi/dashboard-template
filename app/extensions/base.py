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

class DashboardExtension:
    """Classe base per le estensioni della dashboard"""
    
    def __init__(self, name: str):
        self.name = name
        self.blueprint = None
    
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