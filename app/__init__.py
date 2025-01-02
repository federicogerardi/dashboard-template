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
import os
from dotenv import load_dotenv

# Ottieni il percorso assoluto della directory dell'app
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(os.path.dirname(basedir), '.env')

# Carica variabili d'ambiente PRIMA di tutto
load_dotenv(env_path, override=True)

# Debug per verificare il caricamento
print("\nVariabili d'ambiente dopo load_dotenv:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"APP_ENV: {os.getenv('APP_ENV')}")

# Inizializzazione delle estensioni
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name=None):
    """Factory pattern per la creazione dell'app"""
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.getenv('APP_ENV', 'development')
    
    print(f"\nPrima di from_object:")
    print(f"config_name: {config_name}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    
    # Crea un'istanza della configurazione
    app_config = config[config_name]()
    app.config.from_object(app_config)
    
    print(f"\nDopo from_object:")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Debug della configurazione
    app.logger.info(f"Configurazione caricata: {config_name}")
    app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
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
        
        # Verifica se le tabelle sono state create
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'user' not in tables:
            app.logger.warning("La tabella 'user' non esiste - verrà creata dalle migrazioni")
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
