import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

class BaseConfig:
    """Configurazione base comune a tutti gli ambienti"""
    
    # Validazione variabili d'ambiente critiche
    @staticmethod
    def validate_config():
        required_vars = ['SECRET_KEY', 'DATABASE_URL']
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing and os.getenv('FLASK_ENV') == 'production':
            raise ValueError(f"Variabili d'ambiente mancanti: {', '.join(missing)}")
    
    # Configurazioni base
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-molto-segreta'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurazioni di sicurezza
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_REFRESH_EACH_REQUEST = True
    
    # Security Headers come nella configurazione originale
    SECURITY_HEADERS = {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' cdn.jsdelivr.net;",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }

class DevelopmentConfig(BaseConfig):
    """Configurazione per sviluppo"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'dev.db')
    REDIS_URL = 'redis://localhost:6379/0'

class TestingConfig(BaseConfig):
    """Configurazione per testing"""
    TESTING = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'test.db')
    WTF_CSRF_ENABLED = False

class ProductionConfig(BaseConfig):
    """Configurazione per produzione"""
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    REDIS_URL = os.environ.get('REDIS_URL')

    def __init__(self):
        super().validate_config()

# Dizionario per selezionare la configurazione
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
