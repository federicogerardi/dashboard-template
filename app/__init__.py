from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import Config
from sqlalchemy import inspect
from app.utils.errors import register_error_handlers
from app.utils.logger import setup_logger
from app.utils.limiter import init_limiter, limiter
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(id):
    from app.models.user import User
    return User.query.get(int(id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inizializzazione delle estensioni
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
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
    
    return app
