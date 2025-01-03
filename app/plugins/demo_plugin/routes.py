from flask import render_template, jsonify
from flask_login import login_required
import random
from datetime import datetime, timedelta

@login_required
def index():
    """Pagina principale del plugin"""
    stats = {
        'value1': random.randint(100, 1000),
        'value2': random.randint(50, 500),
        'value3': random.randint(10, 100)
    }
    return render_template('demo_plugin/dashboard.html', stats=stats)

@login_required
def chart():
    data = {
        'labels': ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu'],
        'values': [random.randint(0, 100) for _ in range(6)]
    }
    return data

@login_required
def stats():
    # Genera dati dettagliati per la pagina stats
    detailed_stats = {
        'daily': [
            {
                'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'value': random.randint(50, 200),
                'trend': random.choice(['up', 'down', 'stable']),
                'percentage': random.randint(-20, 20)
            } for i in range(7)
        ],
        'summary': {
            'total': random.randint(1000, 5000),
            'average': random.randint(100, 300),
            'peak': random.randint(300, 500),
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
    }
    return render_template('demo_plugin/stats.html', stats=detailed_stats)

@login_required
def installation():
    """Pagina con le istruzioni di installazione"""
    installation_steps = {
        'requirements': ['Python 3.8+', 'Flask 2.0+', 'SQLAlchemy 1.4+'],
        'pip_packages': ['flask-login', 'flask-sqlalchemy', 'flask-migrate'],
        'optional_packages': ['pytest', 'black', 'flake8'],
        'configuration': {
            'DATABASE_URL': 'postgresql://user:pass@localhost/dbname',
            'SECRET_KEY': 'your-secret-key',
            'DEBUG': 'False'
        }
    }
    return render_template('demo_plugin/installation.html', steps=installation_steps)
