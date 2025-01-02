#!/bin/bash

# Uso: ./switch_db.sh [sqlite|postgres] [development|testing|production]

# Funzione per modificare il .env in modo compatibile con macOS e Linux
update_env_file() {
    local key="$1"
    local value="$2"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|^${key}=.*|${key}=${value}|" .env
    else
        # Linux
        sed -i "s|^${key}=.*|${key}=${value}|" .env
    fi
}

# Funzione per creare la directory instance se non esiste
ensure_instance_dir() {
    if [ ! -d "instance" ]; then
        echo "Creating instance directory..."
        mkdir -p instance
        chmod 777 instance  # Temporaneamente diamo tutti i permessi per debug
    else
        # Se la directory esiste, assicuriamoci che abbia i permessi corretti
        chmod 777 instance  # Temporaneamente diamo tutti i permessi per debug
    fi
    
    # Assicuriamoci che il file del database sia scrivibile
    if [ -f instance/dev.db ]; then
        chmod 666 instance/dev.db
    fi
}

# Funzione per gestire i backup
ensure_backup_dir() {
    if [ ! -d "backups" ]; then
        echo "Creating backups directory..."
        mkdir -p backups/sqlite
        mkdir -p backups/postgres
        # Aggiungi .gitkeep per mantenere la struttura delle directory
        touch backups/sqlite/.gitkeep
        touch backups/postgres/.gitkeep
    fi
}

# Verifica parametri
if [ "$#" -lt 1 ]; then
    echo "Usage: ./switch_db.sh [sqlite|postgres] [development|testing|production]"
    exit 1
fi

# Gestione ambiente
ENV=${2:-development}  # Se non specificato, usa development come default
case $ENV in
    development|testing|production)
        echo "Setting environment to: $ENV"
        update_env_file "APP_ENV" "$ENV"
        ;;
    *)
        echo "Invalid environment. Use: development, testing, or production"
        exit 1
        ;;
esac

if [ "$1" = "sqlite" ]; then
    echo "Switching to SQLite..."
    # Backup PostgreSQL se esiste
    if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
        ensure_backup_dir
        echo "Creating PostgreSQL backup..."
        pg_dump -U dashboard_user dashboard_dev > backups/postgres/backup_$(date +%Y%m%d_%H%M%S).sql
    fi
    
    # Prepara directory per SQLite
    ensure_instance_dir
    
    # Switch a SQLite usando percorso assoluto basato sull'ambiente
    case $ENV in
        development)
            DB_PATH="$(pwd)/instance/dev.db"
            ;;
        testing)
            DB_PATH="$(pwd)/instance/test.db"
            ;;
        production)
            DB_PATH="$(pwd)/instance/prod.db"
            ;;
    esac
    update_env_file "DATABASE_URL" "sqlite:///${DB_PATH}"
    
elif [ "$1" = "postgres" ]; then
    echo "Switching to PostgreSQL..."
    # Backup SQLite se esiste
    if [ -f instance/dev.db ]; then
        ensure_backup_dir
        echo "Creating SQLite backup..."
        sqlite3 instance/dev.db .dump > backups/sqlite/backup_$(date +%Y%m%d_%H%M%S).sql
    fi
    
    # Richiedi i dettagli di connessione PostgreSQL
    read -p "Enter PostgreSQL username: " PG_USER
    read -s -p "Enter PostgreSQL password: " PG_PASS
    echo
    read -p "Enter PostgreSQL host [localhost]: " PG_HOST
    PG_HOST=${PG_HOST:-localhost}
    read -p "Enter PostgreSQL port [5432]: " PG_PORT
    PG_PORT=${PG_PORT:-5432}
    
    # Nome database basato sull'ambiente
    case $ENV in
        development)
            DEFAULT_DB="dashboard_dev"
            ;;
        testing)
            DEFAULT_DB="dashboard_test"
            ;;
        production)
            DEFAULT_DB="dashboard_prod"
            ;;
    esac
    read -p "Enter PostgreSQL database name [$DEFAULT_DB]: " PG_DB
    PG_DB=${PG_DB:-$DEFAULT_DB}
    
    # Costruisci l'URL di connessione
    PG_URL="postgresql+psycopg://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/${PG_DB}"
    
    # Switch a PostgreSQL
    update_env_file "DATABASE_URL" "${PG_URL}"
    
    echo "Testing PostgreSQL connection..."
    if ! psql "postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/${PG_DB}" -c '\q' 2>/dev/null; then
        echo "Error: Could not connect to PostgreSQL. Please check your credentials."
        exit 1
    fi

    # Verifica se il database è vuoto o se le tabelle necessarie esistono già
    TABLES_COUNT=$(psql -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" "$PG_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    
    if [ "$TABLES_COUNT" -eq "0" ]; then
        echo "Database vuoto, inizializzazione nuovo schema..."
        if ! psql -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" "$PG_DB" <<EOF 2>/dev/null; then
            CREATE SCHEMA IF NOT EXISTS public;
            GRANT ALL ON SCHEMA public TO ${PG_USER};
EOF
            echo "Permessi insufficienti. È necessario un superuser PostgreSQL."
            read -p "Vuoi procedere con un superuser? (s/N): " use_superuser
            if [[ "$use_superuser" =~ ^[Ss]$ ]]; then
                read -p "Inserisci username del superuser PostgreSQL: " PSQL_SUPERUSER
                echo "Assegnazione permessi con superuser..."
                if ! sudo -u $PSQL_SUPERUSER psql -c "ALTER DATABASE ${PG_DB} OWNER TO ${PG_USER};" >/dev/null 2>&1 || \
                   ! sudo -u $PSQL_SUPERUSER psql -d ${PG_DB} -c "ALTER SCHEMA public OWNER TO ${PG_USER};" >/dev/null 2>&1; then
                    echo "Errore: Impossibile assegnare i permessi anche con superuser."
                    exit 1
                fi
                echo "Permessi assegnati correttamente."
            else
                echo "Operazione annullata. I permessi potrebbero essere insufficienti."
            fi
        fi
    else
        echo "Database esistente trovato, mantenimento dati..."
        # Backup del database PostgreSQL esistente per sicurezza
        ensure_backup_dir
        echo "Creating backup of existing PostgreSQL database..."
        pg_dump -U "$PG_USER" -h "$PG_HOST" -p "$PG_PORT" "$PG_DB" > backups/postgres/backup_$(date +%Y%m%d_%H%M%S).sql
    fi

fi

# Gestione migrazioni
echo "Managing migrations..."
if [ ! -d "migrations" ]; then
    echo "Initializing new migrations directory..."
    export FLASK_APP=app
    flask db init
fi

# Crea e applica la migrazione solo se necessario
echo "Checking and applying migrations..."
flask db migrate -m "Migration $(date +%Y%m%d_%H%M%S)"
flask db upgrade

echo "Switch completed successfully!"