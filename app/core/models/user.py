from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    USER = 'user'
    EDITOR = 'editor'
    ADMIN = 'admin'

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = (
        db.Index('idx_user_username', 'username', unique=True),
        db.Index('idx_user_email', 'email', unique=True),
        db.Index('idx_user_created_at', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=UserRole.USER.value)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=None)
    login_count = db.Column(db.Integer, default=0)
    theme_preference = db.Column(db.String(20), default='light')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
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
