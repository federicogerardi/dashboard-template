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

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            log_security_event(
                'LOGIN_FAILED',
                form.username.data,
                request.remote_addr,
                'Invalid credentials'
            )
            flash('Username o password non validi')
            return redirect(url_for('auth.login'))
            
        login_user(user)
        log_security_event(
            'LOGIN_SUCCESS',
            user.id,
            request.remote_addr,
            'Successful login'
        )
        return redirect(url_for('main.dashboard'))
        
    return render_template('login.html', form=form)

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
    if form.validate_on_submit():
        is_first_user = User.query.first() is None
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=UserRole.ADMIN.value if is_first_user else UserRole.USER.value
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrazione completata con successo!')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

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