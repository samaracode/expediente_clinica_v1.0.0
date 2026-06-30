# Plan: Expediente Clínico ZOE — Backbone Inicial

## Context

Digitalizar el expediente físico de papel de la clínica de rehabilitación Hogar Zoé (Asociación Centro Cristiano Canaán, Costa Rica). El expediente actual es 100% en papel; este sistema lo reemplaza con un flujo digital completo. El backbone cubre: monorepo, base de datos PostgreSQL, API FastAPI, frontend Next.js con TailAdmin, y Makefile como punto de entrada único para todos los comandos de desarrollo.

Conversaciones en español. Todo el código en inglés.

---

## Stack Confirmado

| Capa          | Tecnología                                                              |
| ------------- | ----------------------------------------------------------------------- |
| Frontend      | Next.js + TailAdmin Pro (fuente en `template/`, se trabaja en `admin/`) |
| Backend       | FastAPI (Python) con pip + venv                                         |
| Base de datos | PostgreSQL instalado localmente                                         |
| Archivos      | AWS S3 (boto3, credenciales en .env)                                    |
| Auth          | JWT (generado en FastAPI)                                               |
| Comandos      | GNU Make                                                                |

---

## Nota sobre TailAdmin Pro

El usuario colocará los archivos de TailAdmin Pro en `template/`. El comando `make setup-admin` copia el contenido a `admin/` e instala dependencias. El código propio del proyecto vive en `admin/src/` (componentes, páginas, API client); los componentes de TailAdmin se usan sin modificar.

---

## Estructura de Directorios

```
expediente_clinica_v1.0.0/
├── template/               # TailAdmin Pro (fuente — el usuario la copia aquí)
├── admin/                  # Next.js + TailAdmin Pro (se inicializa desde template/)
│   ├── src/
│   │   ├── app/            # App Router de Next.js
│   │   ├── components/     # Componentes TailAdmin + custom
│   │   ├── lib/            # API client (fetch wrapper), utils
│   │   └── types/          # TypeScript types (espejo de schemas Pydantic)
│   ├── package.json
│   └── .env.local
├── backend/                # FastAPI
│   ├── app/
│   │   ├── main.py         # Entry point, CORS, routers
│   │   ├── api/v1/         # Endpoints por módulo
│   │   │   ├── router.py
│   │   │   ├── auth.py
│   │   │   ├── residents.py
│   │   │   ├── admissions.py
│   │   │   ├── consents.py
│   │   │   ├── medical.py
│   │   │   ├── therapeutic.py
│   │   │   ├── social_work.py
│   │   │   ├── psychology.py
│   │   │   ├── occupational_therapy.py
│   │   │   ├── treatment_plans.py
│   │   │   ├── exit_passes.py
│   │   │   ├── daily_logs.py
│   │   │   ├── files.py
│   │   │   └── users.py
│   │   ├── core/
│   │   │   ├── config.py   # Settings via pydantic-settings (.env)
│   │   │   ├── security.py # JWT encode/decode, bcrypt hashing
│   │   │   └── deps.py     # FastAPI deps: get_db, get_current_user, role_required
│   │   ├── db/
│   │   │   ├── base.py     # Base declarativa SQLAlchemy
│   │   │   └── session.py  # engine, SessionLocal, get_db
│   │   ├── models/         # SQLAlchemy ORM models
│   │   │   ├── resident.py
│   │   │   ├── admission.py
│   │   │   ├── consent.py
│   │   │   ├── medical.py
│   │   │   ├── assessment.py
│   │   │   ├── treatment.py
│   │   │   ├── follow_up.py
│   │   │   ├── user.py
│   │   │   └── file.py
│   │   └── schemas/        # Pydantic v2 schemas
│   │       ├── resident.py
│   │       ├── admission.py
│   │       ├── consent.py
│   │       └── ...
│   ├── alembic/            # Migraciones de base de datos
│   │   ├── env.py
│   │   └── versions/
│   ├── requirements.txt
│   └── .env
├── docs/
│   └── initial_docs/       # Formularios físicos escaneados (fuente de verdad)
├── Makefile
├── .env.example
└── README.md
```

---

## Makefile — Comandos Principales

