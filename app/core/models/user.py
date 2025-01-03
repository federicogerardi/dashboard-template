from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    USER = 'user'
    EDITOR = 'editor'
    ADMIN = 'admin'

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = (
        db.Index('idx_user_username_email', 'username', 'email'),
        db.Index('idx_user_role', 'role'),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default=UserRole.USER.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=None)
    login_count = db.Column(db.Integer, default=0)
    theme_preference = db.Column(db.String(20), default='light')
    
    def set_password(self, password):
        """Imposta l'hash della password"""
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la password"""
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == UserRole.ADMIN.value
    
    def is_editor(self):
        return self.role == UserRole.EDITOR.value or self.role == UserRole.ADMIN.value
    
    def __repr__(self):
        return f'<User {self.username}>'

    def has_role(self, role):
        """Verifica se l'utente ha un determinato ruolo"""
        if role == 'user':
            return True  # Tutti gli utenti autenticati hanno il ruolo 'user'
        return self.role == role
