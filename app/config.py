import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class BaseConfig:
    """Configurazione base comune a tutti gli ambienti"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-molto-segreta'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300
    }

class DevelopmentConfig(BaseConfig):
    """Configurazione per sviluppo"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    def __init__(self):
        super().__init__()
        # Usa DATABASE_URL se impostato, altrimenti usa SQLite
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'instance', 'dev.db')

class TestingConfig(BaseConfig):
    """Configurazione per testing"""
    TESTING = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False

    def __init__(self):
        super().__init__()
        # Usa DATABASE_URL se impostato, altrimenti usa SQLite per i test
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'instance', 'test.db')

class ProductionConfig(BaseConfig):
    """Configurazione per produzione"""
    SESSION_COOKIE_SECURE = True
    REDIS_URL = os.environ.get('REDIS_URL')

    def __init__(self):
        super().__init__()
        if not os.environ.get('DATABASE_URL'):
            raise ValueError("DATABASE_URL non impostato in produzione")
        self.SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
