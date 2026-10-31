# AGENTS.md — Subscription Management System (Brightloop)

## Project Summary
Brightloop Software's internal subscription management platform.
Replaces spreadsheets with a centralised billing and customer portal.

## Stack
| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Django 5.x + Django REST Framework|
| ORM        | Django ORM (migrations only)      |
| Database   | PostgreSQL via Supabase            |
| Auth       | JWT (SimpleJWT)                   |
| Frontend   | React + Vite + Tailwind CSS       |
| Background | (Phase 7) Celery + Redis          |

## Folder Layout
```
O/      ← repo root
├── AGENTS.md                 ← this file
├── flow.md                   ← running progress log
├── .gitignore
├── backend/
│   ├── manage.py
│   ├── .env                  ← secrets (never committed)
│   ├── .env.example          ← key template (committed)
│   ├── brightloop/           ← Django project config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/
│       ├── users/            ← Module 1: auth & user management
│       ├── products/         ← Module 2
│       ├── plans/            ← Module 3
│       ├── subscriptions/    ← Module 4
│       ├── invoices/         ← Module 5
│       ├── discounts/        ← Module 6
│       ├── payments/         ← Module 7
│       └── reports/          ← Module 8
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── layouts/
    │   ├── services/        ← axios API calls only
    │   └── context/
    └── package.json
```

## Rules

### Secrets
- All secrets live in `backend/.env` only.
- `.env` is in `.gitignore`. Verify with `git status` before every commit.
- Never print, log, or hardcode secrets anywhere.
- `.env.example` lists every key with an empty value — always keep it in sync.

### Database
- Use the Django ORM for all queries. Raw SQL only when the ORM cannot express it, and only via `connection.execute()` with parameterised queries.
- Every schema change → a new migration (`makemigrations` + `migrate`). Never edit migration files by hand.
- Only one person creates migrations at a time. Pull and migrate before creating new migrations.

### API / Frontend
- The frontend never connects to the database directly. All data goes through the REST API.
- All API responses use consistent JSON: `{ "data": ..., "error": null }` on success, `{ "data": null, "error": "message" }` on failure.

### Auth
- Three roles: `admin`, `staff`, `customer`. Stored on the user record.
- Admin can create staff accounts. Customers self-register.
- JWT access token (15 min) + refresh token (7 days).

## Commands

```bash
# Activate the virtual environment
source .venv/bin/activate          # from repo root

# Run the dev server (from backend/)
cd backend && python manage.py runserver

# Make migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Test the DB connection
python manage.py check --database default

# Create a superuser (admin seed)
python manage.py createsuperuser

# Run all tests
python manage.py test apps/
```

## Team Rules
- Pull before creating any migration.
- Only one person creates migrations at a time to avoid conflicts.
- All environment variables must be documented in `.env.example` the moment they are added.
