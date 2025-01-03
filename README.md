# 🌟 Personal Dashboard Template

Ciao! 👋 Questo è un template Flask per aiutarti a iniziare rapidamente i tuoi progetti web con autenticazione e gestione utenti già implementati. È un progetto di studio personale che esplora le best practice di sicurezza e architettura in Flask. 

## 🚀 Caratteristiche

- Sistema di autenticazione completo 🔐
- Gestione ruoli utente (Admin, Editor, User) 👥
- Pannello amministrativo 🛠️
- Rate limiting ⏳
- Logging di sicurezza 📜
- Protezioni CSRF 🛡️
- Validazione input ✅
- Security headers configurati 🔒
- Architettura modulare con supporto per plugin 🔌
- Interfaccia utente reattiva con Bootstrap 🎨

## 📋 Requisiti

- Python 3.8+ 🐍
- Redis (opzionale, per rate limiting) 🗄️
- PostgreSQL (o altro database supportato da SQLAlchemy) 🗃️

## 🔒 Sicurezza

Il template implementa diverse misure di sicurezza come riferimento per progetti Flask:
- Password hashing con Argon2 🔑
- Protezione contro XSS 🚫
- Rate limiting sulle API sensibili ⚖️
- Sessioni sicure 🔒
- Input sanitization 🧼
- Protezione CSRF tramite Flask-WTF 🛡️

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

Il sistema supporta l'aggiunta di plugin per estendere le funzionalità dell'app. I plugin possono essere facilmente integrati seguendo questi passaggi:

1. **Creazione di un Plugin**:
   - Crea una nuova cartella all'interno della directory `plugins/`.
   - Implementa la classe del plugin estendendo `DashboardExtension`.
   - Registra le rotte del plugin utilizzando un `Blueprint`.

2. **Registrazione del Plugin**:
   - I plugin vengono automaticamente scoperti e registrati all'avvio dell'app tramite la funzione `init_plugins()`.

3. **Navigazione**:
   - Ogni plugin può fornire voci di navigazione personalizzate tramite il metodo `get_navigation_items()`.

### 🎉 Esempio di Plugin

Un esempio di plugin è fornito nella directory `plugins/demo_plugin/`, che include:

- Un blueprint per gestire le rotte.
- Template e stili specifici per il plugin.
- Funzionalità di esempio per dimostrare l'integrazione.

## 🛠️ Installazione

1. Aggiungi il mio repository come origine remota:  
```  
git remote add upstream https://github.com/federicogerardi/dashboard-template.git  
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

## 🤝 Contributi

I contributi sono sempre benvenuti! Se desideri contribuire, apri una pull request o segnalami eventuali problemi. Grazie! 🙏

## 📄 Licenza

Questo progetto è concesso in licenza sotto la MIT License.