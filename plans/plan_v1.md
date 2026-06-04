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

## Verificación del Backbone

1. `make setup` sin errores (venv + npm install)
2. `make dev` levanta ambos servidores (`:3000` frontend, `:8000` backend)
3. `make db-migrate` crea las 22 tablas en PostgreSQL sin errores
4. `make seed` crea usuario admin inicial y áreas de tratamiento
5. `GET http://localhost:8000/docs` muestra Swagger con todos los routers organizados por módulo
6. `GET http://localhost:3000` redirige a `/login` (middleware activo)
7. Login con credenciales del seed → cookie httpOnly seteada → redirect a dashboard
8. Intentar acceder a `/admin/users` con rol `counselor` → redirect a `/unauthorized`
9. `POST /api/v1/auth/login` con credenciales incorrectas → 401 con mensaje claro
10. Revisar `audit_logs` en DB después de crear un residente → registro automático presente
