#!/bin/bash

# Verifica se è stato fornito il nome del plugin
if [ "$#" -ne 1 ]; then
    echo "Usage: ./create_plugin.sh <plugin_name>"
    echo "Example: ./create_plugin.sh my_plugin"
    exit 1
fi

PLUGIN_NAME=$(echo "$1" | tr '-' '_')
PLUGIN_DIR="app/plugins/${PLUGIN_NAME}"

# Verifica se il plugin esiste già
if [ -d "$PLUGIN_DIR" ]; then
    echo "Error: Plugin $PLUGIN_NAME already exists"
    exit 1
fi

# Crea la struttura delle directory
echo "Creating plugin structure for $PLUGIN_NAME..."
mkdir -p "$PLUGIN_DIR"/{templates/"$PLUGIN_NAME",static/"$PLUGIN_NAME"/{css,js}}

# Converti il nome del plugin in maiuscolo per il primo carattere
PLUGIN_NAME_UPPER="$(tr '[:lower:]' '[:upper:]' <<< ${PLUGIN_NAME:0:1})${PLUGIN_NAME:1}"

# Crea __init__.py
cat > "$PLUGIN_DIR/__init__.py" << EOL
from flask import Blueprint
from app.extensions.base import DashboardExtension, NavigationItem

class ${PLUGIN_NAME_UPPER}Plugin(DashboardExtension):
    def __init__(self):
        super().__init__('${PLUGIN_NAME_UPPER} Plugin')
        self.blueprint = Blueprint(
            '${PLUGIN_NAME}',
            __name__,
            template_folder='templates',
            static_folder='static',
            url_prefix='/${PLUGIN_NAME}'
        )
        
        # Registra le routes
        from . import routes
        self.blueprint.add_url_rule('/', 'index', routes.index)
    
    def get_navigation_items(self):
        return [
            NavigationItem(
                name='${PLUGIN_NAME_UPPER} Plugin',
                icon='fas fa-puzzle-piece',
                url='/${PLUGIN_NAME}',
                permission='user'
            )
        ]

# Istanza del plugin che verrà caricata automaticamente
plugin = ${PLUGIN_NAME_UPPER}Plugin()
EOL

# Crea routes.py
cat > "$PLUGIN_DIR/routes.py" << EOL
from flask import render_template
from flask_login import login_required

@login_required
def index():
    return render_template('${PLUGIN_NAME}/index.html')
EOL

# Crea models.py
cat > "$PLUGIN_DIR/models.py" << EOL
from app.extensions import db

# Definisci qui i tuoi modelli
EOL

# Crea il template base
cat > "$PLUGIN_DIR/templates/$PLUGIN_NAME/index.html" << EOL
{% extends "pdashboard/base.html" %}

{% block title %}${PLUGIN_NAME_UPPER} Plugin{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item">
    <a href="{{ url_for('${PLUGIN_NAME}.index') }}" class="text-decoration-none">
        <i class="fas fa-puzzle-piece me-1"></i>${PLUGIN_NAME_UPPER} Plugin
    </a>
</li>
<li class="breadcrumb-item active" aria-current="page">Dashboard</li>
{% endblock %}

{% block content %}
<div class="container py-4">
    <h1 class="h3 mb-4">${PLUGIN_NAME_UPPER} Plugin Dashboard</h1>
    
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Benvenuto nel ${PLUGIN_NAME_UPPER} Plugin</h5>
            <p class="card-text">Inizia a personalizzare questo plugin secondo le tue necessità.</p>
        </div>
    </div>
</div>
{% endblock %}
EOL

# Sostituisci i placeholder nel template
PLUGIN_NAME_UPPER=$(echo "${PLUGIN_NAME^}")
sed -i "s/\$(PLUGIN_NAME)/$PLUGIN_NAME/g" "$PLUGIN_DIR/templates/$PLUGIN_NAME/index.html"
sed -i "s/\$(PLUGIN_NAME_UPPER)/$PLUGIN_NAME_UPPER/g" "$PLUGIN_DIR/templates/$PLUGIN_NAME/index.html"

# Crea il file CSS base
cat > "$PLUGIN_DIR/static/$PLUGIN_NAME/css/style.css" << EOL
/* Stili specifici del plugin */
.${PLUGIN_NAME}-card {
    transition: transform 0.2s ease;
}

.${PLUGIN_NAME}-card:hover {
    transform: translateY(-5px);
}
EOL

# Imposta i permessi
chmod -R 755 "$PLUGIN_DIR"

echo "Plugin $PLUGIN_NAME created successfully!"
echo "Directory structure:"
tree "$PLUGIN_DIR"
echo -e "\nPer attivare il plugin, riavvia l'applicazione Flask." 

# Debug: Verifica il contenuto dei file generati
echo -e "\nContenuto di __init__.py:"
cat "$PLUGIN_DIR/__init__.py"

echo -e "\nVerifica dei permessi:"
ls -l "$PLUGIN_DIR"

echo -e "\nVerifica della struttura del plugin:"
find "$PLUGIN_DIR" -type f -exec echo {} \;

echo -e "\nVerifica del modulo Python:"
python3 -c "from app.plugins.${PLUGIN_NAME} import plugin; print(f'Plugin name: {plugin.name}')" 