from flask import Blueprint
from app.extensions.base import DashboardExtension, NavigationItem

class Prova_nuovoPlugin(DashboardExtension):
    def __init__(self):
        super().__init__('Prova_nuovo Plugin')
        self.blueprint = Blueprint(
            'prova_nuovo',
            __name__,
            template_folder='templates',
            static_folder='static',
            url_prefix='/prova_nuovo'
        )
        
        # Registra le routes
        from . import routes
        self.blueprint.add_url_rule('/', 'index', routes.index)
    
    def get_navigation_items(self):
        return [
            NavigationItem(
                name='Prova_nuovo Plugin',
                icon='fas fa-puzzle-piece',
                url='/prova_nuovo',
                permission='user'
            )
        ]

# Istanza del plugin che verrà caricata automaticamente
plugin = Prova_nuovoPlugin()
