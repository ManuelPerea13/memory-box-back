# Checkpoint — back (memory-box)

> Actualizado: 2026-08-06

## Estado general

🟡 En desarrollo. Integrado al dev-panel (web :8104). Estado
real del código sin relevar todavía. Prod corre en mark1
(microk8s, namespace `memory-box-prod`), no en el droplet.

## Último trabajo (2026-08-06)

1. Backup de base de prod: `pg_dump` (postgres:14-alpine, DB
   `memory_box`, 20 tablas) desde pod `memory-box-db` en mark1,
   guardado en `backups/memory_box-20260806-162231.sql.gz` (21 KB,
   dump completo verificado).
2. Migración dominio memory-box.shop: configmap suma
   `https://memory-box.shop` y `https://www.memory-box.shop` a
   `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS`. Aplicado y
   back/celery reiniciados; CORS verificado. El front sigue
   llamando a `https://api.innovbi.site/` (baked en build Next.js)
   — no hace falta rebuild. Cambio directo al cluster, **sin
   commit todavía**. Falta DNS (zona CF) — ver checkpoint del
   front.

## Hecho

- Integrado al dev-panel (web :8104).
- Backup de base de prod en `backups/` (2026-08-06).
- CORS/CSRF con memory-box.shop (2026-08-06).

## Pendiente

- [ ] Completar este checkpoint con el estado real del proyecto
      (leer el código en la próxima tarea).
- [ ] Commit + push de k8s/microk8s/base/configmap.yaml; pull en
      clon de mark1.

## API y datos

<completar en próxima tarea>

## Tests

<completar en próxima tarea>

## Notas / riesgos

<completar en próxima tarea>
