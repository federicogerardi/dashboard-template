from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.core.models.user import User, UserRole
from app.core.forms import LoginForm, RegistrationForm
from app import db
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone
from app.core.utils.limiter import limiter
from app.core.utils.logger import log_security_event
from app.core.utils.security import sanitize_input
from sqlalchemy.exc import SQLAlchemyError

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and user.check_password(form.password.data):
            # Aggiorna il timestamp di ultimo login e il contatore
            user.last_login = datetime.utcnow()
            user.login_count += 1  # Incrementa anche il contatore degli accessi
            db.session.commit()
            
            # Effettua il login
            login_user(user, remember=form.remember_me.data)
            
            # Redirect alla pagina richiesta o alla dashboard
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.dashboard'))
            
        flash('Username o password non validi', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    # Non aggiorniamo last_login al logout
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    # Aggiungiamo debug per la validazione
    if request.method == 'POST':
        current_app.logger.debug(f"Form data: {request.form}")
        current_app.logger.debug(f"Form validation: {form.validate()}")
        if form.errors:
            current_app.logger.debug(f"Form errors: {form.errors}")
    
    if form.validate_on_submit():
        # Sanitizzazione input
        username = sanitize_input(form.username.data.lower())
        email = sanitize_input(form.email.data.lower(), allow_email=True)
        
        current_app.logger.info(f"Tentativo registrazione per username: {username}")
        
        is_first_user = User.query.first() is None
        current_app.logger.info(f"Is first user? {is_first_user}")
        
        user = User(
            username=username,
            email=email,
            role=UserRole.ADMIN.value if is_first_user else UserRole.USER.value
        )
        current_app.logger.info(f"User role set to: {user.role}")
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"Utente {user.username} registrato con successo")
            flash('Registrazione completata con successo!')
            return redirect(url_for('auth.login'))
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error: {str(e)}")
            db.session.rollback()
            flash('Errore del database. Riprova più tardi.', 'error')
    
    return render_template('pdashboard/auth/register.html', form=form)

@auth.before_request
def before_request():
    if current_user.is_authenticated:
        last_activity = session.get('last_activity')
        if last_activity:
            # Convertiamo il datetime in UTC se non lo è già
            if not last_activity.tzinfo:
                last_activity = last_activity.replace(tzinfo=timezone.utc)
            
            if datetime.now(timezone.utc) - last_activity > timedelta(minutes=30):
                logout_user()
                session.pop('last_activity', None)
                flash('Sessione scaduta per inattività.')
                return redirect(url_for('auth.login'))
        
        session['last_activity'] = datetime.now(timezone.utc)