```makefile
setup          # primera vez: setup-admin + setup-backend
setup-admin    # copia template/ → admin/ + npm install
setup-backend  # crea venv, pip install -r requirements.txt

dev            # levanta backend + frontend concurrentemente (un solo comando)
dev-backend    # solo FastAPI (uvicorn --reload, puerto 8000)
dev-admin      # solo Next.js (puerto 3000)

db-migrate     # alembic upgrade head
db-revision    # alembic revision --autogenerate -m "$(msg)"
db-reset       # drop + recreate DB + migrate (solo dev, pide confirmación)
seed           # datos iniciales: usuario admin, etapas de tratamiento

test           # pytest + jest
lint           # ruff (backend) + eslint (frontend)
```

> PostgreSQL local: el `.env` define `DATABASE_URL`. No se necesita Docker.

---

## Modelo de Base de Datos — Entidades Principales

### `residents`

id, code (único auto-generado), first_name, last_name, id_number, birthdate, sex, marital_status, nationality, province, canton, district, neighborhood, address_other, phone_home, phone_mobile, emergency_contact_name, emergency_contact_phone, is_insured, insurance_type, photo_file_id, created_at, updated_at

### `family_members`

id, resident_id, full_name, relationship, age

### `education_records`

id, resident_id, level (primary/secondary/other), academic_grade, year_attended, institution_name

### `admissions`

id, resident_id, admission_number, admission_type (first/readmission), admission_date, discharge_date, discharge_reason, assigned_counselor_id, status (intake_pending / consents_pending / assessment_in_progress / treatment_active / discharged / abandoned), referral_source, admission_condition, initial_diagnosis, sponsor_name, sponsor_relationship, sponsor_phone, sponsor_address, judicial_status, has_support_network, created_at, updated_at

### `economic_situations` (snapshot por admisión)

id, admission_id, has_worked, current_job, work_phone, workplace, job_title, tenure_months, monthly_income_colones, house_type (rented/owned/borrowed), rent_amount, family_income_data (JSONB), financial_assistance_data (JSONB)

### `household_members` (snapshot por admisión)

id, admission_id, full_name

### `consumption_snapshots` (snapshot por admisión)

id, admission_id, age_first_use, primary_drug, drug_use_frequency, other_drugs (JSONB), previous_internments_count, previous_internment_places (JSONB), worst_experience, history_notes

### `consent_records`

id, admission_id, consent_type (ENUM: INTERNMENT_SERVICE, INTERNMENT, SEARCH, DRUG_TEST, CCTV, INFO_RELEASE, WEAPONS, IAFA_ACTIONS, INDIVIDUAL_APPROACH, REFERRAL, RECORD_ACCESS, RIGHTS_FOCUS, LABOR, NON_DISCRIMINATION, SPONSOR, MANUAL, LABOR_PROVISION), is_signed, signed_at, verified_by_user_id, authorized_persons (JSONB, para INFO_RELEASE), notes, file_id

### `personal_items_inventories`

id, admission_id, recorded_at, recorded_by_user_id, items (JSONB), notes, user_signature_file_id, staff_signature_file_id

### `medical_records`

id, admission_id, social_security_validated, iafa_icd_data (JSONB), completion_status

### `drug_tests`

id, medical_record_id, test_date, result, notes, file_id

### `medication_logs`

id, medical_record_id, treatment_type (internal/external), medication_name, dosage, frequency, prescribed_by, start_date, end_date, notes

### `therapeutic_assessments`

id, admission_id, assessor_id, assessment_date, initial_summary, clinical_history_summary, europal_si_data (JSONB), socrates_data (JSONB), urica_data (JSONB), afc_analysis (JSONB), relapse_prevention_interview, relapse_prevention_plan, completion_status

### `social_work_assessments`

id, admission_id, social_worker_id, assessment_date, diagnostic_impression, initial_assessment, completion_status

### `psychology_assessments`

id, admission_id, psychologist_id, assessment_date, initial_diagnostic_impression, observable_assessment, diagnostic_tests (JSONB), completion_status

### `occupational_therapy_assessments`

id, admission_id, therapist_id, assessment_date, initial_diagnostic_impression, occupational_profile, completion_status

### `treatment_plans`

id, admission_id, created_by_id, recommendations, plan_details, life_project, created_at, updated_at

### `treatment_stages`

id, treatment_plan_id, stage_name (ENUM: orientation/adaptation/development/consolidation/reintegration), stage_order, start_date, end_date, progress_notes, extension_consent_signed, advancement_criteria, status (pending/active/completed/extended)

