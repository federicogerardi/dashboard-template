from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect
from app.config import config
from app.utils.errors import register_error_handlers
from app.utils.logger import setup_logger
from app.utils.limiter import init_limiter, limiter

# Inizializzazione delle estensioni
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='default'):
    """Factory pattern per la creazione dell'app"""
    app = Flask(__name__)
    
    # Carica la configurazione in base all'ambiente
    app.config.from_object(config[config_name])
    
    # Inizializzazione delle estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configurazione login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Effettua il login per accedere a questa pagina.'
    login_manager.login_message_category = 'warning'
    
    # Setup sicurezza e logging
    setup_logger(app)
    register_error_handlers(app)
    init_limiter(app)
    
    with app.app_context():
        # Importa qui i modelli per assicurarti che siano caricati
        from app.models.user import User
        
        # Registrazione dei blueprint
        from app.controllers.routes import main
        from app.controllers.auth import auth
        
        app.register_blueprint(main)
        app.register_blueprint(auth)
        
        # Crea tutte le tabelle se non esistono
        db.create_all()
        
        # Verifica se le tabelle sono state create
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'user' not in tables:
            app.logger.error("ATTENZIONE: La tabella 'user' non è stata creata correttamente!")
        else:
            app.logger.info("Database inizializzato con successo!")
            
        # Registra funzioni di utilità nei template
        register_template_utils(app)
    
    return app

def register_template_utils(app):
    """Registra funzioni di utilità per i template"""
    @app.template_filter('datetime')
    def format_datetime(value, format='%d/%m/%Y %H:%M'):
        if value:
            return value.strftime(format)
        return ''

def setup_logger(app):
    """Configura il logging dell'applicazione"""
    if not app.debug and not app.testing:
        # Qui puoi aggiungere la configurazione del logging per produzione
        pass

def init_limiter(app):
    """Inizializza il rate limiting"""
    if app.config.get('REDIS_URL'):
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        return limiter
