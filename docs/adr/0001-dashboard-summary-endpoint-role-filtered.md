# 1. Endpoint de resumen del dashboard con datos financieros filtrados por rol

Fecha: 2026-06-30

## Estado

Aceptado

## Contexto

El Dashboard (página de inicio) muestra estadísticas del sistema, entre ellas
la **morosidad / saldo por cobrar**, un dato financiero sensible. El módulo de
Finanzas ya está restringido a los roles `admin` y `receptionist`
(`admin/src/lib/access.ts`). El dashboard, en cambio, lo ven todos los roles
(consejeros, personal médico, terapeutas, etc.).

Necesitábamos decidir cómo alimentar el dashboard y, en particular, cómo evitar
exponer la morosidad a roles que no deben verla.

Dos alternativas:

- **A. Un endpoint único** `GET /api/v1/dashboard/summary` que agrega todos los
  datos en el backend y **omite el campo de morosidad de la respuesta** cuando
  el rol no es `admin`/`receptionist`.
- **B. Que el frontend** llame a varios endpoints existentes, calcule los
  agregados en el cliente y **oculte visualmente** la tarjeta de morosidad
  según el rol.

## Decisión

Adoptamos la opción **A**: un endpoint único `/dashboard/summary`, respaldado
por un `DashboardService` (análogo al `ReportService` ya existente). El dato de
morosidad **se calcula y se incluye en la respuesta HTTP solo si el rol es
`admin` o `receptionist`**; para el resto de roles el campo se omite por
completo del JSON, no se envía al navegador.

## Consecuencias

**A favor:**
- El dato financiero sensible nunca sale del backend hacia roles no
  autorizados. Ocultarlo solo en el frontend (opción B) lo dejaría accesible
  en la respuesta HTTP para cualquiera que abra las herramientas de red.
- Una sola llamada de red; el frontend solo pinta, no calcula.
- La lógica de permisos vive junto a la de Finanzas, en el backend, coherente
  con `lib/access.ts`.

**En contra / a tener en cuenta:**
- La respuesta del endpoint tiene **forma variable** según el rol (el campo
  `outstanding_balance` puede o no estar presente). Los consumidores deben
  tratarlo como opcional.
- Introduce un servicio y un endpoint nuevos que hay que mantener.
