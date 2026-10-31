# flow.md — Running Progress Log

## Current Module
**Module 1 – Authentication & User Management** | Status: 🟡 In Progress

---

## Completed Steps

| Date       | Step                                        | Result                                              |
|------------|---------------------------------------------|-----------------------------------------------------|
| 2026-10-31 | Supabase project created                    | Connection values noted by user                     |
| 2026-10-31 | .venv created, Django 5.x installed         | Django + psycopg + dotenv ready                     |
| 2026-10-31 | AGENTS.md + flow.md + .gitignore created    | Conventions and progress log in place               |
| 2026-10-31 | Django project `brightloop` scaffolded      | `manage.py` + `brightloop/` config package          |
| 2026-10-31 | DRF + SimpleJWT installed                   | djangorestframework 3.18.3, simplejwt 5.5.1         |
| 2026-10-31 | Custom `User` model (email + role)          | `apps/users/models.py` — email as USERNAME_FIELD    |
| 2026-10-31 | Auth serializers + validators               | Password strength regex enforced                    |
| 2026-10-31 | Auth views (register, login, me, reset)     | `apps/users/views.py` — all 7 endpoints             |
| 2026-10-31 | Role permissions (`IsAdmin`, `IsAdminOrStaff`) | `apps/users/permissions.py`                      |
| 2026-10-31 | URL routes wired                            | `brightloop/urls.py` → `apps/users/urls.py`         |
| 2026-10-31 | Admin site registered                       | `apps/users/admin.py`                               |
| 2026-10-31 | Unit tests written                          | `apps/users/tests.py` — model + API tests           |
| 2026-10-31 | `django check` passed (0 issues)            | Config is valid                                     |
| 2026-10-31 | Initial migration generated                 | `apps/users/migrations/0001_initial.py`             |
| 2026-10-31 | React + Vite + Tailwind scaffolded manually | `frontend/` — package.json, vite.config.js          |
| 2026-10-31 | `AuthContext` + axios service               | Token storage, auto-attach, 401 handling            |
| 2026-10-31 | Auth pages: Register, Login, ForgotPw, Reset| All 4 pages + role-based redirect on login          |
| 2026-10-31 | `PrivateRoute` component                    | Redirects unauthenticated or wrong-role users       |
| 2026-10-31 | `App.jsx` router                            | Public + protected routes, placeholder dashboards   |
| 2026-10-31 | `.env.example` committed                    | All keys documented, no values                      |

---

## Next Step
- **You**: fill in `backend/.env` with your Supabase credentials (copy from `.env.example`)
- **Then**: run `python manage.py migrate` to apply migrations to Supabase
- **Then**: run `python manage.py createsuperuser` to create the first admin
- **Then**: run `npm install` in `frontend/` and start both servers to test end-to-end

---

## Decisions Made
| Decision                  | Reason                                                    |
|---------------------------|-----------------------------------------------------------|
| Django ORM (not Prisma)   | Django already installed; Prisma is Node.js only          |
| Supabase PostgreSQL        | Already set up by user                                    |
| JWT auth (SimpleJWT)       | Stateless, fits React SPA; avoids session complexity      |
| Custom User model          | Required to use email as USERNAME_FIELD from the start    |

---

## Open Questions
- (none currently)

---

## Known Issues & Resolutions
- (none yet)
