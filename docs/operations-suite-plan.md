# Plan Técnico — Suite "Operación diaria" (ZOE)

> Estado: diseño aprobado en sesión de grilling (2026-06-20). Pendiente de implementación.
> Convención: prosa en español, identificadores de código/BD en inglés (igual que el resto del repo).

## 1. Objetivo

El expediente clínico (formularios) ya está cubierto. Esta suite agrega la capa **operativa** que el centro vive todos los días y que hoy se maneja en papel/WhatsApp. Se construye en 4 módulos, en orden de criticidad:

1. 💊 **Medicamentos (MAR)** — registro de administración de medicamentos
2. ✅ **Asistencia** — presencia física / pase de lista por turno
3. 🛏️ **Ocupación** — cupos + lista de espera
4. 🔄 **Entrega de turno** — handover entre turnos (auto-compilado)

Frentes siguientes (fuera de este plan): Control financiero → Resultados/reportería. Familias descartado por ahora.

## 2. Arquitectura general

- **Patrón híbrido de navegación:** una sección nueva de nivel superior **"Operación"** (vista de TODO el centro, para el día a día) **+** detalle/historial por residente accesible desde su expediente. Esto contrasta con el expediente actual, que es estrictamente por admisión.
- **Stack existente que reutilizamos:** FastAPI + SQLAlchemy (modelos en `app/models/`, schemas en `app/schemas/`, routers en `app/api/v1/`, lógica en `app/services/`) y Next.js (App Router, páginas en `admin/src/app/(admin)/`).
- **Definición de "residente activo"** (base para ocupación y asistencia): admisión con `status` en `{consents_pending, assessment_in_progress, treatment_active}` (es decir, NO `intake_pending` cancelado, NI `discharged`, NI `abandoned`). A confirmar si `intake_pending` cuenta como ocupando cupo.
- **Hecho operativo clave:** Zoé **no tiene médico de planta**; todas las recetas son externas → el módulo de medicamentos transcribe recetas externas y guarda la foto.

### Navegación nueva (sidebar)
```
Operación
 ├── Pase de medicamentos      /operations/medications
 ├── Asistencia                /operations/attendance
 ├── Ocupación                 /operations/occupancy
 └── Entrega de turno          /operations/handover
```
Y en el expediente del residente (`/admissions/[id]/`): pestañas nuevas de Medicamentos (órdenes + historial) y Asistencia (historial).

## 3. Dependencia transversal: subida de archivos

Necesaria para la foto de la receta (y reutilizable para firmas/escaneos en el futuro). La tabla `files` ya existe (modelada con S3) pero **falta el endpoint**.

| Endpoint | Método | Descripción |
|---|---|---|
| `/files` | POST (multipart) | Sube archivo → almacena (S3 en prod / disco local en dev) → crea row en `files` → devuelve `{id, file_name, mime_type, url}` |
| `/files/{id}` | GET | Devuelve URL prefirmada o hace stream del archivo |

- Config de almacenamiento por entorno (`STORAGE_BACKEND=s3|local`) en `app/core/config.py`.
- Validar `mime_type` (imágenes/pdf) y tamaño máximo.

---

## 4. Módulo 1 — Medicamentos (MAR)

**Modelo:** prescripción estructurada → tomas automáticas. El **encargado de medicamentos** marca cada toma.

### 4.1 Modelo de datos

**`medications`** — catálogo del centro (crece con autocompletar; sostiene el flag de controlado y la advertencia de alergias)
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| name | str | nombre del medicamento |
| form | str | tableta, jarabe, etc. (nullable) |
| strength | str | ej. "50 mg" (nullable) |
| is_controlled | bool | psicotrópico/controlado |
| notes | text | nullable |

