import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from functools import wraps
from flask import request, current_app
from flask_login import current_user

def setup_logger(app):
    # Crea directory logs se non esiste
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # Logger applicazione
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    
    # Logger sicurezza
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=10240,
        backupCount=10
    )
    security_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    security_logger = logging.getLogger('security')
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.WARNING)
    
    # Logger accessi
    access_handler = RotatingFileHandler(
        'logs/access.log',
        maxBytes=10240,
        backupCount=10
    )
    access_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(message)s'
    ))
    access_logger = logging.getLogger('access')
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)

def log_security_event(event_type, user_id, ip_address, details):
    security_logger = logging.getLogger('security')
    security_logger.warning(
        f'Security Event: {event_type} | User: {user_id} | '
        f'IP: {ip_address} | Details: {details}'
    )

def log_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_logger = logging.getLogger('access')
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        access_logger.info(
            f'Access: {request.method} {request.path} | '
            f'User: {user_id} | IP: {request.remote_addr}'
        )
        return f(*args, **kwargs)
    return decorated_function
