# Plan Técnico — Módulo de Control Financiero (Cuentas por cobrar)

> Estado: diseño aprobado en sesión de grilling (2026-06). Pendiente de implementación.
> Convención: prosa en español, identificadores de código/BD en inglés (igual que el resto del repo).
> Segundo frente del roadmap, después de la suite "Operación diaria" (ya construida).

## 1. Objetivo

**Cuentas por cobrar**: llevar cuánto debe cada residente, qué ha pagado (familias y terceros/subsidios), el saldo y la morosidad. **NO** es contabilidad general (sin gastos, nómina ni estados financieros). Factura electrónica de Hacienda queda diferida.

## 2. Arquitectura general

- **Patrón híbrido de navegación:** sección nueva **"Finanzas"** a nivel centro (dashboard de morosidad, pagos del día, reportes) **+** pestaña financiera en el expediente de cada residente (acuerdo, cargos, pagos, saldo).
- **Permisos (NUEVO):** primer módulo con acceso restringido. Reutilizar `RoleRequired(["admin", "receptionist"])` de `app/core/deps.py` en **todos** los endpoints financieros. Los roles clínicos no acceden. En el frontend, ocultar la sección/pestaña si el rol no aplica.
- **Reutilizar:** `notification_service` (alertas de morosidad), `export_service` (contexto para PDFs), patrón de Services/routers/migraciones de los módulos recientes.
- **Dinero:** columnas `Numeric(12, 2)` (igual que `economic_situations.monthly_income_colones`). Moneda asumida: CRC.
- **Residente activo** (para generación de cargos): admisión con `status` en `{consents_pending, assessment_in_progress, treatment_active}`.
- **OJO:** `economic_situations` ya existe pero es perfil socioeconómico de ingreso, **no** facturación. No tocarlo.

### Navegación nueva (sidebar)
```
Finanzas
 ├── Resumen / morosidad     /finance
 └── Pagos del día           /finance/payments   (o integrado en el resumen)
```
Y en el expediente (`/admissions/[id]/finance`): acuerdo, cargos, pagos, saldo, botones de recibo y estado de cuenta.

## 3. Modelo de datos

**`payment_agreements`** — un acuerdo por admisión (como `economic_situations`, unique por admission)
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| admission_id | FK admissions, unique | |
| agreement_type | enum `AgreementType` | `monthly` \| `fixed_total` \| `scholarship_full` \| `scholarship_partial` |
| amount | Numeric(12,2) | monto neto que paga la familia (0 si beca total) |
| billing_day | int (nullable) | día del mes de cobro (para `monthly`) |
| notes | text (nullable) | |
| is_active | bool | default true |
| created_at | DateTime tz | server_default now() |

**`charges`** — cargos (deudas)
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| admission_id | FK admissions | |
| concept | str | "Mensualidad marzo 2026", "Depósito de ingreso", ... |
| amount | Numeric(12,2) | |
| charge_date | Date | |
| period | str (nullable) | "YYYY-MM" para mensualidades (clave de idempotencia) |
| is_auto | bool | true si lo generó el sistema |
| created_by_user_id | FK users (nullable) | |
| notes | text (nullable) | |
| created_at | DateTime tz | |

Índice único parcial sugerido: `(admission_id, period)` para `period IS NOT NULL` → evita duplicar la mensualidad de un mes.

**`payments`** — pagos
| Campo | Tipo | Notas |
|---|---|---|
| id | int PK | |
| admission_id | FK admissions | |
| amount | Numeric(12,2) | |
| payment_date | Date | |
| method | enum `PaymentMethod` | `cash` \| `sinpe` \| `transfer` \| `check` \| `other` |
| payer_type | enum `PayerType` | `family` \| `iafa` \| `imas` \| `church` \| `donor` \| `other` |
| payer_name | str (nullable) | nombre de quien pagó |
| reference | str (nullable) | # de transacción / SINPE |
| receipt_number | int (unique) | correlativo del recibo |
| received_by_user_id | FK users (nullable) | |
| notes | text (nullable) | |
| created_at | DateTime tz | |

**Saldo** = Σ `charges.amount` − Σ `payments.amount` por admisión (calculado, no se asigna pago a cargo específico — cuenta corriente).

