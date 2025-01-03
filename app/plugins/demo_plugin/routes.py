from flask import render_template
from flask_login import login_required
import random

@login_required
def index():
    stats = {
        'value1': random.randint(100, 1000),
        'value2': random.randint(50, 500),
        'value3': random.randint(10, 100)
    }
    return render_template('demo_plugin/index.html', stats=stats)

@login_required
def chart():
    # Dati demo per il grafico
    data = {
        'labels': ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu'],
        'values': [random.randint(0, 100) for _ in range(6)]
    }
    return data
