# El email es un identificador de login, no un buzón; el sistema no envía correos

El personal de ZOE no necesariamente tiene correo electrónico real ni el centro
tiene servidor de correo saliente. Por eso el campo `email` del `User` se trata
como un **identificador de login** (a veces inventado), no como una dirección a
la que se pueda escribir. En consecuencia, el sistema **no envía correos**: se
descartan el reset de contraseña por "link de recuperación", la verificación de
email, las invitaciones por correo y el signup público / OAuth (los stubs
`/signup` y `/reset-password` de la plantilla TailAdmin quedan muertos).

La recuperación de contraseña es **manual**: el Administrador restablece la
contraseña desde `Administración → Usuarios` (la escribe él mismo, sin mínimos
forzados) y la persona luego la cambia desde `Mi Perfil`. El cambio de la clave
temporal es opcional, no forzado (personal no técnico; se prioriza baja
fricción sobre rigor).

## Consecuencias

- Si en el futuro ZOE adopta correos reales + SMTP, esta decisión se revisa y
  se pueden habilitar los flujos por email. Hasta entonces, cualquier feature
  que asuma "enviar un correo" está fuera de alcance por diseño, no por olvido.
