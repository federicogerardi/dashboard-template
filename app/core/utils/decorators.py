from functools import wraps
from flask import abort, current_app, request
from flask_login import current_user

def role_required(role):
    """Decorator per verificare il ruolo dell'utente"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def plugin_required():
    """Decorator per verificare lo stato del plugin"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Estrai il nome del blueprint dalla richiesta
            blueprint_name = request.blueprint
            
            # Trova il plugin corrispondente
            plugin = next(
                (p for p in current_app.plugins if p.blueprint and p.blueprint.name == blueprint_name),
                None
            )
            
            # Verifica se il plugin esiste ed è attivo
            if not plugin or not plugin.is_active:
                current_app.logger.warning(f"Tentativo di accesso a plugin disattivato: {blueprint_name}")
                abort(403, description="Plugin non disponibile")
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator 