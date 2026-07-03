# Capítulo 11: Gestión de Usuarios

> Este capítulo le explica cómo crear y administrar las cuentas del personal que usa el sistema.

---

## ¿Por qué es importante la gestión de usuarios?

> **Solo para administradores:** Esta sección del sistema solo está disponible para el rol de Administrador.

Cada persona que usa el sistema debe tener **su propia cuenta individual**. Esto es fundamental por varias razones:

- **Seguridad:** El sistema registra quién hizo cada acción (quién registró un medicamento, quién guardó el pase de asistencia, etc.). Si varias personas comparten una cuenta, esa trazabilidad se pierde.
- **Control de acceso:** Cada rol tiene permisos específicos. Una cuenta compartida puede dar acceso a información que ciertas personas no deberían ver.
- **Responsabilidad:** En caso de necesitar revisar quién realizó una acción específica, los registros deben ser confiables.

---

## Abrir el módulo

1. En el menú lateral, haga clic en **Administración**.
2. Seleccione **Usuarios**.

[CAPTURA: pantalla de gestión de usuarios mostrando la tabla de usuarios con columnas Nombre+Correo, Rol (desplegable), Estado (badge verde Activo o gris Inactivo); y el botón "+ Nuevo usuario" en la parte superior derecha]

---

## Ver los usuarios existentes

La tabla muestra todos los usuarios del sistema con las siguientes columnas:

| Columna | Descripción |
|---|---|
| **Usuario** | Nombre completo y correo electrónico del usuario. |
| **Rol** | El rol asignado, mostrado como un menú desplegable editable. |
| **Estado** | Si la cuenta está **Activa** (verde) o **Inactiva** (gris). |

---

## Crear un nuevo usuario

Cuando contrata a un nuevo miembro del personal, créele una cuenta en el sistema:

1. Haga clic en el botón **+ Nuevo usuario** en la parte superior derecha.
2. Se desplegará un formulario en la parte superior de la pantalla.

[CAPTURA: formulario de nuevo usuario desplegado en la parte superior mostrando los campos: Nombre completo, Correo electrónico, Rol (desplegable) y Contraseña]

3. Complete los campos:

| Campo | Descripción | ¿Obligatorio? |
|---|---|---|
| **Nombre completo** | El nombre como aparecerá en el sistema. | Sí |
| **Correo electrónico** | Este será el nombre de usuario para iniciar sesión. Debe ser único. | Sí |
| **Rol** | Seleccione el rol adecuado para esta persona (ver tabla de roles abajo). | Sí |
| **Contraseña** | La contraseña inicial. Mínimo 8 caracteres. | Sí |

4. Haga clic en **Crear usuario**.

> **Importante:** El sistema **no envía automáticamente** las credenciales al nuevo usuario por correo electrónico. Debe informarle su correo y contraseña de manera personal o por un medio seguro (no por WhatsApp público ni redes sociales).

> **Consejo:** Pida al nuevo usuario que cambie su contraseña la primera vez que entre al sistema, desde la sección **Mi Perfil** (Capítulo 13).

---

## Los roles y qué permiten

Al crear o editar un usuario, debe asignarle un rol. Elija el que corresponde a las funciones de esa persona en el Hogar:

| Rol | Qué puede hacer en el sistema |
|---|---|
| **Administrador** | Acceso completo: residentes, expedientes, operación, finanzas, reportes y administración de usuarios y profesionales. |
| **Recepcionista** | Acceso a las funciones generales (residentes, operación diaria) y al módulo de finanzas (cobros y pagos). |
| **Consejero** | Acceso a residentes, expedientes y operación diaria. Puede editar las evaluaciones terapéutica y médica. |
| **Médico** | Acceso a residentes y expedientes. Puede editar únicamente la evaluación médica. |
| **Trabajador Social** | Acceso a residentes y expedientes. Puede editar únicamente la evaluación de trabajo social. |
| **Psicólogo** | Acceso a residentes y expedientes. Puede editar únicamente la evaluación psicológica. |
| **Terapeuta Ocupacional** | Acceso a residentes y expedientes. Puede editar únicamente la evaluación de terapia ocupacional. |

> **Nota:** En caso de duda sobre qué rol asignar, consulte con el equipo de soporte técnico. Asignar un rol equivocado puede dar acceso a información que esa persona no debería ver, o impedirle acceder a lo que necesita.

---

## Cambiar el rol de un usuario

Si las responsabilidades de un usuario cambian y necesita darle más o menos acceso:

1. En la tabla de usuarios, encuentre al usuario que desea modificar.
2. Haga clic en el menú desplegable de la columna **Rol**.
3. Seleccione el nuevo rol.
4. Haga clic en el botón **Guardar** que aparece junto al desplegable.

[CAPTURA: fila de usuario con el menú desplegable de rol abierto y el botón "Guardar" visible]

---

## Activar o desactivar un usuario

Cuando un miembro del personal deja de trabajar en el Hogar o necesita suspender temporalmente su acceso:

1. En la tabla, encuentre la fila del usuario.
2. Haga clic en el badge de estado (el botón verde **Activo** o gris **Inactivo**).
3. El estado cambiará al contrario: de Activo a Inactivo, o viceversa.

**Efectos de desactivar una cuenta:**
- El usuario ya **no puede iniciar sesión** en el sistema.
- Toda la información que registró **se conserva intacta** en el historial.
- Los expedientes y registros asociados a ese usuario no se modifican.

> **Importante:** Cuando un miembro del personal se retira del Hogar, **desactive su cuenta de inmediato**. No espere días. Dejar una cuenta activa de alguien que ya no trabaja en el Hogar es un riesgo de seguridad.

---

## Buenas prácticas de seguridad

- **Una cuenta por persona.** Nunca cree una cuenta genérica (ej. "personal@hogar.com") que usen varias personas.
- **Desactive las cuentas inmediatamente** cuando alguien deja el Hogar.
- **Use contraseñas robustas.** Al menos 8 caracteres, combinando letras, números y símbolos.
- **Limite el número de administradores.** Solo las personas que realmente necesitan acceso total deben tener el rol de Administrador.
- **No comparta credenciales de administrador.** Si otra persona necesita hacer algo que requiere rol de Administrador, hágalo usted mismo o créele su propia cuenta con el rol apropiado.

---

## En resumen

- Cada miembro del personal debe tener su propia cuenta con su propio correo y contraseña.
- Al crear un usuario, el sistema no envía las credenciales automáticamente — infórmeselas personalmente.
- El rol determina qué puede ver y hacer cada usuario. Elíjalo con cuidado.
- Desactive las cuentas de inmediato cuando alguien deja el Hogar.
- Los datos de los usuarios inactivos se conservan en el sistema — solo se les bloquea el acceso.