### `exit_passes`

id, admission_id, requested_at, approved_by_id, departure_date, return_date_expected, return_date_actual, reason, narrative, companion, pass_type (regular/special), status (pending/approved/rejected/completed)

### `daily_logs`

id, admission_id, logged_by_id, log_date, intervention_type, notes, recommendations

### `family_therapy_sessions`

id, admission_id, therapist_id, session_date, attendees (JSONB), session_type (family/individual), notes

### `program_abandonments`

id, admission_id, abandoned_at, reason, notes, staff_notified_id

### `complaints`

id, admission_id, reported_at, description, resolution, resolved_at, resolved_by_id

### `treatment_areas` ← configurable, no hardcodeada

id, name (medicine/therapeutic/social_work/psychology/occupational_therapy), description

### `professionals`

id, user_id, area_id, first_name, last_name, specialty, is_active

### `relatives` ← entidad de primer nivel con perfil completo

id, id_number, first_name, last_name, birthdate, marital_status, address, judicial_situation, phone, education_level

### `patient_relatives` ← tabla puente

id, resident_id, relative_id, relationship

### `consultations` ← citas de seguimiento por área

id, admission_id, professional_id, area_id, consultation_type, description, observations, next_appointment_date, consultation_date

### `audit_logs` ← trazabilidad para cumplimiento IAFA

id, user_id, operation_type (CREATE/UPDATE/DELETE), table_affected, record_id, timestamp

### `users`

id, full_name, email, hashed_password, role (ENUM: admin/counselor/medical/social_worker/psychologist/occupational_therapist/receptionist), is_active, created_at

### `files`

id, s3_key, s3_bucket, file_name, mime_type, entity_type, entity_id, uploaded_by_id, uploaded_at

---

## Flujo de Admisión (lógica de negocio)

```
intake_pending      → crear admisión, capturar datos generales
consents_pending    → firmar todos los consentimientos requeridos (bloquea avance)
assessment_in_progress → 5 secciones en paralelo (medical, therapeutic, social_work,
                         psychology, occupational_therapy). Cuando todas = completed
treatment_active    → plan de tratamiento activo, etapas, logs diarios habilitados
discharged/abandoned → cierre del episodio
```

---

## API — Estructura de Rutas

```
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh

GET    /api/v1/residents          (search, pagination)
POST   /api/v1/residents
GET    /api/v1/residents/{id}
PUT    /api/v1/residents/{id}
GET    /api/v1/residents/{id}/admissions

POST   /api/v1/admissions
GET    /api/v1/admissions/{id}
PUT    /api/v1/admissions/{id}/status

GET    /api/v1/admissions/{id}/consents
POST   /api/v1/admissions/{id}/consents/{type}/sign

GET/PUT /api/v1/admissions/{id}/personal-items
GET/PUT /api/v1/admissions/{id}/economic-situation
GET/PUT /api/v1/admissions/{id}/medical
GET/PUT /api/v1/admissions/{id}/therapeutic
GET/PUT /api/v1/admissions/{id}/social-work
GET/PUT /api/v1/admissions/{id}/psychology
GET/PUT /api/v1/admissions/{id}/occupational-therapy
GET/PUT /api/v1/admissions/{id}/treatment-plan

GET    /api/v1/admissions/{id}/exit-passes
POST   /api/v1/admissions/{id}/exit-passes
PUT    /api/v1/exit-passes/{id}

GET    /api/v1/admissions/{id}/daily-logs
POST   /api/v1/admissions/{id}/daily-logs

POST   /api/v1/files/upload-url  (genera presigned URL de S3)
GET    /api/v1/files/{id}

GET    /api/v1/admissions/{id}/consultations
POST   /api/v1/admissions/{id}/consultations
PUT    /api/v1/consultations/{id}

GET    /api/v1/residents/{id}/relatives
POST   /api/v1/residents/{id}/relatives
PUT    /api/v1/relatives/{id}

GET    /api/v1/reports/admissions          (reporte de ingresos)
GET    /api/v1/reports/consultations       (reporte de citas)
GET    /api/v1/reports/treatment-progress  (evolución de pacientes)

GET    /api/v1/users             (admin only)
POST   /api/v1/users
PUT    /api/v1/users/{id}

GET    /api/v1/professionals     (admin only)
POST   /api/v1/professionals
PUT    /api/v1/professionals/{id}
```

