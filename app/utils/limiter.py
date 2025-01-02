from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user
import redis
import os

limiter = Limiter(
    key_func=get_remote_address,
    strategy="fixed-window-elastic-expiry",
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    default_limits_deduct_when=lambda response: response.status_code < 400,
    default_limits_exempt_when=lambda: current_user.is_authenticated and current_user.is_admin()
)

def init_limiter(app):
    redis_url = app.config.get('REDIS_URL')
    
    if redis_url:
        try:
            limiter.storage_uri = redis_url
        except redis.ConnectionError:
            app.logger.warning(
                "Impossibile connettersi a Redis, uso storage in memoria"
            )
    else:
        app.logger.warning(
            "Rate limiter usa storage in memoria. "
            "Per produzione, configura REDIS_URL nelle variabili d'ambiente"
        )
    
    limiter.init_app(app)
    return limiter