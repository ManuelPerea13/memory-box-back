# Checkpoint — back (memory-box)

> Actualizado: 2026-08-06

## Estado general

🟢 Prod en mark1 (microk8s, namespace `memory-box-prod`), API
servida por mismo origen en https://memory-box.shop/api. Integrado
al dev-panel (web :8104). Estado real del código sin relevar
todavía.

## Último trabajo (2026-08-06)

1. Backup de base de prod: `pg_dump` (postgres:14-alpine, DB
   `memory_box`, 20 tablas) desde pod `memory-box-db` en mark1,
   guardado en `backups/memory_box-20260806-162231.sql.gz` (21 KB,
   dump completo verificado).
2. Migración a memory-box.shop (commit `012b3d2`): configmap con
   `FRONTEND_URL`, CORS y CSRF apuntando solo a memory-box.shop
   (+ www); eliminado el ingress `api.innovbi.site` (manifest y
   objeto vivo) — `/api`, `/media` y `/docs` rutean por el ingress
   del front. Aplicado a mano en mark1 (Actions no disparó ese
   día), back/celery reiniciados, verificado /api 200 mismo origen.

## Hecho

- Integrado al dev-panel (web :8104).
- Backup de base de prod en `backups/` (2026-08-06).
- API por mismo origen en memory-box.shop; innovbi.site fuera
  (2026-08-06).

## Pendiente

- [ ] Completar este checkpoint con el estado real del proyecto
      (leer el código en la próxima tarea).

## Notas / riesgos (2026-08-06)

- Django admin ya no es público: solo LAN via NodePort
  (http://192.168.88.50:30082/admin). `/admin` en el dominio es
  del front.
- `/static` público es del front; los estáticos de Django admin
  quedan detrás del NodePort (whitenoise).

## API y datos

<completar en próxima tarea>

## Tests

<completar en próxima tarea>

## Notas / riesgos

<completar en próxima tarea>
