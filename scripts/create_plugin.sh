#!/bin/bash

# Funzione per la validazione del nome del plugin
validate_plugin_name() {
    local display_name="$1"
    local max_length=50  # Lunghezza massima del nome visualizzato
    local min_length=3   # Lunghezza minima del nome visualizzato
    
    # Controllo lunghezza minima
    if [ ${#display_name} -lt $min_length ]; then
        echo "Error: Il nome del plugin deve essere di almeno $min_length caratteri"
        exit 1
    fi
    
    # Controllo lunghezza massima
    if [ ${#display_name} -gt $max_length ]; then
        echo "Error: Il nome del plugin non può superare i $max_length caratteri"
        exit 1
    fi
    
    # Controllo caratteri non consentiti nel nome visualizzato
    if [[ "$display_name" =~ [^a-zA-Z0-9àáâãäçèéêëìíîïñòóôõöùúûü\ \-] ]]; then
        echo "Error: Il nome del plugin contiene caratteri non consentiti"
        echo "Sono permessi solo lettere, numeri, spazi e trattini"
        exit 1
    fi
}

# Verifica se è stato fornito il nome del plugin
if [ "$#" -ne 1 ]; then
    echo "Usage: ./create_plugin.sh \"<plugin display name>\""
    echo "Example: ./create_plugin.sh \"Il Mio Plugin\""
    exit 1
fi

# Validazione del nome del plugin
validate_plugin_name "$1"

# Gestione nomi plugin
PLUGIN_DISPLAY_NAME="$1"                                          # Nome visualizzato (es: "Il Mio Plugin")
PLUGIN_NAME=$(echo "$1" | tr '[:upper:]' '[:lower:]' |          # Converti in lowercase
              tr -d '[:punct:]' |                                # Rimuovi punteggiatura
              tr 'àáâãäçèéêëìíîïñòóôõöùúûü' 'aaaaaceeeeiiiinooooouuuu' |  # Normalizza caratteri accentati
              tr ' ' '_' |                                       # Sostituisci spazi con underscore
              sed 's/__*/_/g')                                   # Rimuovi underscore multipli

# Verifica lunghezza del nome tecnico
PLUGIN_NAME_MAX_LENGTH=30
if [ ${#PLUGIN_NAME} -gt $PLUGIN_NAME_MAX_LENGTH ]; then
    echo "Error: Il nome tecnico del plugin (${PLUGIN_NAME}) supera i ${PLUGIN_NAME_MAX_LENGTH} caratteri"
    echo "Usa un nome più breve o con meno parole"
    exit 1
fi

# Verifica che il nome tecnico contenga solo caratteri validi
if [[ ! "$PLUGIN_NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Error: Il nome tecnico del plugin deve iniziare con una lettera e contenere solo lettere minuscole, numeri e underscore"
    exit 1
fi

PLUGIN_DIR="app/plugins/${PLUGIN_NAME}"

# Verifica se il plugin esiste già
if [ -d "$PLUGIN_DIR" ]; then
    echo "Error: Plugin $PLUGIN_NAME already exists"
    exit 1
fi

# Verifica i permessi della directory plugins
if [ ! -w "app/plugins" ]; then
    echo "Error: Non hai i permessi di scrittura nella directory app/plugins"
    exit 1
fi

# Verifica spazio disponibile (minimo 1MB)
available_space=$(df -P . | awk 'NR==2 {print $4}')
if [ "$available_space" -lt 1024 ]; then
    echo "Error: Spazio su disco insufficiente"
    exit 1
fi

# Crea la struttura delle directory
echo "Creating plugin structure for $PLUGIN_DISPLAY_NAME..."
mkdir -p "$PLUGIN_DIR"/{templates/"$PLUGIN_NAME",static/"$PLUGIN_NAME"/{css,js}} || {
    echo "Error: Impossibile creare la struttura delle directory"
    exit 1
}

# Converti il nome del plugin per la classe Python
PLUGIN_CLASS_NAME=$(echo "$PLUGIN_NAME" | sed -r 's/(^|_)([a-z])/\U\2/g')  # Convert to PascalCase

# Crea __init__.py
cat > "$PLUGIN_DIR/__init__.py" << EOL
from flask import Blueprint
from app.extensions.base import DashboardExtension, NavigationItem

class ${PLUGIN_CLASS_NAME}Plugin(DashboardExtension):
    def __init__(self):
        super().__init__('${PLUGIN_DISPLAY_NAME}')  # Usa il nome visualizzato
        self.blueprint = Blueprint(
            '${PLUGIN_NAME}',
            __name__,
            template_folder='templates',
            static_folder='static',
            url_prefix='/${PLUGIN_NAME}'
        )
        self.provides_index = False
        self.index_priority = 0
        
        # Registra le routes
        from . import routes
        self.blueprint.add_url_rule('/', 'index', routes.index)
    
    def get_navigation_items(self):
        return [
            NavigationItem(
                name='${PLUGIN_DISPLAY_NAME}',  # Usa il nome visualizzato
                icon='fas fa-puzzle-piece',
                url='/${PLUGIN_NAME}',
                permission='user',
                subitems=[]
            )
        ]

plugin = ${PLUGIN_CLASS_NAME}Plugin()
EOL

# Crea routes.py
cat > "$PLUGIN_DIR/routes.py" << EOL
from flask import render_template
from flask_login import login_required

@login_required
def index():
    """Pagina principale del plugin"""
    return render_template('${PLUGIN_NAME}/dashboard.html')
EOL

# Crea models.py
cat > "$PLUGIN_DIR/models.py" << EOL
from app.extensions import db

# Definisci qui i tuoi modelli
EOL

# Crea il template dashboard.html
cat > "$PLUGIN_DIR/templates/$PLUGIN_NAME/dashboard.html" << EOL
{% extends "pdashboard/base.html" %}

{% block title %}${PLUGIN_DISPLAY_NAME} - Dashboard{% endblock %}

{% block styles %}
<link rel="stylesheet" href="{{ url_for('${PLUGIN_NAME}.static', filename='css/style.css') }}">
{% endblock %}

{% block content %}
<div class="container py-4">
    <!-- Header Section -->
    <div class="row mb-4">
        <div class="col-md-8">
            <h1 class="h3 mb-2">${PLUGIN_DISPLAY_NAME}</h1>
            <p class="text-muted">Descrizione del plugin</p>
        </div>
        <div class="col-md-4 text-end">
            <button class="btn btn-outline-primary" id="configPlugin">
                <i class="fas fa-cog me-2"></i>Configura
            </button>
        </div>
    </div>

    <!-- Content Section -->
    <div class="row g-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Contenuto Plugin</h5>
                    <p>Implementa qui il contenuto del tuo plugin.</p>
                </div>
            </div>
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

echo "Plugin created successfully!"
echo "Display Name: $PLUGIN_DISPLAY_NAME"
echo "Technical Name: $PLUGIN_NAME"
echo "Class Name: ${PLUGIN_CLASS_NAME}Plugin"
echo -e "\nDirectory structure:"
tree "$PLUGIN_DIR"
echo -e "\nPer attivare il plugin, riavvia l'applicazione Flask."

# Debug: Verifica il contenuto dei file generati
echo -e "\nContenuto di __init__.py:"
cat "$PLUGIN_DIR/__init__.py"

echo -e "\nVerifica dei permessi:"
ls -l "$PLUGIN_DIR"

echo -e "\nVerifica della struttura del plugin:"
find "$PLUGIN_DIR" -type f -exec echo {} \;

# Rimuovo questa verifica perché richiede l'ambiente Python attivo
# e potrebbe fallire se l'app non è in esecuzione
# echo -e "\nVerifica del modulo Python:"
# python3 -c "from app.plugins.${PLUGIN_NAME} import plugin; print(f'Plugin name: {plugin.name}')" 