from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models.user import User, UserRole
from app.utils.decorators import role_required
from app.utils.security import sanitize_input, validate_json_request, validate_username
from app import db
from werkzeug.security import generate_password_hash

# Creazione del blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/dashboard')
@login_required
def dashboard():
    # Inizializza i valori se non esistono
    if current_user.login_count is None:
        current_user.login_count = 0
    if current_user.created_at is None:
        current_user.created_at = datetime.utcnow()
    
    # Aggiorna statistiche utente
    current_user.login_count += 1
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
    
    return render_template('dashboard.html',
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
    
    # Calcola alcune statistiche di base
    total_users = User.query.count()
    
    # Considera attivi gli utenti che hanno effettuato l'accesso negli ultimi 7 giorni
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_users = User.query.filter(User.last_login >= seven_days_ago).count()
    
    new_users = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    return render_template('admin.html',
                         users=users,
                         total_users=total_users,
                         active_users=active_users,
                         new_users=new_users)

@main.route('/editor')
@login_required
@role_required('editor')
def editor_panel():
    return render_template('editor.html')

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
    try:
        print("1. Inizio creazione utente")
        # Verifica che l'utente corrente sia admin
        if not current_user.is_admin():
            print("2. Utente non autorizzato")
            return jsonify({'message': 'Non autorizzato'}), 403
        
        data = request.get_json()
        print("3. Dati ricevuti:", data)
        
        # Validazione dati
        required_fields = ['username', 'email', 'password', 'role']
        if not all(key in data for key in required_fields):
            missing_fields = [field for field in required_fields if field not in data]
            print("4. Campi mancanti:", missing_fields)
            return jsonify({
                'message': f'Dati mancanti: {", ".join(missing_fields)}',
                'error': 'missing_fields'
            }), 400
            
        # Validazione username
        if User.query.filter_by(username=data['username']).first():
            print("5. Username già esistente")
            return jsonify({
                'message': 'Username già in uso',
                'error': 'username_exists'
            }), 400
            
        # Validazione email
        if User.query.filter_by(email=data['email']).first():
            print("6. Email già esistente")
            return jsonify({
                'message': 'Email già in uso',
                'error': 'email_exists'
            }), 400
            
        # Creazione nuovo utente
        print("7. Creazione nuovo utente")
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data['role'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_user)
        db.session.commit()
        print("8. Utente creato con successo")
        
        return jsonify({
            'message': 'Utente creato con successo',
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'role': new_user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print("ERROR:", str(e))
        current_app.logger.error(f"Errore durante la creazione dell'utente: {str(e)}")
        return jsonify({
            'message': 'Errore durante la creazione dell\'utente',
            'error': str(e)
        }), 500

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@main.route('/update_theme', methods=['POST'])
@login_required
def update_theme():
    data = request.get_json()
    if 'theme' in data:
        current_user.theme_preference = data['theme']
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400
