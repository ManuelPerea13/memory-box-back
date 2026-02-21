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
├── k8s/microk8s/        # deploy en mark1 (base + overlays dev/prod)
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

## Deploy on mark1 (MicroK8s)

Todo lo necesario está en este repo: código + `k8s/microk8s/` (base + overlays dev/prod). En mark1:

1. Clonar con deploy key en `~/workspaces/memory-box/repos/memory-box-back`.
2. Editar `k8s/microk8s/base/secret.yaml` (SECRET_KEY, POSTGRES_PASSWORD) y aplicar:
   ```bash
   docker build -t localhost:32000/memory-box-back:prod .
   docker push localhost:32000/memory-box-back:prod
   microk8s kubectl create namespace memory-box-prod
   microk8s kubectl apply -k k8s/microk8s/overlays/prod -n memory-box-prod
   ```
3. Actualizar: `git pull`, rebuild, push, `kubectl rollout restart deployment memory-box-back -n memory-box-prod`.

## Main endpoints

- `POST /api/api-token-auth/` – Admin login (email, password) → JWT
- `GET/POST /api/orders/` – List/create orders
- `GET/POST /api/image-crops/` – List/create image crops (query `order_id`)
