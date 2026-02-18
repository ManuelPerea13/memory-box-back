#!/usr/bin/env python
"""Wait for PostgreSQL to be ready before running migrate/runserver."""
import os
import sys
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memory_box.settings')

try:
    import django
    django.setup()
    from django.db import connection
    from django.db.utils import OperationalError
except ImportError:
    print("Error: Django no está instalado")
    sys.exit(1)

def wait_for_db(max_attempts=30, delay=2):
    for attempt in range(1, max_attempts + 1):
        try:
            connection.ensure_connection()
            print("✓ Base de datos conectada")
            return True
        except OperationalError:
            print(f"Intento {attempt}/{max_attempts}: Esperando base de datos...")
            if attempt < max_attempts:
                time.sleep(delay)
    print("✗ No se pudo conectar a la base de datos")
    return False

if __name__ == '__main__':
    if not wait_for_db():
        sys.exit(1)