---

## Hallazgos de initial_docs — Lo que cambió en el plan

De la imagen del diagrama de base de datos (Sistema Canaán) y el Acta de Constitución (SIGP):

| Módulo faltante                          | Fuente                     | Impacto en plan                           |
| ---------------------------------------- | -------------------------- | ----------------------------------------- |
| `consultations` (citas/seguimiento)      | Acta + Diagrama `Consulta` | Nueva tabla + endpoints                   |
| `audit_logs`                             | Diagrama `Auditoria`       | Nueva tabla, se auto-llena via middleware |
| `treatment_areas` configurable           | Diagrama `AreaTratamiento` | Tabla en lugar de enum hardcodeado        |
| `professionals` (perfil del profesional) | Diagrama `Profesional`     | Separado de `users`                       |
| `relatives` como entidad completa        | Diagrama `Familiar`        | Propia tabla con perfil completo          |
| Reportes básicos                         | Acta entregables           | 3 endpoints de reporting                  |

El diagrama también sugería un patrón `EventoClinico` como eje central. Se descartó en favor del enfoque `admission`-céntrico (más simple, mismo resultado para el alcance de este proyecto).

Detalles absorbidos del diseño de Sebastián:

- `admission_condition` + `initial_diagnosis` → en `admissions`
- `recommendations` → en `daily_logs`
- `treatment_type` (internal/external) → en `medication_logs`

---

## Frontend — Sistema de Diseño (TailAdmin Pro + Tailwind)

### Paleta de Colores (Healthcare / Accessible & Ethical)

| Rol           | Color          | Hex       |
| ------------- | -------------- | --------- |
| Primary       | Teal médico    | `#0891B2` |
| Secondary     | Teal claro     | `#22D3EE` |
| CTA / Success | Verde salud    | `#22C55E` |
| Background    | Menta suave    | `#F0FDFA` |
| Text          | Verde oscuro   | `#134E4A` |
| Error         | Rojo accesible | `#DC2626` |
| Warning       | Ámbar          | `#D97706` |

Extender en `tailwind.config.ts` como `colors.brand.*` para uso consistente en todo el proyecto.

### Tipografía

- **Headings:** Figtree (300–700) — limpia, médica, confiable
- **Body:** Noto Sans (300–700) — máxima legibilidad, accesible
- Tamaño mínimo body: 16px. Line-height: 1.5–1.75
- Google Fonts importado en `admin/src/app/layout.tsx`

### Estilo Base

- WCAG AAA compliant (contraste 4.5:1 mínimo en texto normal)
- Focus rings visibles de 3px en todos los interactivos
- Touch targets mínimo 44×44px
- Sin emojis como iconos → usar Heroicons / Lucide
- Sin animaciones agresivas → `prefers-reduced-motion` respetado
- Transiciones: 150–300ms en micro-interacciones

### Páginas y Componentes Clave

```
admin/src/app/
├── (auth)/
│   └── login/page.tsx          ← pantalla de login, sin sidebar
├── (dashboard)/
│   ├── layout.tsx              ← sidebar + navbar de TailAdmin
│   ├── page.tsx                ← dashboard principal (por rol)
│   ├── residents/
│   │   ├── page.tsx            ← lista/búsqueda de residentes
│   │   ├── new/page.tsx        ← nuevo residente
│   │   └── [id]/
│   │       ├── page.tsx        ← perfil del residente
│   │       └── admissions/
│   │           ├── new/page.tsx         ← nueva admisión (multi-step)
│   │           └── [admissionId]/
│   │               ├── page.tsx         ← resumen de admisión
│   │               ├── consents/        ← consentimientos
│   │               ├── medical/         ← sección médica
│   │               ├── therapeutic/     ← área terapéutica
│   │               ├── social-work/
│   │               ├── psychology/
│   │               ├── occupational-therapy/
│   │               ├── treatment-plan/
│   │               ├── exit-passes/
│   │               └── daily-logs/
│   ├── consultations/page.tsx  ← agenda de citas
│   ├── reports/page.tsx        ← reportes básicos
│   └── admin/
│       ├── users/page.tsx
│       └── professionals/page.tsx
```

### UX Patterns para Personal Clínico

