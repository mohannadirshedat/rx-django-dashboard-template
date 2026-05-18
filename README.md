# rxdjango-dashboard

A Reflex dashboard integrated with Django via [reflex-django](https://github.com/reflex-dev/reflex-django). The UI is built with Reflex; persistence, authentication, and admin are handled by Django.

## Stack

- **Reflex** — reactive UI and routing
- **Django 6** — ORM, auth, sessions, admin
- **reflex-django** — `AppState`, login/register pages, `ReflexDjangoModelSerializer`, and the `ReflexDjangoPlugin` configured in `rxconfig.py`

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Overview | `/` | KPI cards and charts backed by the `analytics` app |
| Table | `/table` | Transaction list with search, sort, pagination, and CRUD modals |
| Profile | `/profile` | Display name, email, notifications, and avatar upload |
| Settings | `/settings` | Theme and appearance options |
| About | `/about` | Project documentation (this file) |

Authentication (login and register) is provided by reflex-django.

## Django apps

- **`items`** — `Transaction` model (`name`, `payment`, `date`, `status`) and `TransactionSerializer`
- **`accounts`** — `UserProfile` (OneToOne to Django’s `User`)
- **`analytics`** — `KpiSnapshot`, `DailyMetric`, `DeviceShare` for dashboard metrics
- **`backend`** — Django settings, URLs, WSGI/ASGI

## Project structure

```text
rxdjango-dashboard/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── rxconfig.py
├── requirements.txt
├── manage.py
├── backend/              # Django settings, urls, wsgi
├── items/                # Transaction model + serializers
├── accounts/             # UserProfile
├── analytics/            # Dashboard metrics
├── dashboard/            # Reflex app
│   ├── pages/            # index, table, profile, settings, about
│   ├── state/            # AppState classes (overview, profile, transactions)
│   ├── views/            # charts, table + CRUD modals
│   ├── components/       # sidebar, navbar, cards, etc.
│   └── templates/        # @template layout wrapper
└── assets/
```

## Getting started

1. Create and activate a virtual environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Install `reflex-django` if it is not already included in your environment.

2. Apply database migrations:

```bash
reflex django migrate
```

Or:

```bash
python manage.py migrate
```

3. Seed demo data (optional):

```bash
python manage.py import_transactions
python manage.py seed_demo_metrics
```

4. Run the development server:

```bash
reflex run
```

## Docker

Copy the example environment file and adjust values as needed (especially `DJANGO_SECRET_KEY` for production):

```bash
cp .env.example .env
```

### Local development

Runs `reflex run` with the Vite dev server on port **3000** and the ASGI backend on port **8000**. Source is bind-mounted for hot reload; SQLite and uploads persist in named volumes.

```bash
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000) (Django admin and API are proxied from the frontend URL).

First-time setup inside the container (optional demo data):

```bash
docker compose run --rm web reflex django migrate
docker compose run --rm web python manage.py import_transactions
docker compose run --rm web python manage.py seed_demo_metrics
```

### Production

Single-port mode on **8080** with `reflex run --env prod`. Set `DJANGO_DEBUG=0` and a strong `DJANGO_SECRET_KEY` in `.env` before starting.

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

Open [http://localhost:8080](http://localhost:8080).

Persistent volumes:

| Volume | Mount | Purpose |
|--------|-------|---------|
| `dashboard-db` | `/data` | SQLite database (`DJANGO_DB_PATH`) |
| `dashboard-media` | `/app/media` | User uploads (avatars) |
| `dashboard-static` | `/app/staticfiles` | Collected Django static files |

The entrypoint runs migrations on every start; production also runs `collectstatic` when `RUN_COLLECTSTATIC=1`.

## Development notes

### Adding a page

1. Add a module under `dashboard/pages/` with a function decorated by `@template(route=..., title=...)`.
2. Import the page in `dashboard/pages/__init__.py`.
3. Add the route to `ordered_page_routes` in `dashboard/components/sidebar.py` and `dashboard/components/navbar.py`.

### Table CRUD

The Table page uses `TransactionState` (`dashboard/state/transactions.py`), which subclasses `AppState` (not `ModelState`). Create, read, update, and delete run through explicit event handlers and `items/serializers.py` — no reflex-django CRUD mixins.

### Django admin and API

Configured in `rxconfig.py` via `ReflexDjangoPlugin`:

- Django admin: `/admin`
- API prefix: `/api`
- Media files: `/media`

## Links

- [Reflex documentation](https://reflex.dev/docs)
- [reflex-django on GitHub](https://github.com/reflex-dev/reflex-django)
