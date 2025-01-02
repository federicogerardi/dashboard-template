from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if role == 'admin' and not current_user.is_admin():
                abort(403)
            if role == 'editor' and not current_user.is_editor():
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator 