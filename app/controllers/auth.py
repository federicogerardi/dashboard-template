from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.forms import LoginForm, RegistrationForm
from app import db
from urllib.parse import urlparse
from app.models.user import UserRole
from datetime import datetime, timedelta, timezone
from app.utils.limiter import limiter
from app.utils.logger import log_security_event
from app.utils.security import sanitize_input

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user and user.check_password(form.password.data):
            # Incrementiamo il contatore qui, al login effettivo
            user.login_count += 1
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash('Username o password non validi', 'error')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    if 'last_activity' in session:
        session.pop('last_activity')
    flash('Logout effettuato con successo.')
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
        
        user = User(
            username=username,
            email=email,
            role=UserRole.ADMIN.value if is_first_user else UserRole.USER.value
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"Utente {user.username} registrato con successo")
            flash('Registrazione completata con successo!')
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f"Errore durante la registrazione: {str(e)}")
            db.session.rollback()
            flash('Errore durante la registrazione. Riprova più tardi.', 'error')
    
    return render_template('auth/register.html', form=form)

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