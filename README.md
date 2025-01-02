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

## Requisiti

- Python 3.8+
- Redis (opzionale, per rate limiting)

## Sicurezza

Il template implementa diverse misure di sicurezza come riferimento per progetti Flask:
- Password hashing con Argon2
- Protezione contro XSS
- Rate limiting sulle API sensibili
- Sessioni sicure
- Input sanitization