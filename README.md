# 🌟 Personal Dashboard Template

Benvenuto! 👋 Questo è un template per applicazioni web basate su Flask, progettato per avviare rapidamente progetti con funzionalità di autenticazione e gestione utenti già integrate. Questo progetto esplora le migliori pratiche di sicurezza e architettura in Flask.

## 🚀 Caratteristiche

- **Autenticazione Completa**: Sistema di login sicuro.
- **Gestione Ruoli**: Supporto per ruoli utente come Admin, Editor e User.
- **Pannello Amministrativo**: Interfaccia per la gestione dell'applicazione.
- **Rate Limiting**: Limita le richieste per proteggere le API.
- **Logging di Sicurezza**: Tracciamento delle attività per la sicurezza.
- **Protezioni CSRF**: Protezione contro attacchi Cross-Site Request Forgery.
- **Validazione Input**: Controllo e sanificazione degli input utente.
- **Security Headers**: Configurazione di intestazioni HTTP per la sicurezza.
- **Architettura Modulare**: Supporto per plugin per estendere le funzionalità.
- **Interfaccia Reattiva**: Design moderno con Bootstrap.

## 📋 Requisiti

- **Python 3.8+**: Linguaggio di programmazione richiesto.
- **Redis**: Opzionale, per il rate limiting.
- **PostgreSQL**: Database consigliato, supportato da SQLAlchemy.

## 🔒 Sicurezza

Il template include diverse misure di sicurezza:

- **Password Hashing**: Utilizzo di Argon2 per l'hashing delle password.
- **Protezione XSS**: Difesa contro attacchi Cross-Site Scripting.
- **Sessioni Sicure**: Gestione sicura delle sessioni utente.
- **Sanitizzazione Input**: Pulizia degli input per prevenire attacchi.
- **Protezioni CSRF**: Implementate tramite Flask-WTF.

## 📂 Struttura del Progetto

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

### 🧩 Gestione dei Plugin

Il sistema supporta l'aggiunta di plugin per estendere le funzionalità:

1. **Creazione di un Plugin**:
   - Crea una cartella in `plugins/`.
   - Estendi `DashboardExtension` per la classe del plugin.
   - Registra le rotte con un `Blueprint`.

2. **Registrazione del Plugin**:
   - I plugin vengono scoperti e registrati automaticamente all'avvio tramite `init_plugins()`.

3. **Navigazione**:
   - I plugin possono aggiungere voci di navigazione personalizzate con `get_navigation_items()`.

### 🎉 Esempio di Plugin

Un esempio è disponibile in `plugins/demo_plugin/`, che include:

- Un blueprint per le rotte.
- Template e stili specifici.
- Funzionalità di esempio per l'integrazione.

## 🛠️ Installazione

1. Aggiungi il repository come origine remota:
   ```bash
   git remote add upstream https://github.com/federicogerardi/dashboard-template.git
   ```

2. Gestione delle dipendenze:
   - `requirements-base.txt` contiene le dipendenze base.
   - Usa `requirements.txt` per aggiungere dipendenze personalizzate:
   ```requirements.txt
   -r requirements-base.txt

   # Dipendenze personalizzate
   pandas==2.2.0
   numpy==1.26.3
   ```

3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura il file `.env` per le variabili d'ambiente.
5. Avvia l'app:
   ```bash
   flask run
   ```

## 🤝 Contributi

I contributi sono benvenuti! Apri una pull request o segnala problemi. Grazie! 🙏

## 📄 Licenza

Questo progetto è concesso in licenza sotto la MIT License.