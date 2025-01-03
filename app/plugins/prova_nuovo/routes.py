from flask import render_template
from flask_login import login_required

@login_required
def index():
    return render_template('prova_nuovo/index.html')
