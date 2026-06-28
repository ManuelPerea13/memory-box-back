import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "memory_box.settings")

app = Celery("memory_box")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Tareas programadas (beat). Vacío por ahora; agregar acá cuando haya
# jobs por cron (ej. recordatorios, limpieza).
app.conf.beat_schedule = {}
