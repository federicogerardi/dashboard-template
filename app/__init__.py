from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect
from app.config import config
from app.core.utils.errors import register_error_handlers
from app.core.utils.logger import setup_logger
from app.core.utils.limiter import init_limiter, limiter
import os
from dotenv import load_dotenv
from app.plugins import init_plugins, discover_plugins

# Ottieni il percorso assoluto della directory dell'app
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(os.path.dirname(basedir), '.env')

# Carica variabili d'ambiente PRIMA di tutto
load_dotenv(env_path, override=True)

# Inizializzazione delle estensioni
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name=None):
    """Factory pattern per la creazione dell'app"""
    app = Flask(__name__)
    
    # Configurazione
    if config_name is None:
        config_name = os.getenv('APP_ENV', 'development')
    
    print("\nPrima di from_object:")
    print(f"config_name: {config_name}")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
    
    app.config.from_object(config[config_name])
    
    print("\nDopo from_object:")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.logger.info(f"Configurazione caricata: {config_name}")
    app.logger.info(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Inizializzazione delle estensioni con l'app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    init_limiter(app)
    
    # Configurazione login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Effettua il login per accedere a questa pagina.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(id):
        from app.core.models.user import User  # Updated import
        return User.query.get(int(id))
    
    with app.app_context():
        # Registrazione dei blueprint
        from app.core.controllers.routes import main  # Updated import
        from app.core.controllers.auth import auth    # Updated import
        
        app.register_blueprint(main)
        app.register_blueprint(auth)
        
        # Registrazione gestione errori
        register_error_handlers(app)
        
        # Setup logger
        setup_logger(app)
        
        # Verifica esistenza database
        if not os.path.exists(os.path.join(basedir, 'instance')):
            os.makedirs(os.path.join(basedir, 'instance'))
        
        # Inizializzazione database
        inspector = inspect(db.engine)
        if not inspector.has_table("user"):
            app.logger.info("Inizializzazione database...")
            db.create_all()
            from app.core.models.user import User, UserRole  # Updated import
            # Crea utente admin se non esiste
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', email='admin@example.com', role=UserRole.ADMIN)
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()
                app.logger.info("Database inizializzato con successo!")
        
        # Inizializza i plugin e rendili disponibili nel contesto dell'app
        app.plugins = discover_plugins()
        init_plugins(app)
        
        # Aggiungi current_app ai template globals
        @app.context_processor
        def inject_plugins():
            return {
                'plugins': current_app.plugins
            }
    
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