**`medication_orders`** — orden/prescripción transcrita de receta externa
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| admission_id | FK admissions | |
| medication_id | FK medications | |
| dose | str | ej. "1 tableta", "50 mg" |
| route | enum | oral, IM, SC, otra (vía) |
| schedule_type | enum | `scheduled` \| `prn` |
| times | JSONB | franjas horarias (claves de `med_time_slots`) para `scheduled` |
| frequency_text | str | texto humano de la receta ("cada 12h") |
| prn_reason | text | motivo para `prn` (SOS) |
| start_date | date | |
| end_date | date | nullable (indefinido) |
| prescribed_by_external | str | médico/psiquiatra externo |
| prescriber_institution | str | nullable |
| transcribed_by_user_id | FK users | quién la cargó |
| receta_file_id | FK files | foto de la receta (nullable) |
| is_controlled | bool | derivado del catálogo, override permitido |
| status | enum | `active` \| `suspended` \| `finished` |
| notes | text | |
| created_at | datetime | |

**`medication_administrations`** — cada toma (evento)
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| order_id | FK medication_orders | |
| admission_id | FK admissions | denormalizado para consultas del pase |
| scheduled_at | datetime | hora pautada (null para PRN) |
| status | enum | `pending` \| `taken` \| `refused` \| `omitted` |
| administered_at | datetime | hora real (nullable) |
| administered_by_user_id | FK users | encargado |
| witness_user_id | FK users | segundo testigo (obligatorio si controlado) |
| reason | text | motivo si rechazado/omitido, o motivo PRN |
| notes | text | |

**`med_time_slots`** — franjas horarias configurables del centro
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| label | str | "Mañana", "Mediodía", "Tarde", "Noche" |
| time | time | ej. 06:00, 12:00, 18:00, 21:00 |

**`resident_allergies`** — alergias a nivel residente
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| resident_id | FK residents | |
| substance | str | ej. "Penicilina" |
| reaction | str | nullable |
| severity | enum | leve / moderada / severa (nullable) |

### 4.2 Generación de tomas
Estrategia **lazy** (sin cron al inicio): al abrir el "Pase del día" para una fecha, el backend genera las filas `pending` faltantes en `medication_administrations` para cada `medication_order` activa (`scheduled`) cuyas `times` y rango `start_date..end_date` apliquen ese día. Idempotente (no duplica). Más adelante se puede mover a un job programado.

### 4.3 Reglas
- **Controlados:** al registrar una toma de orden `is_controlled`, exigir `witness_user_id` y/o `reason`.
- **Rechazado/Omitido:** `reason` obligatorio.
- **Alertas de dosis omitidas:** si `scheduled_at` + margen (config, ej. 60 min) ya pasó y `status = pending`, generar notificación al encargado (reusar servicio de `notifications`). Cron ligero o cálculo al cargar el pase.
- **Alergias:** mostrar advertencia del residente en el perfil y en el pase.

### 4.4 Endpoints
| Endpoint | Método | Descripción |
|---|---|---|
| `/medications` | GET, POST | catálogo |
| `/admissions/{id}/medication-orders` | GET, POST | órdenes del residente |
| `/medication-orders/{id}` | PATCH | editar / suspender / finalizar |
| `/medications/pass` | GET | pase del día center-wide (`?date=&slot=`), agrupado por franja |
| `/medication-administrations/{id}/record` | POST | marcar toma (status, hora, testigo, motivo) |
| `/admissions/{id}/medication-orders/{order_id}/prn` | POST | registrar toma PRN ad-hoc |
| `/residents/{id}/allergies` | GET, POST, DELETE | alergias |
| `/settings/medication-slots` | GET, PUT | franjas horarias |

### 4.5 Frontend
- `/operations/medications` — **Pase del día** center-wide: por franja horaria, lista de tomas pendientes de todos los residentes, marcar Tomado/Rechazado/Omitido, controlados resaltados 🔴, alergias visibles, banner de omitidas.
- `/admissions/[id]/medications` — órdenes del residente + historial de tomas; crear orden con **subida de foto de receta**.
- Alergias en el perfil del residente.

