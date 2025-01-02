from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models.user import User
from app.utils.security import validate_username

class LoginForm(FlaskForm):
    """Form per il login"""
    username = StringField('Username', validators=[
        DataRequired(message="Username obbligatorio"),
        Length(min=3, max=64, message="Username non valido")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password obbligatoria")
    ])
    remember_me = BooleanField('Ricordami')
    submit = SubmitField('Login')

    def validate_username(self, username):
        """Validazione aggiuntiva username"""
        if not username.data.isalnum():
            raise ValidationError('Username può contenere solo lettere e numeri')
        username.data = username.data.lower()

class RegistrationForm(FlaskForm):
    """Form per la registrazione"""
    username = StringField('Username', validators=[
        DataRequired(message="Username obbligatorio"),
        Length(min=3, max=64, message="L'username deve essere tra 3 e 64 caratteri")
    ])
    
    email = EmailField('Email', validators=[
        DataRequired(message="Email obbligatoria"),
        Email(message="Inserisci un indirizzo email valido")
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message="Password obbligatoria"),
        Length(min=12, message="La password deve essere di almeno 12 caratteri")
    ])
    
    password2 = PasswordField('Ripeti Password', validators=[
        DataRequired(message="Ripeti la password"),
        EqualTo('password', message="Le password devono coincidere")
    ])
    
    submit = SubmitField('Registrati')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError('Username già in uso.')
        
        if not username.data.isalnum():
            raise ValidationError('Username può contenere solo lettere e numeri.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError('Email già registrata.')

    def validate_password(self, password):
        """Validazione custom per la password"""
        if len(password.data) < 12:
            raise ValidationError('La password deve essere di almeno 12 caratteri')
        
        if not any(c.isupper() for c in password.data):
            raise ValidationError('La password deve contenere almeno una lettera maiuscola')
        
        if not any(c.islower() for c in password.data):
            raise ValidationError('La password deve contenere almeno una lettera minuscola')
        
        if not any(c.isdigit() for c in password.data):
            raise ValidationError('La password deve contenere almeno un numero')
        
        if not any(c in '@$!%*?&' for c in password.data):
            raise ValidationError('La password deve contenere almeno un carattere speciale (@$!%*?&)')