- **Multi-step admission form:** barra de progreso "Paso 2 de 6", botones Anterior/Siguiente, auto-save por paso
- **Indicadores de estado del expediente:** checklist visual en el perfil de admisión (qué secciones están completas)
- **Formularios:** siempre `<label>` explícito, nunca solo placeholder; errores con `role="alert"` + ícono + texto
- **Botones de submit:** estado loading (spinner + disable) durante operaciones async
- **Consentimientos:** tabla con badge de estado (Pendiente / Firmado + fecha)
- **Dashboard por rol:** cada rol ve solo lo relevante a su área

---

## Autenticación — Arquitectura Completa

### Flujo JWT

```
1. POST /api/v1/auth/login  →  { access_token, token_type }
2. Token guardado en httpOnly cookie (NO localStorage — seguridad)
3. Cada request incluye cookie automáticamente
4. Backend valida token en dep get_current_user
5. Refresh: POST /api/v1/auth/refresh antes de expirar
```

### Next.js — Protección de Rutas (middleware.ts)

```
middleware.ts (raíz de admin/)
  ├── Lee token de cookie
  ├── Si no existe → redirect a /login
  ├── Decodifica payload (role)
  ├── Si role no tiene acceso a la ruta → redirect a /unauthorized
  └── Pasa token en header X-User-Role al backend

Matriz de acceso por ruta:
  /dashboard/admin/*           → solo admin
  /dashboard/residents/*/medical/*  → admin, medical, counselor
  /dashboard/residents/*/therapeutic/* → admin, counselor, therapist
  /dashboard/residents/*/social-work/* → admin, social_worker
  /dashboard/residents/*/psychology/* → admin, psychologist
  /dashboard/residents/*/occupational-therapy/* → admin, occupational_therapist
  /dashboard/residents/* (lectura) → todos los roles
```

### FastAPI — Seguridad

```python
# backend/app/core/security.py
- bcrypt para hashing de contraseñas (passlib)
- JWT con python-jose: HS256, exp en payload
- ACCESS_TOKEN_EXPIRE: configurable en .env (default 8h turno clínico)

# backend/app/core/deps.py
- get_current_user: extrae y valida JWT del header Authorization
- role_required(roles): decorador/dep que verifica rol del usuario
- get_db: inyecta sesión de DB con context manager

# Audit log automático:
- Middleware FastAPI intercepta POST/PUT/DELETE
- Escribe en audit_logs: user_id, operation, table, record_id, timestamp
```

### Cookies httpOnly (seguridad)

- El endpoint `/auth/login` setea `Set-Cookie: access_token=...; HttpOnly; SameSite=Lax; Secure`
- El frontend **nunca** accede al token directamente
- El logout limpia la cookie en el servidor

---

## Variables de Entorno (.env.example)

```
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/zoe_clinic
SECRET_KEY=changeme
ACCESS_TOKEN_EXPIRE_MINUTES=480
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=zoe-clinic-files

# Frontend (admin/.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Fases de Implementación

### Fase 1 — Modelos de BD, Migración y Seed

Crear `backend/app/models/` con 10 archivos (uno por dominio), actualizar `db/base.py` para importarlos todos, generar migración real con `alembic revision --autogenerate`, y crear `backend/app/db/seed.py`.

El seed crea:
- Usuario admin: `admin@zoe.clinica` / `Admin1234!`
- 5 `TreatmentArea`: medicine, therapeutic, social_work, psychology, occupational_therapy

Agregar target `seed` al Makefile:
```makefile
seed:
    cd backend && $(PYTHON) -m app.db.seed
