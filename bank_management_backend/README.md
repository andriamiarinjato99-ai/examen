# Bank Management System — Django Backend

Backend REST fonctionnel pour une application de gestion bancaire.

## Stack

- Python
- Django 5
- Django REST Framework
- SimpleJWT
- django-filter
- drf-spectacular / Swagger
- SQLite par défaut
- Transactions SQL avec `transaction.atomic()`
- Verrouillage concurrentiel avec `select_for_update()`
- Journal d'audit

## 1. Installation Windows

Dans CMD/PowerShell :

```bash
cd bank_management_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Ou simplement :

```text
setup.bat
```

## 2. Accès

Swagger:
http://127.0.0.1:8000/api/docs/

Schéma OpenAPI:
http://127.0.0.1:8000/api/schema/

Admin:
http://127.0.0.1:8000/admin/

Compte de démonstration:
- username: admin
- password: Admin123!

Change ce mot de passe en production.

## 3. Authentification JWT

POST `/api/auth/token/`

```json
{
  "username": "admin",
  "password": "Admin123!"
}
```

Puis utiliser :

```text
Authorization: Bearer <access_token>
```

## 4. Principales routes

```text
POST /api/auth/token/
POST /api/auth/token/refresh/

GET/POST /api/clients/
GET/POST /api/accounts/
GET/POST /api/agencies/
GET/POST /api/employees/
GET/POST /api/beneficiaries/

GET /api/transactions/
POST /api/transactions/deposit/
POST /api/transactions/withdraw/
POST /api/transactions/transfer/

GET /api/audit/
GET /api/statistics/
```

## 5. Dépôt

POST `/api/transactions/deposit/`

```json
{
  "account_id": 1,
  "amount": "100000.00",
  "description": "Dépôt espèces"
}
```

## 6. Retrait

POST `/api/transactions/withdraw/`

```json
{
  "account_id": 1,
  "amount": "25000.00",
  "description": "Retrait"
}
```

Le backend refuse automatiquement un retrait supérieur au solde.

## 7. Virement

POST `/api/transactions/transfer/`

```json
{
  "source_account_id": 1,
  "destination_account_id": 2,
  "amount": "50000.00",
  "description": "Virement interne"
}
```

Le virement utilise une transaction SQL atomique. Le solde des deux comptes est verrouillé pendant l'opération. Si une étape échoue, l'ensemble de l'opération est annulé.

## 8. Rôles

Le modèle Employee prévoit :

- ADMIN
- MANAGER
- CASHIER
- AUDITOR

Les permissions peuvent être affinées selon les besoins de l'application React.

## 9. Sécurité

Le projet contient déjà :

- JWT
- permissions DRF
- validation des montants
- protection contre le retrait avec solde insuffisant
- comptes actifs/bloqués/fermés
- `transaction.atomic()`
- `select_for_update()`
- journal d'audit
- secret dans `.env`
- mots de passe Django hashés
- protection HTTP de base

Pour une vraie mise en production bancaire, il faut ajouter HTTPS, rotation des secrets, PostgreSQL, sauvegardes, limitation de débit, MFA, surveillance, gestion stricte des rôles et procédures de conformité.

## 10. PostgreSQL

Le projet démarre avec SQLite pour faciliter les tests. Pour un environnement sérieux, remplace DATABASES dans `config/settings.py` par PostgreSQL et ajoute le driver adapté.

## 11. Architecture

```text
clients       -> informations clients
accounts      -> comptes bancaires et soldes
transactions  -> dépôts / retraits / virements
beneficiaries -> bénéficiaires
agencies      -> agences
employees     -> employés + rôles
audit         -> journalisation
dashboard     -> statistiques
```

Le frontend React peut consommer directement cette API.
