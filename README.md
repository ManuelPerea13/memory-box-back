# memory-box-back (Cajita de la Memoria – API)

Backend Django REST Framework para el sistema de pedidos Cajita de la Memoria.

## Estructura (réplica de catriel-back)

```
memory-box-back/
├── src/
│   ├── manage.py
│   ├── memory_box/       # config (settings, urls, wsgi, asgi)
│   ├── pedidos/          # app principal (Pedido, RecorteImagen)
│   └── users/            # admin JWT (Administrador)
├── requirements.txt
├── Dockerfile
└── README.md
```

## Requisitos

- Python 3.11+
- Variables de entorno (opcional): crear `.env` con `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`.

## Uso

### Con Docker Compose (PostgreSQL)

```bash
cp .env.example .env
# Editar .env y ajustar POSTGRES_PASSWORD, SECRET_KEY, etc.
docker compose up -d
docker compose exec web python manage.py createsuperuser  # username + password (como catriel)
```

**Resetear la base (borrar tablas y migraciones aplicadas, dejar una sola migración por app):**
```bash
chmod +x scripts/reset_db.sh
./scripts/reset_db.sh
```

- API: `http://localhost:8000/api/`
- Docs: `http://localhost:8000/docs/swagger/`
- Admin: `http://localhost:8000/admin/`

### Local (SQLite, sin Docker)

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
- Documentación: `http://localhost:8000/docs/swagger/`
- Admin: `http://localhost:8000/admin/`

## Endpoints principales

- `POST /api/api-token-auth/` – Login admin (email, password) → JWT
- `GET/POST /api/pedidos/` – Listar/crear pedidos
- `GET/POST /api/recortes/` – Listar/crear recortes (query `pedido_id`)
