# memory-box-back (Memory Box – API)

Django REST Framework backend for the Memory Box order system.

## Structure

```
memory-box-back/
├── src/
│   ├── manage.py
│   ├── memory_box/       # config (settings, urls, wsgi, asgi)
│   ├── orders/           # main app (Order, ImageCrop)
│   └── users/            # admin JWT (AdminUser)
├── requirements.txt
├── Dockerfile
└── README.md
```

## Requirements

- Python 3.11+
- Environment variables (optional): create `.env` with `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.

## Usage

### With Docker Compose (PostgreSQL)

```bash
cp .env.example .env
# Edit .env and set POSTGRES_PASSWORD, SECRET_KEY, etc.
docker compose up -d
docker compose exec web python manage.py createsuperuser  # username + password
```

**Reset database (drop tables, reapply migrations):**
```bash
chmod +x scripts/reset_db.sh
./scripts/reset_db.sh
```

- API: `http://localhost:8000/api/`
- Docs: `http://localhost:8000/docs/swagger/`
- Admin: `http://localhost:8000/admin/`

### Local (SQLite, no Docker)

```bash
cd src
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py createsuperuser  # username + password
python manage.py runserver
```

- API: `http://localhost:8000/api/`
- Docs: `http://localhost:8000/docs/swagger/`
- Admin: `http://localhost:8000/admin/`

## Main endpoints

- `POST /api/api-token-auth/` – Admin login (email, password) → JWT
- `GET/POST /api/orders/` – List/create orders
- `GET/POST /api/image-crops/` – List/create image crops (query `order_id`)
