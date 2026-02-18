#!/bin/sh
# Borra todas las tablas de la base (y las migraciones aplicadas) y deja la DB lista para migrate.
# Uso: desde la raíz del proyecto (memory-box-back): ./scripts/reset_db.sh

set -e
cd "$(dirname "$0")/.."

echo "Reseteando base de datos PostgreSQL..."
docker compose exec db sh -c 'psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-memory_box}" -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
"'
echo "Base vacía. Aplicando migraciones..."
docker compose exec web python manage.py migrate --noinput
echo "Listo. Puedes crear superusuario con: docker compose exec web python manage.py createsuperuser"
