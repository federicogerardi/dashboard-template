from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from app.models.user import User
from app.utils.security import validate_username

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username obbligatorio"),
        Length(min=3, max=64, message="L'username deve essere tra 3 e 64 caratteri")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password obbligatoria")
    ])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username obbligatorio"),
        Length(min=3, max=64, message="L'username deve essere tra 3 e 64 caratteri"),
        Regexp(r'^[a-z0-9_]+$', message="Username può contenere solo lettere minuscole, numeri e underscore")
    ])
    email = EmailField('Email', validators=[
        DataRequired(message="Email obbligatoria"),
        Email(message="Inserisci un indirizzo email valido")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password obbligatoria"),
        Length(min=12, message="La password deve essere di almeno 12 caratteri"),
        Regexp(
            r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$',
            message="La password deve contenere almeno: una lettera maiuscola, "
                   "una minuscola, un numero e un carattere speciale (@$!%*?&)"
        )
    ])
    password2 = PasswordField('Ripeti Password', validators=[
        DataRequired(message="Ripeti la password"),
        EqualTo('password', message="Le password devono coincidere")
    ])
    submit = SubmitField('Registrati')

    def validate_username(self, username):
        # Validazione esistenza username
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError('Username già in uso.')
            
        # Sanitizzazione e validazione formato
        valid_username = validate_username(username.data)
        if not valid_username:
            raise ValidationError('Username non valido: usa solo lettere minuscole, numeri e underscore')
        
        # Forza il valore sanitizzato
        username.data = valid_username

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email già registrata.') 