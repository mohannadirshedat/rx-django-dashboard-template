# rxdjango-dashboard

A production-grade Reflex dashboard backed by Django, built on
[reflex-django](https://web7ai.github.io/reflex-django/). The whole UI
is written in Python with [Reflex](https://reflex.dev) and runs in the same ASGI
process as the Django ORM, admin, auth, and migrations — one port, one deploy
artefact, no separate Node server.

## Stack

- **Reflex** — reactive Python UI compiled to a React SPA.
- **Django 6** — ORM, sessions, auth, admin, migrations, management commands.
- **reflex-django** — mounts both into a single ASGI app, provides
  `@template` / `@page` auto-discovery, `AppState`, canned auth pages
  (login / register / password reset), `DjangoContextState`, the upload
  endpoint at `/_upload`, and the WebSocket bridge at `/_event`.
- **uvicorn** + **Vite 7** — runtime server and frontend bundler.
- **SQLite** (default) or **PostgreSQL** + optional **Redis** for multi-worker
  state.

## Pages

| Page | Route | Lives in | Description |
|---|---|---|---|
| Overview | `/` | `analytics/views.py` | KPI cards, area/line/pie charts, acquisition table |
| Transactions | `/transactions` | `items/views.py` | Searchable table with CRUD modals and pagination |
| Profile | `/profile` | `accounts/views.py` | Display name, email, notifications, avatar upload |
| Settings | `/settings` | `core/views.py` | Theme accent / gray colour / radius / scaling |
| About | `/about` | `core/views.py` | Renders this README inside the dashboard shell |
| Login | `/login` | `dashboard/auth.py` | Custom-branded `BaseAuthPage` |
| Register | `/register` | `dashboard/auth.py` | Custom-branded sign-up |
| Password reset | `/password-reset` (+ confirm) | `dashboard/auth.py` | Email-based reset flow |

Authenticated pages set `login_required=True` on the dashboard's `@template`
decorator (see `dashboard/templates/template.py`); anonymous visitors are
redirected to `/login` via `DjangoAuthState.redirect_to_login`.

## Django apps

Every app contributes both Django assets (models, admin, migrations) and Reflex
assets (state, components, pages). reflex-django auto-discovers `views.py` in
each entry of `INSTALLED_APPS`, so adding a new feature is a single new app —
no central page registry to edit.

- **`analytics`** — `KpiSnapshot`, `DailyMetric`, `DeviceShare` models;
  `OverviewState`; charts + stats cards.
- **`items`** — `Transaction` model + `TransactionSerializer`;
  `TransactionState`; the table component with CRUD modals.
- **`accounts`** — `UserProfile` (OneToOne to `auth.User`) with avatar upload;
  `ProfileState`; signals to auto-create profiles on user creation.
- **`core`** — shared UI components (cards, status badges, color/radius/scaling
  pickers, notifications) and the settings + about pages.
- **`dashboard`** — non-Django app holding the shell: navbar, sidebar, the
  custom `@template` decorator, custom auth pages, and shared theme styles.
- **`backend`** — Django project settings, URL routing, ASGI/WSGI entrypoints.

## Project structure

```text
rxdjango-dashboard/
├── README.md
├── Dockerfile
├── docker-compose.yml             # dev: bind-mounted source, run_reflex
├── docker-compose.prod.yml        # prod: uvicorn on :3000, Coolify-ready
├── .env.example
├── pyproject.toml
├── requirements.txt
├── manage.py
├── backend/                       # Django settings, urls, asgi, wsgi
│   ├── settings.py
│   └── urls.py                    # ← reflex_mount(app_name="dashboard")
├── accounts/                      # UserProfile, ProfileState, avatar upload
│   ├── components/
│   ├── state.py
│   ├── views.py                   # /profile page
│   └── models.py
├── analytics/                     # KpiSnapshot, DailyMetric, OverviewState
│   ├── components/
│   ├── state.py
│   ├── views.py                   # / (overview) page
│   ├── management/commands/
│   │   └── seed_demo_metrics.py
│   └── models.py
├── items/                         # Transaction, TransactionState, CRUD
│   ├── components/table.py
│   ├── state.py
│   ├── views.py                   # /transactions page
│   ├── management/commands/
│   │   └── import_transactions.py
│   ├── serializers.py
│   └── models.py
├── core/                          # Shared UI + settings/about pages
│   ├── components/                # card, status_badge, color_picker, …
│   └── views.py                   # /settings, /about pages
├── dashboard/                     # Reflex shell (not a Django app)
│   ├── templates/
│   │   └── template.py            # ← @template decorator + ThemeState
│   ├── components/                # sidebar, navbar
│   ├── auth.py                    # CustomLoginPage / RegisterPage / …
│   ├── views.py                   # Registers the auth pages
│   └── styles.py
└── assets/                        # Static files served at /assets
```

There is **no `rxconfig.py` and no `dashboard/dashboard.py`**: everything
lives in `backend/urls.py` via `reflex_mount(app_name="dashboard", …)` and
reflex-django builds the `rx.App` automatically.

## Getting started

### 1. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate            # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Apply database migrations

```bash
python manage.py migrate
```

### 3. (Optional) Seed demo data

```bash
python manage.py import_transactions
python manage.py seed_demo_metrics
python manage.py createsuperuser
```

### 4. Run the dev server

```bash
python manage.py run_reflex
```

That single command:
- Compiles the SPA into `.web/build/client/` (only when sources change),
- Starts uvicorn on **`http://localhost:8000`**,
- Mounts Django at `/admin/`, `/media/`, and the Reflex SPA + `/_event`
  WebSocket on every other route.

Reload the page after editing Python — Reflex's HMR will rebuild the affected
chunks without restarting Django.

## Docker

```bash
cp .env.example .env                   # adjust DJANGO_SECRET_KEY etc.
```

### Local development

```bash
docker compose up --build
```

Brings up the `dev` image stage with the project source bind-mounted, runs
`python manage.py run_reflex`, exposes **`http://localhost:8000`**. SQLite and
uploaded files persist in named volumes (`dashboard-db`, `dashboard-uploads`).

To enable Postgres and/or Redis (recommended once you want > 1 worker):

```bash
docker compose --profile postgres --profile redis up --build
```

Run management commands inside the container with:

```bash
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed_demo_metrics
```

### Production

The production compose file is **Coolify-ready**: no host port binding (only
`expose: 3000` on the internal Docker network), `SERVICE_FQDN_WEB_3000` magic
env var for automatic FQDN + TLS provisioning, and uvicorn with proxy headers.

```bash
docker compose -f docker-compose.prod.yml up --build
```

| Knob | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | *required* | Server secret. Generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated hosts. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | empty | Comma-separated `https://…` origins. |
| `UVICORN_WORKERS` | `2` | Set higher with Redis + Postgres for parallelism. |
| `SERVICE_FQDN_WEB_3000` | empty | Coolify assigns / rewrites this; managed in the **Domains** tab of the service UI, not the env-vars UI. |
| `REDIS_URL` | empty | `redis://redis:6379/0` when the `redis` profile is enabled. |
| `DJANGO_DB_ENGINE` | `sqlite` | Set to `postgresql` with the `postgres` profile. |

For HTTPS-aware deployments (the usual case behind Coolify, Nginx, Caddy, or a
cloud LB), `backend/settings.py` automatically enables `SECURE_PROXY_SSL_HEADER`,
`SECURE_SSL_REDIRECT`, secure cookies, and HSTS whenever `DJANGO_DEBUG=False`. You
can disable individual knobs with `DJANGO_BEHIND_TLS_PROXY=False`,
`DJANGO_SECURE_SSL_REDIRECT=False`, etc.

### Persistent volumes

| Volume | Mount | Purpose |
|---|---|---|
| `dashboard-db` | `/data` | SQLite database (when `DJANGO_DB_ENGINE=sqlite`) |
| `dashboard-media` | `/app/media` | User uploads (avatars) |
| `dashboard-uploads` | `/app/uploaded_files` | Reflex `/_upload` staging area |
| `dashboard-pgdata` | `/var/lib/postgresql/data` | Postgres data (profile) |
| `dashboard-redis` | `/data` | Redis AOF (profile) |

The entrypoint runs `python manage.py migrate` on every start; static
collection is skipped in production because the SPA is baked into the image at
build time.

## Development notes

### Adding a new page

1. Pick a Django app (or create one). Add the state in `state.py`, components
   in `components/`, and the page function in `views.py`:

   ```python
   import reflex as rx
   from dashboard.templates import template

   @template(route="/reports", title="Reports", login_required=True)
   def reports() -> rx.Component:
       return rx.heading("Reports")
   ```

2. Make sure the app is in `INSTALLED_APPS`. reflex-django auto-discovers
   `views.py` and registers the route.

3. Add the link to the sidebar / navbar (`dashboard/components/sidebar.py`,
   `dashboard/components/navbar.py`).

### Auth-gated pages

Always pass `login_required=True` to the `@template` decorator instead of
stacking `@login_required` on top of it. The dashboard's `@template` wraps the
component body in a `DjangoAuthState` guard before registering the route — an
outer `@login_required` would never reach the Reflex page registry.

### Table CRUD

`TransactionState` (in `items/state.py`) subclasses `AppState` and implements
explicit create / read / update / delete event handlers using
`TransactionSerializer`. No reflex-django CRUD mixins — the explicit pattern is
easier to extend with custom validation, optimistic updates, and toast
notifications.

### Theming

Theme tokens (accent colour, gray colour, radius, scaling) live in
`ThemeState` inside `dashboard/templates/template.py` and are bound directly
into `rx.theme(…)` so every page reacts to changes from `/settings`.

### Django admin and APIs

- Django admin: **`/admin/`** (configured per app in `*/admin.py`).
- User uploads served at **`/media/`** (in dev, and when `SERVE_MEDIA=True`).
- The Reflex WebSocket: **`/_event`**.
- File uploads (`rx.upload`): **`/_upload`** — automatically registered by
  `reflex_django.app_factory._ensure_optional_api_endpoints` at boot.

## Troubleshooting

- **Page stuck on the loading skeleton, browser console shows
  `[reflex-django] No dispatcher for substate '…'` or `h[…] is not a
  function`.** The SPA bundle was compiled before a state class was imported.
  Stop the server, delete `.web/build/` and `.web/utils/state.js`, restart
  `python manage.py run_reflex`, and hard-refresh (Ctrl+Shift+R).
- **`POST /_upload` returns 404.** Update `reflex-django` to 0.5.x or newer;
  the endpoint is registered at runtime via
  `_ensure_optional_api_endpoints`.
- **`TypeError: <var> is not a function` in `recharts` / socket dispatcher.**
  A Vite bundler regression. Pin the version with
  `REFLEX_DJANGO_VITE_VERSION = "7.3.3"` in `backend/settings.py` (already set
  in this project) and rebuild.

## Links

- [reflex-django docs](https://web7ai.github.io/reflex-django/)
- [Reflex](https://reflex.dev)
- [Django](https://www.djangoproject.com/)
