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
| **Correo electrónico** | Este será el nombre de usuario para iniciar sesión. **No necesita ser un correo real que la persona revise** — es solo un identificador de acceso, ya que el sistema no envía correos. Debe ser único. | Sí |
| **Rol** | Una etiqueta que describe qué es esta persona (ver más abajo). No determina por sí sola qué puede ver o hacer. | Sí |
| **Módulos habilitados** | Las secciones del sistema a las que esta persona podrá entrar (ver "Módulos y accesos" más abajo). Si el rol es Administrador, este paso se omite: el Administrador siempre tiene acceso a todo. | Sí (salvo Administrador) |
| **Contraseña** | La contraseña inicial (temporal). Sin restricción de formato — elija algo que pueda dictarle a la persona con facilidad. | Sí |

4. Haga clic en **Crear usuario**.

> **Importante:** El sistema **no envía automáticamente** las credenciales al nuevo usuario por correo electrónico (el sistema no envía correos en absoluto). Debe informarle su usuario (correo) y contraseña de manera personal o por un medio seguro (no por WhatsApp público ni redes sociales).

> **Consejo:** El cambio de contraseña por parte del usuario es opcional, no obligatorio. Si quiere que la cambie, indíqueselo y explíquele cómo hacerlo desde **Mi Perfil** (Capítulo 13).

---

## Los roles: una etiqueta, no un permiso

El **rol** describe qué es la persona (Médico, Psicólogo, Consejero, etc.). Se usa para identificarla en los reportes y para vincularla como Profesional (Capítulo 12), pero **ya no determina por sí solo el acceso a los módulos del sistema**. El acceso real lo define la lista de **módulos habilitados** de cada usuario (ver siguiente sección).

La única excepción es el rol **Administrador**: siempre tiene acceso completo a todas las secciones del sistema, incluyendo Administración, y esto no se puede desmarcar. Esto evita que un administrador quede accidentalmente bloqueado fuera de su propia cuenta.

| Rol | Quién suele tenerlo |
|---|---|
| **Administrador** | Dueños o directores del Hogar. Acceso total, siempre. |
| **Recepcionista** | Personal de recepción o administración. |
| **Consejero** | Consejeros y coordinadores clínicos. |
| **Médico** | Médico del centro o de referencia. |
| **Trabajador Social** | Trabajador(a) social. |
| **Psicólogo** | Psicólogo(a). |
| **Terapeuta Ocupacional** | Terapeuta ocupacional. |

---

## Módulos y accesos: qué puede ver cada usuario

Al crear o editar un usuario (salvo que sea Administrador), usted marca con casillas qué secciones puede usar esa persona:

| Módulo | Qué habilita |
|---|---|
| **Clínica / Residentes** | Ver la lista de residentes y sus fichas. |
| **Operación** | Pase de medicamentos, asistencia, ocupación y entrega de turno (las cuatro sub-secciones juntas, un solo interruptor). |
| **Finanzas** | Resumen de morosidad, cobros y pagos. |
| **Reportes** | Reportes de admisiones, consultas y progreso. |
| **Evaluación Médica** | Ver y editar la evaluación médica del expediente. |
| **Evaluación Psicológica** | Ver y editar la evaluación psicológica. |
| **Evaluación Terapéutica** | Ver y editar la evaluación terapéutica. |
| **Trabajo Social** | Ver y editar la evaluación de trabajo social. |
| **Terapia Ocupacional** | Ver y editar la evaluación de terapia ocupacional. |

El **Panel principal** (Dashboard) y **Mi Perfil** están siempre disponibles para cualquier usuario, sin necesidad de marcarlos. La sección **Administración** (este capítulo y el siguiente) es siempre exclusiva del rol Administrador.

> **Ejemplo:** Si contrata a una psicóloga que también necesita ver la lista de residentes, márquele los módulos **Clínica / Residentes** y **Evaluación Psicológica**. No necesita marcarle Finanzas ni Operación si no le corresponden.

