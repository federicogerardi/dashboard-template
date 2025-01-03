from flask import Blueprint
from app.extensions.base import DashboardExtension, NavigationItem

class DemoPlugin(DashboardExtension):
    def __init__(self):
        super().__init__('Demo Plugin')
        self.blueprint = Blueprint(
            'demo_plugin',
            __name__,
            template_folder='templates',
            static_folder='static',
            url_prefix='/demo'
        )
        self.provides_index = False  # Disattiva la gestione dell'index
        self.index_priority = 10      # Imposta la priorità
        
        # Registra le routes
        from . import routes
        self.blueprint.add_url_rule('/', 'index', routes.index)
        self.blueprint.add_url_rule('/chart', 'chart', routes.chart)
        self.blueprint.add_url_rule('/stats', 'stats', routes.stats)
        self.blueprint.add_url_rule('/installation', 'installation', routes.installation)
    
    def get_navigation_items(self):
        return [
            NavigationItem(
                name='Demo Plugin',
                icon='fas fa-flask',
                url='/demo',
                permission='user',
                subitems=[
                    NavigationItem(
                        name='Statistiche',
                        icon='fas fa-chart-line',
                        url='/demo/stats'
                    ),
                    NavigationItem(
                        name='Installazione',
                        icon='fas fa-book',
                        url='/demo/installation'
                    )
                ]
            )
        ]

# Istanza del plugin che verrà caricata automaticamente
plugin = DemoPlugin()
