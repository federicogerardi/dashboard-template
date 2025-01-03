from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.core.models.user import User, UserRole
from app.core.utils.decorators import role_required
from app.core.utils.security import (
    sanitize_input, 
    validate_json_request, 
    validate_username
)
from app import db
from werkzeug.security import generate_password_hash
import os
from app.core.forms import RegistrationForm
from app.core.utils.plugin_manager import save_plugin_status, load_plugin_status
from app.plugins import init_plugins

# Creazione del blueprint con il nuovo namespace
main = Blueprint('main', __name__, url_prefix='')

@main.route('/')
def index():
    """Gestisce la visualizzazione dell'index page"""
    # Cerca il plugin preferito se configurato
    if current_app.config.get('PREFERRED_INDEX_PLUGIN'):
        preferred = next(
            (p for p in current_app.plugins 
             if p.name == current_app.config['PREFERRED_INDEX_PLUGIN']),
            None
        )
        if preferred and preferred.provides_index:
            current_app.logger.info(f"Usando index del plugin preferito: {preferred.name}")
            return render_template(
                preferred.get_index_template(),
                **preferred.get_index_context()
            )
    
    # Altrimenti cerca il plugin con priorità più alta
    index_plugins = [p for p in current_app.plugins if p.provides_index]
    if index_plugins:
        # Ordina per priorità (decrescente) e nome (crescente per parità)
        provider = sorted(
            index_plugins,
            key=lambda x: (-x.index_priority, x.name)
        )[0]
        current_app.logger.info(f"Usando index del plugin con priorità più alta: {provider.name}")
        return render_template(
            provider.get_index_template(),
            **provider.get_index_context()
        )
    
    # Fallback al template di default
    current_app.logger.info("Nessun plugin fornisce index, uso template default")
    return render_template(current_app.config['DEFAULT_INDEX_TEMPLATE'])

@main.route('/dashboard')
@login_required
def dashboard():
    # Inizializza i valori se non esistono
    if current_user.login_count is None:
        current_user.login_count = 0
    if current_user.created_at is None:
        current_user.created_at = datetime.utcnow()
    
    current_user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Calcola statistiche
    user_stats = {
        'logins': current_user.login_count,
        'days_active': (datetime.utcnow() - current_user.created_at).days
    }
    
    # Simula attività recenti (da implementare con veri dati)
    recent_activities = [
        {
            'icon': 'fa-sign-in-alt',
            'timestamp': datetime.utcnow().strftime('%H:%M'),
            'description': 'Accesso effettuato'
        }
    ]
    
    return render_template('pdashboard/dashboard.html',
                         user_stats=user_stats,
                         recent_activities=recent_activities)

@main.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    # Sanitizza eventuali parametri di query
    page = sanitize_input(request.args.get('page', '1'))
    try:
        page = int(page)
    except ValueError:
        page = 1
    
    # Recupera tutti gli utenti ordinati per ID
    users = User.query.order_by(User.id).all()
    
    # Calcola statistiche
    total_users = User.query.count()
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = User.query.filter(User.last_login >= seven_days_ago).count()
    new_users = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    # Ottieni informazioni sul database
    database_url = current_app.config['SQLALCHEMY_DATABASE_URI']
    app_env = os.getenv('APP_ENV', 'development')  # Usa APP_ENV dal .env
    
    return render_template('pdashboard/admin.html',
                         users=users,
                         total_users=total_users,
                         active_users=active_users,
                         new_users=new_users,
                         database_url=database_url,
                         app_env=app_env)

@main.route('/editor')
@login_required
@role_required('editor')
def editor_panel():
    return render_template('pdashboard/editor.html')

