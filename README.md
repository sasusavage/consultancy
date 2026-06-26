# Comfydoe

Flask lead-generation site and admin dashboard for Comfort Doe (advisory, logistics & global trade).

## Stack

- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate (Alembic)
- **Security:** Flask-WTF (CSRF), Flask-Limiter (rate limiting)
- **DB:** PostgreSQL in production, SQLite fallback for local dev
- **Frontend:** Tailwind CSS (compiled locally to `static/css/app.css`)
- **Serving:** Gunicorn (see `Procfile`)

## Local setup

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
npm install                      # for the Tailwind build

cp .env.example .env             # then edit values
```

Run the app:

```bash
python app.py                    # http://localhost:5007
```

## Admin account

There is **no admin password in the environment**. Credentials live in the
database, hashed. Create the first admin once:

```bash
flask create-admin        # prompts for username + password
```

Re-running it for an existing username updates that password. You can also
change your password from the admin dashboard (**Change Password** in the
sidebar) once logged in.

## Tailwind CSS

The compiled stylesheet `static/css/app.css` **is committed**, so deploys don't need Node. Rebuild it whenever you change template classes or the theme:

```bash
npm run build:css        # one-off minified build
npm run watch:css        # rebuild on change during development
```

The color palette / fonts live in `tailwind.config.js`; custom component styles in `static/src/input.css`.

## Database migrations

Schema is managed by Alembic via Flask-Migrate. Migrations live in `migrations/`.

```bash
flask db migrate -m "describe change"   # generate after editing models.py
flask db upgrade                         # apply
```

**Existing production database (already has tables):** run once so Alembic
knows the current state before future upgrades:

```bash
flask db stamp head
```

Fresh databases just need `flask db upgrade`.

## Tests

```bash
pytest
```

Tests run against a temporary SQLite database and cover the public lead form,
validation/anti-spam, auth, lead management, CMS whitelist, CSRF and uploads.

## Environment variables

| Variable         | Required        | Notes                                            |
|------------------|-----------------|--------------------------------------------------|
| `DATABASE_URL`   | prod            | `postgres://` is auto-rewritten to `postgresql://` |
| `SECRET_KEY`     | **prod (hard)** | App refuses to start in production without it    |
| `FLASK_ENV`      | prod            | Set to `production` to enforce the SECRET_KEY check |

Admin credentials are **not** environment variables — see *Admin account* above (`flask create-admin`).