## 4. Lógica (servicio `finance_service.py`)

- **Generación de cargos mensuales:** para cada acuerdo `monthly` activo de una admisión activa, generar un `charge` del periodo `YYYY-MM` (concept "Mensualidad <mes año>", amount = agreement.amount, charge_date según billing_day) si no existe ya ese `(admission_id, period)`. Idempotente. Disparada por:
  - endpoint manual `POST /finance/generate-monthly-charges?period=YYYY-MM` (recomendado para v1, con revisión humana), y/o
  - generación lazy al abrir el dashboard del periodo. (Cron = fase posterior.)
- **Saldo / cuenta:** método que devuelve cargos, pagos y saldo de una admisión.
- **Morosidad:** admisiones con saldo > 0 cuyo cargo más viejo sin cubrir supera un margen (config, ej. 30 días). Genera notificación vía `notification_service` (tipo `overdue_balance`).
- **Correlativo de recibo:** `receipt_number` = max actual + 1 (transaccional).

## 5. Endpoints

Todos con `Depends(RoleRequired(["admin", "receptionist"]))`.

| Endpoint | Método | Descripción |
|---|---|---|
| `/admissions/{id}/payment-agreement` | GET, PUT | leer / crear-actualizar el acuerdo |
| `/admissions/{id}/charges` | GET, POST | listar / crear cargo manual |
| `/charges/{id}` | DELETE | anular cargo (si fue error) |
| `/admissions/{id}/payments` | GET, POST | listar / registrar pago (asigna receipt_number) |
| `/admissions/{id}/account` | GET | `{charges, payments, balance}` |
| `/admissions/{id}/account/statement` | GET | estado de cuenta PDF |
| `/payments/{id}/receipt` | GET | recibo de pago PDF |
| `/finance/generate-monthly-charges` | POST | generar cargos del periodo (`?period=YYYY-MM`) |
| `/finance/overview` | GET | dashboard: total recibido por periodo + desglose por `payer_type` |
| `/finance/overdue` | GET | lista de morosidad (residente, saldo, días de atraso) |

## 6. Documentos PDF
- **Recibo de pago** numerado (residente, monto, concepto/periodo, método, pagador, fecha, recibido por).
- **Estado de cuenta** por residente (cargos, pagos, saldo).
- Reutilizar/extender `export_service` para el contexto; confirmar el motor de render PDF durante la construcción (lib tipo reportlab/weasyprint o plantilla HTML).

## 7. Frontend
- `/finance` — **Dashboard de finanzas** (centro): total recibido del periodo + desglose familias vs subsidios, lista de **morosidad**, pagos del día, botón "Generar cargos del mes".
- `/admissions/[id]/finance` — **pestaña financiera** del residente: acuerdo (crear/editar), cargos, pagos (registrar), saldo, botones de **recibo** y **estado de cuenta**.
- Sidebar: grupo nuevo **"Finanzas"** (visible solo para admin/recepción).

## 8. Plan de implementación por fases

| Fase | Entregable | Depende de |
|---|---|---|
| **1A** | Datos: `payment_agreements`, `charges`, `payments` + enums + migración | — |
| **1B** | API: `finance_service` (acuerdo, cargos, generación auto, pagos, saldo, morosidad, correlativo) + endpoints con `RoleRequired` + tests | 1A |
| **1C** | PDFs: recibo de pago + estado de cuenta | 1B |
| **1D** | Frontend: dashboard de finanzas + pestaña en expediente + sidebar (role-gated) | 1B/1C |
| **Notif.** | Alerta de morosidad (`overdue_balance`) en `notification_service` | 1B |

## 9. Diferido (fase posterior)
- Factura electrónica de Hacienda CR · contabilidad general (gastos/nómina/flujo de caja) · cron de generación automática de cargos.

## 10. Decisiones abiertas (a confirmar antes de construir)
1. Margen de morosidad (¿30 días desde el cargo?).
2. Correlativo de recibo: ¿global o por año (ej. 2026-00001)?
3. ¿Solo CRC, o también registrar moneda por pago?
4. Generación de cargos: ¿botón manual + lazy (recomendado) o cron desde el inicio?
5. Día de cobro por defecto si el acuerdo no lo especifica (¿día 1?).
