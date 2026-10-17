# Finova Bank — Backend + Frontend (JWT, sans Keycloak)

Banque en ligne étudiante : inscription, connexion JWT, comptes, dépôts, retraits, virements.  
Prêt pour **Render** (sans Docker obligatoire).

## Contenu

```
bank_management_backend/   # API Django + SimpleJWT
frontend/                  # React (Vite + Tailwind)
```

## Démarrage local

### Backend

```bash
cd bank_management_backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

- API : http://127.0.0.1:8000  
- Docs : http://127.0.0.1:8000/api/docs/  
- Compte démo : `admin` / `Admin123!`

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

- App : http://localhost:5173  
- Inscription : `/register` (crée User + Client + compte bancaire)  
- Connexion : e-mail + mot de passe

## Auth

| Endpoint | Description |
|----------|-------------|
| `POST /api/auth/register/` | Inscription (first_name, last_name, email, phone, password) |
| `POST /api/auth/token/` | Login → `{ access, refresh }` |
| `POST /api/auth/token/refresh/` | Rafraîchir le token |
| `GET /api/auth/me/` | Fiche client de l'utilisateur connecté |

Identifiant de connexion = **e-mail**.

## Déploiement Render

### 1. PostgreSQL
New → PostgreSQL (free).

### 2. Backend (Web Service)
- Root directory : `bank_management_backend`
- Build : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start : `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
- Env :
```
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<depuis Postgres Render>
CORS_ALLOWED_ORIGINS=https://VOTRE-FRONTEND.onrender.com
BEHIND_PROXY=true
```

### 3. Frontend (Static Site)
- Root : `frontend`
- Build : `npm install && npm run build`
- Publish : `dist`
- Env build :
```
VITE_API_URL=https://VOTRE-BACKEND.onrender.com/api
```

**Note :** le free tier backend s'endort après 15 min d'inactivité (~1 min au réveil).

## InfinityFree

Non adapté (PHP uniquement). Utilisez Render pour ce projet.

## Fonctionnalités bancaires

- Inscription + ouverture automatique d'un compte courant
- Dépôt / retrait / virement (transaction atomique)
- Bénéficiaires, historique, tableau de bord
