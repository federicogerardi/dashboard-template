from functools import wraps
from flask import request, abort
import re
from hmac import compare_digest
import html
import unicodedata
import os
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta

def sanitize_input(text, allow_email=False):
    """Sanitizza input per prevenire XSS e injection"""
    if not text:
        return text
        
    # Normalizza unicode
    text = unicodedata.normalize('NFKC', str(text))
    
    # Rimuove HTML
    text = html.escape(text)
    
    if allow_email:
        # Per email, permetti caratteri speciali necessari
        text = re.sub(r'[^\w\s@.-]', '', text)
    else:
        # Per altri input, rimuovi caratteri speciali
        text = re.sub(r'[^\w\s-]', '', text)
    
    # Normalizza spazi
    text = ' '.join(text.split())
    
    return text.strip()

def sanitize_filename(filename):
    """Sanitizza nomi file"""
    # Rimuovi estensione
    name, ext = os.path.splitext(filename)
    
    # Sanitizza nome file
    name = re.sub(r'[^\w\s-]', '', name)
    name = name.strip().lower()
    name = re.sub(r'[-\s]+', '-', name)
    
    # Riattacca estensione sicura
    allowed_extensions = {'.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif'}
    ext = ext.lower()
    if ext not in allowed_extensions:
        ext = '.txt'
        
    return name + ext

def validate_json_request(required_fields):
    """Valida richieste JSON"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                abort(400, "Richiesta deve essere JSON")
            data = request.get_json()
            for field in required_fields:
                if field not in data:
                    abort(400, f"Campo mancante: {field}")
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_username(username):
    """Valida e sanitizza username"""
    if not username:
        return None
        
    # Rimuove HTML e spazi iniziali/finali
    username = sanitize_input(username)
    
    # Converte in minuscolo
    username = username.lower()
    
    # Verifica caratteri permessi (solo lettere, numeri e underscore)
    if not re.match(r'^[a-z0-9_]+$', username):
        return None
        
    return username

def validate_password(password: str) -> tuple[bool, str]:
    """Valida la password secondo i criteri di sicurezza.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 12:
        return False, 'La password deve essere di almeno 12 caratteri'
    
    if not any(c.isupper() for c in password):
        return False, 'La password deve contenere almeno una lettera maiuscola'
    
    if not any(c.islower() for c in password):
        return False, 'La password deve contenere almeno una lettera minuscola'
    
    if not any(c.isdigit() for c in password):
        return False, 'La password deve contenere almeno un numero'
    
    if not any(c in '@$!%*?&' for c in password):
        return False, 'La password deve contenere almeno un carattere speciale (@$!%*?&)'
    
    return True, ''

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    """Crea un JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    
    # Utilizzo di PyJWT invece di python-jose
    encoded_jwt = jwt.encode(
        to_encode, 
        current_app.config['SECRET_KEY'], 
        algorithm="HS256"
    )
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decodifica un JWT token"""
    try:
        # Utilizzo di PyJWT invece di python-jose
        payload = jwt.decode(
            token, 
            current_app.config['SECRET_KEY'], 
            algorithms=["HS256"]
        )
        return payload
    except InvalidTokenError:
        return None
