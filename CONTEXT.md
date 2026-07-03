# Contexto — Expediente Clínico ZOE

Sistema de expediente clínico para el Hogar Zoé (Asociación Centro Cristiano
Canaán), clínica de rehabilitación de adicciones en Costa Rica.

## Glosario

### Usuario (User)
Cuenta de acceso al sistema para una persona del personal. Tiene `full_name`,
`email`, `role`, `is_active`. El **`email` es solo un identificador de login,
no un buzón**: el personal de ZOE no necesariamente tiene correo real ni el
centro tiene correo saliente configurado. Por eso el sistema **no** envía
correos (nada de "link de recuperación", verificación de email, ni
invitaciones). La recuperación de contraseña es **manual**: el Administrador la
restablece desde `Administración → Usuarios` y el usuario luego la cambia desde
`Mi Perfil`. El cambio de contraseña temporal es opcional, no forzado.
_Avoid_: "cuenta de correo" como sinónimo de email — aquí email ≠ buzón.

### Rol (Role)
**Etiqueta descriptiva** de qué es una persona: `admin`, `counselor`
(Consejero), `medical` (Médico), `social_worker` (Trabajador Social),
`psychologist` (Psicólogo), `occupational_therapist` (Terapeuta Ocupacional),
`receptionist` (Recepcionista). Tras el rediseño de autorización, **el rol ya
NO controla el acceso a módulos** (eso lo hacen los Permisos de módulo por
usuario); el rol solo describe a la persona y sigue usándose para el vínculo
Professional→área y el filtro financiero del Dashboard. El rol `admin` es el
único con significado de acceso: **acceso total, no editable** (evita lockout).

### Permiso de módulo (Module permission)
Acceso de un **Usuario** concreto a un **Módulo** del sistema, marcado por el
Administrador con checkboxes al crear/editar el usuario. Reemplaza la matriz
rol→ruta hardcodeada. Granularidad **por módulo, acceso total** (sí/no; quien
entra puede ver y editar). Módulos configurables: Residentes, Operación (un
solo checkbox para sus 4 sub-pantallas), Finanzas, Reportes, y cada evaluación
clínica por separado (Médica, Psicología, Terapéutica, Trabajo Social, Terapia
Ocupacional). El **Dashboard** siempre es visible (pantalla de inicio) y
**Administración** es siempre admin-only; ninguno es configurable. El `admin`
tiene todos los módulos por defecto y no editable. Ver ADR 0003.

### Profesional (Professional)
Perfil clínico asociado a un Usuario (relación 1:1 opcional). Vincula al usuario
con un Área de tratamiento y guarda su especialidad. Un Usuario **tiene** (no
**es**) un Profesional: no todos los usuarios son profesionales clínicos (p. ej.
recepcionista, admin). El nombre mostrado del profesional vive hoy duplicado en
`User.full_name` y en `Professional.first_name/last_name`.

### Dashboard
Página de inicio del sistema (ruta `/`), lo primero que ve el usuario tras
iniciar sesión. Presenta estadísticas significativas del estado de la clínica.
Reemplaza al dashboard demo "Ecommerce" de TailAdmin. En el menú lateral
aparece como ítem propio, arriba de "Clínica".

No confundir con los dashboards demo de TailAdmin (Ecommerce, Analytics, CRM,
Stocks, etc.), que se retiran del menú por no pertenecer al dominio clínico.

### Menú lateral (navegación de ZOE)
Tras la limpieza, el menú muestra solo los ítems del dominio ZOE:
`Dashboard` (nuevo, → `/`), `Clínica`, `Operación`, `Finanzas`, `Reportes`,
`Administración`, y `User Profile` (funcional, para cuenta/contraseña).

Los ítems demo de TailAdmin se retiran del menú. Se decidió **solo quitarlos
del menú**, sin bloquear sus rutas ni borrar sus archivos: las páginas demo
siguen existiendo en el repo y son técnicamente alcanzables escribiendo la URL
a mano, pero al no estar en la navegación, en la práctica no se accede a ellas.
Bloquear las rutas (allowlist en `access.ts`) o borrar los archivos quedan como
tareas futuras opcionales si se quiere endurecer.

### Residente
Persona ingresada en el Hogar Zoé para tratamiento de rehabilitación.
Identificada por un `code` único. Ver modelo `Resident`.

### Admisión (Admission)
Un episodio de ingreso de un Residente. Un Residente puede tener varias
admisiones a lo largo del tiempo (primera vez o readmisión). Tiene un estado
que sigue el flujo: intake_pending → consents_pending → assessment_in_progress
→ treatment_active → discharged / abandoned.

### Ocupación
KPI principal del Dashboard. Se compone de:
- **Residentes activos**: admisiones con estado `treatment_active`.
- **Capacidad**: nº total de camas, guardado en `clinic_settings` (clave
  `capacity`).
- **% ocupación**: activos / capacidad.
- **Lista de espera**: `waitlist_entries` en estado pendiente.
Es el dato operativo más consultado a diario; se muestra destacado con un
gráfico radial.

### KPIs del Dashboard
Fila de tarjetas de métrica en la parte superior:
1. **Residentes activos** — admisiones `treatment_active`.
2. **Ingresos del mes** — admisiones con `admission_date` en el mes actual.
3. **Egresos del mes** — admisiones `discharged`/`abandoned` con
   `discharge_date` en el mes actual.
4. **Morosidad / saldo por cobrar** — suma de saldos pendientes
   (charges − payments). **Dato financiero restringido**: solo visible para
   roles `admin` y `receptionist`, coherente con el acceso al módulo de
   Finanzas (`lib/access.ts`). Otros roles ven el dashboard sin esta tarjeta.

### Gráficos del Dashboard
El dashboard es una vista panorámica/estratégica (lo que ve la dirección al
entrar), no operativa de turno. Por eso muestra tendencias, no detalle diario
(el detalle vive en los módulos de Operación). Dos gráficos en v1:
1. **Ingresos vs. egresos por mes** (barras) — narrativa de movimiento del
   centro en los últimos meses: ¿crece o se vacía?
2. **Residentes por estado de admisión** (dona) — el "embudo" clínico:
   cuántos en intake, evaluación, tratamiento activo, etc.

Descartado para v1 (v2): "ocupación en el tiempo" (line chart), requiere
agregación histórica más compleja.

### DashboardService / endpoint de resumen
Los datos del Dashboard se sirven desde un endpoint único
`GET /api/v1/dashboard/summary`, respaldado por un `DashboardService`
(análogo al `ReportService` existente). Devuelve ocupación, KPIs, admisiones
por estado y flujo mensual en una sola respuesta. El campo de morosidad
(`outstanding_balance`) solo se calcula y devuelve si el rol del usuario es
`admin` o `receptionist`; para otros roles el campo se omite de la respuesta
(no solo se oculta en el frontend). Ver ADR 0001.
