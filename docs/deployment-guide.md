# Guía de despliegue — Expediente Clínico ZOE

Esta guía despliega el sistema en la nube con un stack económico:

| Pieza | Servicio | Free tier | Producción |
|-------|----------|-----------|------------|
| Frontend Next.js | **Vercel** | Gratis | Gratis |
| API FastAPI | **Render** (Docker) | $0 (duerme) | ~$7/mes |
| Base de datos | **Neon** (Postgres serverless) | 0.5 GB | ~$19/mes |
| Archivos/escaneos | **Cloudflare R2** | 10 GB, sin egress | ~$0.015/GB |

> ⚠️ **Datos clínicos reales:** no uses free tiers en producción. El plan
> `free` de Render duerme la API y Neon en free tier tiene límites de
> almacenamiento. Para residentes reales, usa al menos los planes pagos
> mínimos y activa backups en Neon.

El orden importa: **Neon → R2 → Render → Vercel**, porque cada paso produce
un valor que el siguiente necesita.

---

## 1. Base de datos — Neon

1. Crear cuenta en <https://neon.tech> y un proyecto nuevo (región cercana a
   la de Render, p. ej. *US West*).
2. Nombrar la base de datos `zoe_clinic`.
3. En **Connection Details**, elegir la cadena con **Pooled connection**
   (incluye `-pooler` en el host). Copiarla.
4. Asegurarse de que termine en `?sslmode=require`. Queda así:

   ```
   postgresql://usuario:password@ep-xxxx-pooler.us-west-2.aws.neon.tech/zoe_clinic?sslmode=require
   ```

   Ese valor es tu **`DATABASE_URL`**. Guárdalo para el paso 3.

> 💡 **Branching para migraciones:** antes de aplicar una migración nueva en
> producción, crea una *branch* en Neon, corre `alembic upgrade head` contra
> ella, verifica, y solo entonces aplícala a `main`.

---

## 2. Almacenamiento de archivos — Cloudflare R2

1. En el panel de Cloudflare → **R2** → *Create bucket* → nombre
   `zoe-clinic-files`.
2. **Mantener el bucket PRIVADO.** Nunca lo hagas público: los archivos son
   datos clínicos y se sirven mediante *presigned URLs* temporales.
3. **R2 → Manage R2 API Tokens → Create API Token**:
   - Permisos: *Object Read & Write*.
   - Copiar el **Access Key ID** y el **Secret Access Key**.
4. Anotar el **endpoint** de tu cuenta (aparece en la página del bucket):

   ```
   https://<account_id>.r2.cloudflarestorage.com
   ```

Guarda estos cuatro valores para el paso 3:

| Variable | Valor |
|----------|-------|
| `AWS_ACCESS_KEY_ID` | Access Key ID del token R2 |
| `AWS_SECRET_ACCESS_KEY` | Secret Access Key del token R2 |
| `S3_ENDPOINT_URL` | `https://<account_id>.r2.cloudflarestorage.com` |
| `S3_BUCKET_NAME` | `zoe-clinic-files` |

---

## 3. API — Render

El repo ya incluye [`render.yaml`](../render.yaml) y
[`backend/Dockerfile`](../backend/Dockerfile), así que Render configura casi
todo solo.

1. Crear cuenta en <https://render.com> y conectar tu repositorio de GitHub.
2. **New → Blueprint** → seleccionar el repo. Render detecta `render.yaml` y
   propone el servicio `zoe-clinic-api`.
3. Render pedirá los valores marcados como `sync: false`. Pegar:

   | Variable | De dónde sale |
   |----------|---------------|
   | `DATABASE_URL` | Paso 1 (Neon, cadena `-pooler`) |
   | `SECRET_KEY` | Generar uno fuerte (ver abajo) |
   | `AWS_ACCESS_KEY_ID` | Paso 2 (R2) |
   | `AWS_SECRET_ACCESS_KEY` | Paso 2 (R2) |
   | `S3_ENDPOINT_URL` | Paso 2 (R2) |
   | `CORS_ORIGINS` | **Pendiente** — lo llenas tras el paso 4 |

   Para `SECRET_KEY`, generar uno con:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

4. Crear el servicio. En el primer arranque, el contenedor corre
   `alembic upgrade head` (crea las tablas) y levanta la API.
5. Copiar la URL pública que Render asigna, p. ej.
   `https://zoe-clinic-api.onrender.com`. La necesitas para el paso 4.
6. Verificar el health check:

   ```bash
   curl https://zoe-clinic-api.onrender.com/api/v1/health
   # → {"status":"healthy", ...}
   ```

> El `CORS_ORIGINS` se completa al final, cuando ya tengas la URL de Vercel.

---

## 4. Frontend — Vercel

1. Crear cuenta en <https://vercel.com> e importar el mismo repo.
2. En **Root Directory**, seleccionar `admin/` (ahí vive el Next.js).
3. Vercel detecta Next.js automáticamente. En **Environment Variables**:

   | Variable | Valor |
   |----------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://zoe-clinic-api.onrender.com/api/v1` |

4. *Deploy*. Vercel asigna una URL, p. ej.
   `https://zoe-clinic.vercel.app`.

---

## 5. Cerrar el círculo CORS

1. Volver a Render → servicio `zoe-clinic-api` → **Environment**.
2. Setear `CORS_ORIGINS` con la URL de Vercel (sin barra final):

   ```
   CORS_ORIGINS=https://zoe-clinic.vercel.app
   ```

3. Render redespliega solo. Listo: el frontend ya puede llamar a la API.

---

## Checklist post-despliegue

- [ ] `curl .../api/v1/health` responde `healthy`.
- [ ] Login funciona desde el frontend (CORS correcto).
- [ ] Subir un archivo de prueba y verificar que aparece en el bucket R2.
- [ ] Generar un recibo PDF (valida que wkhtmltopdf quedó instalado).
- [ ] Crear el primer usuario admin (ver `backend/app/db/seed.py`).
- [ ] **Producción:** subir de plan `free` a pago en Render y Neon; activar
      backups en Neon.

## Notas de operación

- **Migraciones:** se aplican solas en cada deploy (`alembic upgrade head` en
  el `CMD` del Dockerfile). Para cambios de esquema riesgosos, prueba primero
  en una branch de Neon.
- **Arranque en frío:** con plan `free` de Render la API duerme tras
  inactividad (~50s la primera petición). Neon despierta en ~1s. El plan
  `starter` de Render elimina el sleep.
- **Secretos:** nunca se commitean. Viven solo en los paneles de Render
  (`sync: false`) y Vercel.