---

## 5. Módulo 2 — Asistencia (presencia física)

**Modelo híbrido:** el sistema pre-llena el estado esperado y el encargado **confirma por turno**.

### 5.1 Modelo de datos

**`attendance_roll_calls`** — un pase por turno/fecha
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| date | date | |
| shift | enum | `morning` \| `afternoon` \| `night` |
| conducted_by_user_id | FK users | |
| conducted_at | datetime | |
| notes | text | |

**`attendance_entries`** — un registro por residente en ese pase
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| roll_call_id | FK attendance_roll_calls | |
| admission_id | FK admissions | |
| expected_status | enum | calculado por el sistema |
| actual_status | enum | confirmado por el encargado |
| note | text | |

**Enum de estado:** `present`, `on_pass`, `external_appointment`, `hospitalized`, `absent_without_leave`, `discharged`.

### 5.2 Reglas
- `expected_status` se calcula de: admisiones activas (= `present`) menos quienes tengan un `ExitPass` activo ese día (= `on_pass`) o cita externa registrada.
- Si `actual_status = absent_without_leave` (o difiere de lo esperado hacia ausencia) → **alerta de fuga** (notificación a admin) y opción de crear incidente en la entrega de turno.

### 5.3 Endpoints
| Endpoint | Método | Descripción |
|---|---|---|
| `/attendance/roll-call` | GET | roster pre-llenado (`?date=&shift=`) |
| `/attendance/roll-call` | POST | guardar confirmaciones |
| `/attendance/today` | GET | resumen de conteo actual (dashboard) |
| `/admissions/{id}/attendance` | GET | historial por residente |

### 5.4 Frontend
- `/operations/attendance` — pase por turno, pre-llenado, confirmación rápida, resumen de conteo (presentes / en permiso / cita externa / ausentes), discrepancias resaltadas.

---

## 6. Módulo 3 — Ocupación (solo cupos) + lista de espera

### 6.1 Modelo de datos
- **Capacidad:** setting del centro (`clinic_settings.capacity`, int) — tabla simple key-value o columna en config.
- **Ocupación:** calculada = conteo de admisiones activas. No hay camas nominales.

**`waitlist_entries`** — lista de espera simple
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| full_name | str | |
| contact_phone | str | |
| contact_email | str | nullable |
| requested_at | date | |
| referred_by | str | persona/institución |
| status | enum | `waiting` \| `admitted` \| `declined` \| `cancelled` |
| notes | text | |
| created_by_user_id | FK users | |

### 6.2 Endpoints
| Endpoint | Método | Descripción |
|---|---|---|
| `/occupancy` | GET | `{capacity, occupied, available, by_status}` |
| `/waitlist` | GET, POST | lista de espera |
| `/waitlist/{id}` | PATCH | cambiar estado |
| `/settings/capacity` | GET, PUT | capacidad |

### 6.3 Frontend
- `/operations/occupancy` — tablero de cupos (ocupadas/disponibles, barra) + tabla de lista de espera con acciones.

---

## 7. Módulo 4 — Entrega de turno (auto-compilada + notas)

**Depende de los módulos 1–3** para el auto-resumen.

### 7.1 Modelo de datos

**`shift_handovers`** — una entrega por turno/fecha
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| date | date | |
| shift | enum | `morning` \| `afternoon` \| `night` |
| auto_summary | JSONB | snapshot al cerrar (ver 7.2) |
| notes | text | observaciones del encargado |
| closed_by_user_id | FK users | saliente |
| closed_at | datetime | |
| received_by_user_id | FK users | entrante |
| received_at | datetime | |
| status | enum | `open` \| `closed` \| `received` |

**`shift_incidents`** — incidentes del turno
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| handover_id | FK shift_handovers | |
| admission_id | FK admissions | nullable |
| type | str | crisis, conflicto, médico, otro |
| severity | enum | baja / media / alta |
| description | text | |
| action_taken | text | |
| reported_by_user_id | FK users | |
| created_at | datetime | |