```

### Fase 2 — Autenticación (Backend + Frontend)

**Backend:**
- `backend/app/schemas/user.py` — `UserLogin`, `Token`, `UserOut`
- `backend/app/api/v1/auth.py`:
  - `POST /api/v1/auth/login` → valida credenciales, JWT en httpOnly cookie + body
  - `POST /api/v1/auth/logout` → limpia la cookie
  - `GET  /api/v1/auth/me` → usuario actual autenticado
- Actualizar `deps.py` para consultar `User` real en BD (reemplaza mock)
- `backend/app/api/v1/router.py` + registrar en `main.py`

**Frontend:**
- `admin/src/lib/api.ts` — fetch wrapper con `credentials: "include"` (cookie automática)
- `admin/src/types/index.ts` — tipos TypeScript espejo de los schemas Pydantic
- `admin/src/context/AuthContext.tsx` — estado `user`, funciones `login()` y `logout()`
- Adaptar signin page existente para llamar a `AuthContext.login()`
- `admin/src/middleware.ts` — protege rutas `/(admin)/`, redirige a `/signin` si no hay cookie
- Agregar `<AuthProvider>` en `admin/src/app/layout.tsx`

### Fase 3 — Residentes y Admisiones (Backend + Frontend)

**Backend:**
- `backend/app/schemas/resident.py` — `ResidentCreate`, `ResidentUpdate`, `ResidentOut`, `ResidentList`
- `backend/app/schemas/admission.py` — `AdmissionCreate`, `AdmissionOut`
- `backend/app/api/v1/residents.py`:
  - `GET  /api/v1/residents` — lista paginada, búsqueda por nombre/cédula
  - `POST /api/v1/residents` — crear residente
  - `GET  /api/v1/residents/{id}` — perfil completo
  - `PUT  /api/v1/residents/{id}` — actualizar datos demográficos
  - `GET  /api/v1/residents/{id}/admissions` — historial
- `backend/app/api/v1/admissions.py`:
  - `POST /api/v1/admissions` — crear admisión (status: `intake_pending`)
  - `GET  /api/v1/admissions/{id}` — detalle
  - `PUT  /api/v1/admissions/{id}/status` — avanzar en el flujo

**Frontend:**
- Nuevas rutas bajo `admin/src/app/(admin)/`:
  - `residents/page.tsx` — tabla de residentes (reutiliza `DataTableTwo`)
  - `residents/new/page.tsx` — formulario nuevo residente
  - `residents/[id]/page.tsx` — perfil + lista de admisiones
  - `residents/[id]/admissions/new/page.tsx` — nueva admisión
- Componentes en `admin/src/components/residents/`:
  - `ResidentTable.tsx`, `ResidentForm.tsx`, `AdmissionForm.tsx`, `AdmissionStatusBadge.tsx`
- Agregar sección "Clínica" con Residentes en la navegación del sidebar

---

## Verificación del Sistema (Fases 1–3)

```bash
make db-migrate         # 22+ tablas creadas sin errores
make seed               # "Admin creado" + "5 áreas creadas"
make dev-backend        # /docs muestra módulos Auth + Residents + Admissions
make dev-admin          # localhost:3000 → redirect a /signin
```

Smoke test en browser:
1. Login con `admin@zoe.clinica` / `Admin1234!` → redirige al dashboard
2. Navegar a `/residents` → tabla vacía visible
3. Crear nuevo residente → aparece en la tabla
4. Crear admisión para ese residente → status `intake_pending`
5. Login con credenciales incorrectas → error 401 visible
6. `POST /api/v1/auth/login` correcto → cookie `access_token` seteada como httpOnly
7. Revisar `audit_logs` en DB después de crear un residente → registro automático presente

---

### Fase 4 — Módulos Clínicos, Admin y Reportes ✅ IMPLEMENTADO

Todos los módulos del expediente clínico por admisión, el panel de administración y los reportes básicos.

**Backend implementado:**
- `consents.py` — GET lista + POST firmar por tipo
- `personal_items.py` — GET/PUT inventario de pertenencias
- `economic_situation.py` — GET/PUT situación económica
- `medical.py` — GET/PUT evaluación médica (pruebas de droga + medicamentos)
- `therapeutic.py` — GET/PUT evaluación terapéutica
- `social_work.py` — GET/PUT trabajo social
- `psychology.py` — GET/PUT psicología
- `occupational_therapy.py` — GET/PUT terapia ocupacional
- `treatment.py` — GET/PUT plan de tratamiento con etapas
- `exit_passes.py` — GET lista + POST crear + PUT estado
- `daily_logs.py` — GET lista + POST crear + PUT editar
- `consultations.py` — GET/POST por admisión + PUT por id
- `relatives.py` — GET/POST por residente + PUT por patient_relative_id (deduplicación por cédula)
- `professionals.py` — GET/POST/PUT profesionales + GET áreas
- `users.py` — GET/POST/PUT usuarios (admin)
- `reports.py` — GET ingresos / GET consultas / GET progreso de tratamiento

**Frontend implementado:**
- `/admissions/[id]/` — hub de secciones del expediente
- `/admissions/[id]/consents` — tabla de consentimientos con firma inline
- `/admissions/[id]/personal-items` — inventario dinámico
- `/admissions/[id]/economic-situation` — formulario situación económica
- `/admissions/[id]/medical` — evaluación médica con sub-listas
- `/admissions/[id]/therapeutic` — evaluación terapéutica
- `/admissions/[id]/social-work` — trabajo social
- `/admissions/[id]/psychology` — psicología
- `/admissions/[id]/occupational-therapy` — terapia ocupacional
- `/admissions/[id]/treatment-plan` — plan de tratamiento con etapas y progreso
- `/admissions/[id]/exit-passes` — permisos de salida con flujo de aprobación
- `/admissions/[id]/daily-logs` — notas diarias con edición inline
- `/admissions/[id]/consultations` — consultas de seguimiento con edición inline
- `/residents/[id]/relatives` — red familiar con tarjetas expandibles
- `/admin/users` — gestión de usuarios y roles
- `/admin/professionals` — gestión de profesionales por área
- `/reports` — dashboard 3 pestañas: ingresos, consultas, progreso

---

### Fase 5 — Búsqueda, Filtros y Paginación

**Objetivo:** Hacer usable el sistema cuando haya decenas o cientos de registros.

**Backend:**
- `GET /residents` — agregar `q` (búsqueda por nombre o cédula), `page`, `page_size` (default 20). Retornar `{ items: [...], total: int, page: int, pages: int }`
- `GET /admissions/resident/{id}` — paginación opcional
- `GET /admissions/{id}/daily-logs` — filtro por rango de fechas (`from_date`, `to_date`)
- `GET /admissions/{id}/consultations` — filtro por área o profesional
- `GET /admissions/{id}/exit-passes` — filtro por estado

**Frontend:**
- `residents/page.tsx` — campo de búsqueda en tiempo real (debounce 300ms) + controles de paginación (Anterior / Página X de N / Siguiente)
- `admissions/[id]/daily-logs` — filtro de fecha (desde / hasta)
- `admissions/[id]/consultations` — filtro por área
- Componente reutilizable `Pagination.tsx` en `components/ui/`

---

### Fase 6 — Control de Acceso por Rol (Enforcement Frontend)

**Objetivo:** Cada rol solo accede a lo que le corresponde. Actualmente el middleware protege login, pero no granularidad por sección.

**Matriz de acceso por ruta (ya definida en el plan, pendiente de implementar):**

| Ruta | Roles con acceso |
|------|-----------------|
| `/admin/*` | admin |
| `/admissions/[id]/medical` | admin, medical, counselor |
| `/admissions/[id]/therapeutic` | admin, counselor |
| `/admissions/[id]/social-work` | admin, social_worker |
| `/admissions/[id]/psychology` | admin, psychologist |
| `/admissions/[id]/occupational-therapy` | admin, occupational_therapist |
| `/admissions/[id]/daily-logs` | todos (solo escriben su rol) |
| `/residents/*` (lectura) | todos |

**Frontend:**
- `admin/src/middleware.ts` — ampliar la lógica actual para enforcer la matriz de acceso por ruta
- `AuthContext` — exponer `hasAccess(route: string): boolean` helper
- En páginas sensibles: mostrar mensaje "Sin acceso" en lugar de redirigir (mejor UX para navegación directa por URL)
- Sidebar: ocultar secciones de Admin para roles no-admin

**Backend:**
- Agregar `role_required(["admin"])` dep a endpoints de `users.py` y `professionals.py` que ya lo necesitan
- Agregar `role_required(["admin", "medical", "counselor"])` a endpoints médicos

---

### Fase 7 — Borrado Lógico (Archivar / Eliminar)

**Objetivo:** Permitir corregir errores sin destruir datos históricos. Nunca DELETE físico en producción.

**Patrón:** `is_deleted: bool = False` + `deleted_at: datetime | None` en las tablas afectadas. Todos los GET filtran `WHERE is_deleted = false`.

**Entidades con borrado lógico:**
- `residents` — archivar residente (oculta de la lista activa, mantiene historial)
- `admissions` — solo admin puede archivar admisiones erróneas
- `daily_logs` — eliminar nota errónea del día
- `exit_passes` — cancelar permiso
- `consultations` — eliminar consulta duplicada o errónea
- `patient_relatives` — desvincular familiar (no borra el `Relative` base)

**Backend (por entidad):**
- `DELETE /residents/{id}` — soft delete (requiere rol admin)
- `DELETE /admissions/{id}` — soft delete (requiere rol admin)
- `DELETE /daily-logs/{id}` — soft delete (usuario que lo creó o admin)
- `DELETE /consultations/{id}` — soft delete (admin)
- `DELETE /relatives/{patient_relative_id}` — desvincula (borra `PatientRelative`, no `Relative`)

**Frontend:**
- Botón "Archivar" (con modal de confirmación) en perfil de residente
- Botón "Eliminar" (con confirmación) en filas de notas diarias, consultas
- Residentes archivados: toggle "Mostrar archivados" en la lista
- Admisión errónea: solo admin ve el botón, requiere confirmación de texto

---

### Fase 8 — Exportar / Imprimir Expediente a PDF

**Objetivo:** Generar un PDF del expediente completo de una admisión para impresión o archivo físico (requerimiento IAFA).

**Opción elegida:** Generación en backend con WeasyPrint (renderiza HTML→PDF, soporte completo CSS). Alternativa más simple: endpoint que retorna HTML con `@media print` styles, el navegador imprime.

**Backend:**
- Instalar `weasyprint` (o `reportlab` como fallback más ligero)
- `GET /admissions/{id}/export/pdf` — compila todos los datos de la admisión, renderiza template Jinja2 HTML, retorna `application/pdf`
- Template HTML en `backend/app/templates/admission_report.html` — layout de impresión A4 con logo ZOE, secciones del expediente

**Frontend:**
- Botón "Exportar PDF" en la página hub de admisión (`/admissions/[id]`)
- Al clickear: `window.open(/api/v1/admissions/{id}/export/pdf)` — el browser descarga / abre el PDF
- Estado loading mientras el backend genera el archivo

**Contenido del PDF:**
1. Portada: nombre del residente, número de admisión, fechas, estado
2. Datos del residente y red familiar
3. Consentimientos (tabla con estado)
4. Evaluaciones (médica, terapéutica, social, psicología, TO)
5. Plan de tratamiento y etapas
6. Notas diarias (últimas 30)
7. Consultas de seguimiento

---

### Fase 9 — Notificaciones Básicas

**Objetivo:** Alertar al personal de eventos clínicamente importantes sin email ni push — visible en el panel al iniciar sesión.

**Tipos de notificaciones:**
1. **Próximas citas** — `consultations` con `next_appointment_date` en los próximos 3 días
2. **Permisos vencidos** — `exit_passes` con `return_date_expected < hoy` y `status = approved` (el residente no regresó)
3. **Etapa de tratamiento próxima a vencer** — `treatment_stages` con `end_date` en los próximos 7 días y `status = active`

**Backend:**
- `GET /notifications` — retorna lista de notificaciones activas para el usuario actual (filtrado por rol):
  ```json
  [
    { "type": "upcoming_appointment", "message": "...", "entity_id": 42, "entity_type": "consultation", "due_date": "2026-06-12" },
    { "type": "overdue_exit_pass", "message": "...", "entity_id": 15, "entity_type": "exit_pass", "due_date": "2026-06-09" }
  ]
  ```
- Sin tabla adicional — se calculan on-the-fly con queries directas

**Frontend:**
- Campana en el navbar (ya existe el ícono en TailAdmin) con badge de conteo
- Dropdown con lista de notificaciones, cada una con link a la entidad
- Al entrar al dashboard: fetch automático de `/notifications`
- Componente `NotificationBell.tsx` en `components/common/`

---

## Estado de Implementación

| Fase | Descripción | Estado |
|------|-------------|--------|
| 1 | Modelos BD, migración, seed | ✅ Completo |
| 2 | Autenticación (JWT, httpOnly cookies) | ✅ Completo |
| 3 | Residentes y admisiones | ✅ Completo |
| 4 | Módulos clínicos, admin, reportes | ✅ Completo |
| 5 | Búsqueda, filtros y paginación | ⏳ Pendiente |
| 6 | Control de acceso por rol (enforcement) | ⏳ Pendiente |
| 7 | Borrado lógico (archivar / eliminar) | ⏳ Pendiente |
| 8 | Exportar / imprimir expediente a PDF | ⏳ Pendiente |
| 9 | Notificaciones básicas | ⏳ Pendiente |
