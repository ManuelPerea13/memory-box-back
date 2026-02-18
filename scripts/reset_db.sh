#!/bin/sh
# Drops all tables and resets the database. Leaves DB ready for migrate.
# Usage: from project root (memory-box-back): ./scripts/reset_db.sh

set -e
cd "$(dirname "$0")/.."

echo "Resetting PostgreSQL database..."
docker compose exec db sh -c 'psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-memory_box}" -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
"'
echo "Empty database. Applying migrations..."
docker compose exec web python manage.py migrate --noinput
echo "Creating superuser admin..."
docker compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'Prueba1234')
    print('Superuser admin created successfully.')
else:
    print('Superuser admin already existed.')
"
echo "Done."
