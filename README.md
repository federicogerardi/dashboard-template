# Personal Dashboard Template

Un template Flask per iniziare rapidamente progetti web con autenticazione e gestione utenti già implementati. Questo è un progetto di studio personale per esplorare le best practice di sicurezza e architettura in Flask.

## Caratteristiche

- Sistema di autenticazione completo
- Gestione ruoli utente (Admin, Editor, User)
- Pannello amministrativo
- Rate limiting
- Logging di sicurezza
- Protezioni CSRF
- Validazione input
- Security headers configurati
- Architettura modulare con supporto per plugin
- Interfaccia utente reattiva con Bootstrap

## Requisiti

- Python 3.8+
- Redis (opzionale, per rate limiting)
- PostgreSQL (o altro database supportato da SQLAlchemy)

## Sicurezza

Il template implementa diverse misure di sicurezza come riferimento per progetti Flask:
- Password hashing con Argon2
- Protezione contro XSS
- Rate limiting sulle API sensibili
- Sessioni sicure
- Input sanitization
- Protezione CSRF tramite Flask-WTF

## Struttura del Progetto

La struttura del progetto è organizzata come segue:

```
app/
├── __init__.py
├── core/
│   ├── controllers/
│   ├── models/
│   └── utils/
├── extensions/
├── plugins/
│   ├── demo_plugin/
│   └── ...
├── templates/
│   └── pdashboard/
└── static/
```

### Gestione dei Plugin

Il sistema supporta l'aggiunta di plugin per estendere le funzionalità dell'app. I plugin possono essere facilmente integrati seguendo questi passaggi:

1. **Creazione di un Plugin**:
   - Creare una nuova cartella all'interno della directory `plugins/`.
   - Implementare la classe del plugin estendendo `DashboardExtension`.
   - Registrare le rotte del plugin utilizzando un `Blueprint`.

2. **Registrazione del Plugin**:
   - I plugin vengono automaticamente scoperti e registrati all'avvio dell'app tramite la funzione `init_plugins()`.

3. **Navigazione**:
   - Ogni plugin può fornire voci di navigazione personalizzate tramite il metodo `get_navigation_items()`.

### Esempio di Plugin

Un esempio di plugin è fornito nella directory `plugins/demo_plugin/`, che include:

- Un blueprint per gestire le rotte.
- Template e stili specifici per il plugin.
- Funzionalità di esempio per dimostrare l'integrazione.

## Installazione

1. Clona il repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```

3. Configura il file `.env` per le variabili d'ambiente necessarie.

4. Avvia l'app:
   ```
   flask run
   ```

## Contribuzione

Le contribuzioni sono benvenute! Se desideri contribuire, apri una pull request o segnalaci eventuali problemi.

## Licenza

Questo progetto è concesso in licenza sotto la MIT License.