> **Nota:** Puede cambiar los módulos habilitados de un usuario en cualquier momento desde la tabla de usuarios (ver "Cambiar los módulos habilitados" más abajo). El cambio queda aplicado la próxima vez que esa persona inicie sesión.

---

## Cambiar el rol de un usuario

Si la función de una persona en el Hogar cambia (ej. pasó de Consejero a Coordinador):

1. En la tabla de usuarios, encuentre al usuario que desea modificar.
2. Haga clic en el menú desplegable de la columna **Rol**.
3. Seleccione el nuevo rol.
4. Haga clic en el botón **Guardar** que aparece junto al desplegable.

[CAPTURA: fila de usuario con el menú desplegable de rol abierto y el botón "Guardar" visible]

> **Recuerde:** cambiar el rol **no cambia automáticamente** los módulos habilitados de la persona. Si su acceso también debe cambiar, ajústelo por separado (ver siguiente sección).

---

## Cambiar los módulos habilitados de un usuario

Si necesita dar más o menos acceso a alguien (por ejemplo, ya no debe ver Finanzas, o ahora también necesita Reportes):

1. En la tabla de usuarios, en la columna **Módulos**, haga clic en el texto que muestra cuántos módulos tiene (o "Sin módulos").
2. Se despliega la lista de casillas. Marque o desmarque los módulos según corresponda.
3. Haga clic en **Guardar**.

[CAPTURA: fila de usuario con la lista de casillas de módulos desplegada y el botón "Guardar" visible]

> **Importante:** El cambio se aplica la próxima vez que esa persona inicie sesión, no de manera instantánea mientras tiene la sesión abierta. Si necesita que el cambio sea inmediato, pídale que cierre sesión y vuelva a entrar.

> **Nota:** Si el usuario tiene rol Administrador, esta columna muestra "Acceso total (fijo)" y no se puede editar — el Administrador siempre ve todo el sistema.

---

## Restablecer la contraseña de un usuario

El sistema no permite que un usuario recupere su contraseña por sí mismo (no hay "olvidé mi contraseña" con envío de correo, ya que el sistema no envía correos). Si alguien olvida su contraseña:

1. En la tabla de usuarios, encuentre la fila de la persona.
2. Haga clic en **Restablecer contraseña**, en la columna de la derecha.
3. Escriba una contraseña temporal en el campo que aparece.
4. Haga clic en **Restablecer**.
5. Comuníquele la contraseña temporal a la persona de manera personal o por un medio seguro.

[CAPTURA: modal de "Restablecer contraseña" con el campo de nueva contraseña temporal y el botón "Restablecer"]

La persona puede seguir usando esa contraseña temporal indefinidamente, o cambiarla ella misma desde **Mi Perfil** (Capítulo 13) — el cambio es opcional, no obligatorio.

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
- **Marque solo los módulos que la persona realmente necesita.** No habilite Finanzas o Administración "por si acaso".
- **Use contraseñas temporales que pueda dictar con facilidad**, pero evite las obvias (nombre del Hogar, "1234", etc.).
- **Limite el número de administradores.** Solo las personas que realmente necesitan acceso total deben tener el rol de Administrador — recuerde que ese rol no se puede restringir por módulo.
- **No comparta credenciales de administrador.** Si otra persona necesita hacer algo que requiere rol de Administrador, hágalo usted mismo o créele su propia cuenta con el rol apropiado.

---

## En resumen

- Cada miembro del personal debe tener su propia cuenta con su propio usuario (correo) y contraseña.
- Al crear un usuario, el sistema no envía las credenciales automáticamente ni por correo — infórmeselas personalmente.
- El **rol** es una etiqueta descriptiva; los **módulos habilitados** son los que realmente determinan qué puede ver y hacer cada usuario (excepto el Administrador, que siempre tiene acceso total).
- Puede restablecer la contraseña de cualquier usuario desde esta pantalla si la olvidó.
- Desactive las cuentas de inmediato cuando alguien deja el Hogar.
- Los datos de los usuarios inactivos se conservan en el sistema — solo se les bloquea el acceso.