@main.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
@role_required('admin')
@validate_json_request(['role'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Impedisce la modifica del proprio ruolo
    if user.id == current_user.id:
        return jsonify({'message': 'Non puoi modificare il tuo ruolo'}), 403
    
    data = request.get_json()
    new_role = data.get('role')
    
    # Validazione ruolo
    if new_role not in [role.value for role in UserRole]:
        return jsonify({'message': 'Ruolo non valido'}), 400
    
    user.role = new_role
    db.session.commit()
    current_app.logger.info(f'Utente {current_user.username} ha modificato il ruolo di {user.username} in {new_role}')
    
    return jsonify({'message': 'Ruolo aggiornato con successo'})

@main.route('/admin/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Impedisce l'eliminazione del proprio account
    if user.id == current_user.id:
        return jsonify({'message': 'Non puoi eliminare il tuo account'}), 403
    
    db.session.delete(user)
    db.session.commit()
    current_app.logger.info(f'Utente {current_user.username} ha eliminato l\'utente {user.username}')
    
    return jsonify({'message': 'Utente eliminato con successo'})

@main.route('/admin/users', methods=['POST'])
@login_required
def create_user():
    """Crea un nuovo utente (solo admin)"""
    if not current_user.is_admin():
        return jsonify({'status': 'error', 'message': 'Accesso non autorizzato'}), 403
    
    data = request.get_json()
    current_app.logger.info(f"Tentativo creazione utente da admin {current_user.username}")
    current_app.logger.debug(f"Dati ricevuti per creazione utente: {data}")
    
    try:
        # Validazione dati
        if not all(k in data for k in ('username', 'email', 'password', 'role')):
            return jsonify({'status': 'error', 'error': 'missing_fields', 
                          'message': 'Campi mancanti'}), 400
        
        # Verifica username univoco
        if User.query.filter_by(username=data['username'].lower()).first():
            return jsonify({'status': 'error', 'error': 'username_exists', 
                          'message': 'Username già in uso'}), 400
        
        # Verifica email unica
        if User.query.filter_by(email=data['email'].lower()).first():
            return jsonify({'status': 'error', 'error': 'email_exists', 
                          'message': 'Email già in uso'}), 400
        
        # Validazione password
        form = RegistrationForm()
        try:
            form.validate_password(type('obj', (), {'data': data['password']}))
        except ValidationError as e:
            return jsonify({'status': 'error', 'error': 'invalid_password', 
                          'message': str(e)}), 400
        
        # Crea nuovo utente
        user = User(
            username=data['username'].lower(),
            email=data['email'].lower(),
            role=data['role']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f"Utente {user.username} creato con successo da admin {current_user.username}")
        return jsonify({'status': 'success', 'message': 'Utente creato con successo'})
        
    except Exception as e:
        current_app.logger.error(f"Errore durante creazione utente da admin {current_user.username}: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Errore interno del server'}), 500

@main.route('/profile')
@login_required
def profile():
    current_app.logger.info(f"Accesso al profilo utente: {current_user.username}")
    return render_template('pdashboard/profile.html', user=current_user)

@main.route('/update_theme', methods=['POST'])
@login_required
def update_theme():
    data = request.get_json()
    if 'theme' in data:
        current_user.theme_preference = data['theme']
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@main.route('/debug-config')
def debug_config():
    """Endpoint temporaneo per debug configurazione"""
    config_info = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'APP_ENV': os.getenv('APP_ENV'),
        'SQLALCHEMY_DATABASE_URI': current_app.config['SQLALCHEMY_DATABASE_URI']
    }
    return jsonify(config_info)

@main.route('/admin/plugins/<plugin_name>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_plugin(plugin_name):
    """Attiva/disattiva un plugin"""
    try:
        # Trova il plugin
        plugin = next((p for p in current_app.plugins if p.name == plugin_name), None)
        if not plugin:
            return jsonify({'success': False, 'message': 'Plugin non trovato'}), 404

        # Toggle dello stato
        plugin.is_active = not plugin.is_active
        
        # Salva lo stato
        plugin_status = load_plugin_status()
        plugin_status[plugin_name] = plugin.is_active
        save_plugin_status(plugin_status)
        
        current_app.logger.info(f"Plugin {plugin_name} {'attivato' if plugin.is_active else 'disattivato'}")
        
        # Invece di manipolare i blueprint, restituiamo un segnale per riavviare
        return jsonify({
            'success': True,
            'message': f"Plugin {plugin_name} {'attivato' if plugin.is_active else 'disattivato'}. Riavvia l'applicazione per applicare le modifiche.",
            'requiresRestart': True
        })
        
    except Exception as e:
        current_app.logger.error(f"Errore durante il toggle del plugin {plugin_name}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@main.route('/admin/plugins/reinit', methods=['POST'])
@login_required
@role_required('admin')
def reinit_plugins():
    """Reinizializza tutti i plugin"""
    try:
        # Carica lo stato corrente dei plugin
        plugin_status = load_plugin_status()
        
        # Rimuovi tutti i blueprint esistenti
        plugins_to_remove = []
        for name, blueprint in current_app.blueprints.items():
            if any(p.blueprint and p.blueprint.name == name for p in current_app.plugins):
                plugins_to_remove.append(name)
        
        for name in plugins_to_remove:
            current_app.blueprints.pop(name)
        
        # Aggiorna lo stato e registra i blueprint attivi
        for plugin in current_app.plugins:
            plugin.is_active = plugin_status.get(plugin.name, True)
            if plugin.is_active and plugin.blueprint:
                current_app.register_blueprint(plugin.blueprint)
        
        current_app.logger.info("Plugin reinizializzati con successo")
        return jsonify({'success': True, 'message': 'Plugin reinizializzati con successo'})
        
    except Exception as e:
        current_app.logger.error(f"Errore durante la reinizializzazione dei plugin: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
