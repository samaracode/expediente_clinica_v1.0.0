# Autorización por permisos de módulo por-usuario, no por rol

## Contexto

La autorización estaba hardcodeada por rol en dos capas: `admin/src/lib/access.ts`
(frontend) y una constante `RoleRequired([...])` por router (backend). Cambiar
quién accede a qué requería editar código en dos sitios y redeployar. ZOE tiene
pocos usuarios (~10-15) y el administrador necesita ajustar accesos por persona
sin depender del desarrollador.

## Decisión

El acceso a módulos pasa a ser **por Usuario**, no por Rol. Al crear/editar un
usuario, el admin marca con checkboxes qué módulos puede entrar esa persona. Los
permisos se guardan en BD y se leen en cada request (el backend ya carga el
`User` completo en `get_current_user`, así que el token y el login no cambian).

- **Granularidad**: por módulo, acceso total (sí/no). Sin distinción ver/editar.
- **Rol**: se conserva como **etiqueta descriptiva** (qué es la persona) y para
  el vínculo Professional→área y el filtro financiero del Dashboard. Deja de ser
  el guardián de acceso.
- **admin**: acceso total a todo, no editable (evita lockout catastrófico).
- **Dashboard** siempre visible; **Administración** siempre admin-only.
- Módulos: Residentes, Operación (1 checkbox = 4 sub-pantallas), Finanzas,
  Reportes, y cada evaluación clínica por separado (Médica, Psicología,
  Terapéutica, Trabajo Social, Terapia Ocupacional).

## Considered / rechazado

- **Matriz rol×módulo configurable**: se descartó a favor de por-usuario porque
  con pocos usuarios es más directo marcar por persona y evita la complejidad de
  sincronizar "qué pasa al cambiar el rol de alguien".
- **Granularidad ver/editar o por-acción**: sobre-ingeniería para ZOE.

## Consecuencias

- `RoleRequired([...])` se reemplaza por un guard tipo `ModuleRequired("medical")`
  que consulta los permisos del usuario. Es el único punto de chequeo backend.
- `access.ts` deja de tener reglas fijas: lee los permisos del usuario logueado.
- Riesgo mitigado: como admin es siempre total y no editable, nadie puede
  quitarse a sí mismo el acceso a Administración.
