from flask import Blueprint, render_template
from pdashboard import create_app

# Crea un blueprint di esempio
example = Blueprint('example', __name__, url_prefix='/example')

@example.route('/')
def index():
    return render_template('example/index.html')

# Inizializza l'app
app = create_app()

# Registra il blueprint aggiuntivo
app.register_additional_blueprints([example])

if __name__ == '__main__':
    app.run(debug=True) 