**`shift_tasks`** — pendientes para el siguiente turno
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| handover_id | FK shift_handovers | |
| related_admission_id | FK admissions | nullable |
| description | text | |
| due_at | datetime | nullable |
| is_done | bool | |
| done_by_user_id | FK users | nullable |

### 7.2 Auto-resumen (calculado al cerrar)
Dentro de la ventana del turno, juntar:
- Medicamentos: dosis `omitted`/`refused`.
- Asistencia: discrepancias / ausencias sin permiso.
- Permisos: salidas y retornos del día (de `ExitPass`).
- Ingresos/egresos del día (cambios de `admission.status`).

### 7.3 Apretón de manos
- `close` → registra `closed_by_user_id` + `closed_at`, congela `auto_summary`.
- `receive` → registra `received_by_user_id` + `received_at`. Cadena de responsabilidad por franja.

### 7.4 Endpoints
| Endpoint | Método | Descripción |
|---|---|---|
| `/shift-handovers` | GET | `?date=&shift=` |
| `/shift-handovers/{id}/auto-summary` | GET | resumen calculado |
| `/shift-handovers/{id}/close` | POST | cerrar (saliente) |
| `/shift-handovers/{id}/receive` | POST | recibir (entrante) |
| `/shift-handovers/{id}/incidents` | GET, POST | incidentes |
| `/shift-handovers/{id}/tasks` | GET, POST, PATCH | pendientes |

### 7.5 Frontend
- `/operations/handover` — armar la entrega (auto-resumen + incidentes + pendientes), cerrar, y bandeja de "recibir" para el turno entrante.

---

## 8. Roles y permisos

- Roles actuales: `admin, counselor, medical, social_worker, psychologist, occupational_therapist, receptionist` (no hay enfermería).
- **Encargado de medicamentos:** crear esta figura. Opciones a decidir en implementación:
  - (a) Nuevo `UserRole = med_in_charge`, o
  - (b) Designación por turno (registrada en el pase/handover) + permiso a `{admin, counselor}`.
  - **Recomendado:** (b) por flexibilidad de cobertura de turnos; el sistema siempre registra quién marcó cada toma.
- Operación (los 4 módulos) accesible a `{admin, counselor, + encargado}`. Configuración (franjas, capacidad) solo `admin`.

## 9. Plan de implementación por fases

| Fase | Entregable | Depende de |
|---|---|---|
| **0** | Subida de archivos (`POST /files`, storage local/S3, `GET /files/{id}`) | — |
| **1** | Medicamentos completo (catálogo, órdenes + receta, franjas, alergias, pase del día, tomas, controlados con testigo, PRN, alertas de omitidas) | Fase 0 |
| **2** | Asistencia (pase híbrido por turno, estados, alertas de fuga) | — |
| **3** | Ocupación (tablero de cupos) + lista de espera | — |
| **4** | Entrega de turno (auto-compilada + incidentes + pendientes + handshake) | Fases 1–3 |
| **Navegación** | Sección "Operación" en el sidebar + pestañas en expediente | por fase |

## 10. Diferido (fase 2 / futuro)
- Inventario completo de medicamentos controlados (stock, entradas, descuento por toma, conteo/cuadre por turno).
- Asistencia a actividades (participación clínica) — distinto de presencia.
- Camas/habitaciones nominales (hoy solo cupos).
- Frentes mayores: Control financiero, Resultados/reportería.

## 11. Decisiones abiertas (a confirmar antes de construir)
1. ¿`intake_pending` ocupa cupo para el cálculo de ocupación?
2. ¿Encargado de medicamentos = rol nuevo (a) o designación por turno (b)?
3. Franjas horarias por defecto del centro (06/12/18/21?) y margen de "dosis omitida" (60 min?).
4. ¿Alergias como tabla estructurada (propuesto) o campo de texto simple?
