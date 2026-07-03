# Capítulo 3: Gestión de Residentes

> Este capítulo le explica cómo crear, buscar, editar y administrar la ficha de cada residente del Hogar, incluyendo sus alergias y su red familiar.

---

## La lista de residentes

Para acceder a los residentes, haga clic en **Clínica → Residentes** en el menú lateral.

[CAPTURA: pantalla de lista de residentes mostrando la tabla con columnas Código, Nombre, Cédula, Teléfono, Fecha de ingreso; el campo de búsqueda en la parte superior; y el botón "+ Nuevo residente" en la esquina superior derecha]

La tabla muestra todos los residentes activos con las siguientes columnas:

| Columna | Qué muestra |
|---|---|
| **Código** | Identificador único del residente en el sistema (ej. RES-001). |
| **Nombre** | Nombre completo del residente. |
| **Cédula** | Número de identificación. Muestra un guión (—) si no fue registrada. |
| **Teléfono** | Número de contacto principal. |
| **Fecha de ingreso** | Fecha en que fue creado el registro en el sistema. |

### Buscar un residente

1. Haga clic en el campo de búsqueda en la parte superior de la lista.
2. Escriba el nombre o número de cédula del residente.
3. La lista se filtra automáticamente mientras escribe.
4. Para ver todos los residentes nuevamente, borre el texto del campo de búsqueda.

> **Consejo:** Puede buscar por nombre parcial. Por ejemplo, escribir "Gon" mostrará a "González, Mario" y a "Gontier, Ana".

### Ver residentes archivados

> **Solo para administradores:** En la parte superior de la lista hay una casilla de verificación que dice **Mostrar archivados**. Al marcarla, también aparecerán los residentes que han sido archivados. Los residentes archivados muestran un distintivo gris junto a su nombre.

### Paginación

La lista muestra 20 residentes por página. Use los botones de navegación en la parte inferior para avanzar o retroceder entre páginas.

---

## Crear un nuevo residente

Cuando ingresa un nuevo residente al Hogar, el primer paso es crear su ficha en el sistema.

1. Haga clic en el botón **+ Nuevo residente** en la esquina superior derecha.
2. Se abrirá el formulario de registro.

[CAPTURA: formulario de nuevo residente con todos los campos visibles]

3. Complete los campos del formulario:

| Campo | Descripción | ¿Obligatorio? |
|---|---|---|
| **Nombre** | Primer nombre del residente | Sí |
| **Apellidos** | Apellidos del residente | Sí |
| **Cédula** | Número de identificación (formato: 0-0000-0000 para cédula costarricense) | No |
| **Fecha de nacimiento** | Use el selector de fecha que aparece al hacer clic en el campo | No |
| **Sexo** | Masculino, Femenino u Otro | No |
| **Estado civil** | Soltero, Casado, Divorciado, Viudo, Unión libre | No |
| **Teléfono celular** | Número de celular del residente | No |
| **Teléfono casa** | Número de teléfono fijo | No |
| **Correo electrónico** | Correo del residente | No |
| **Provincia / Cantón / Distrito** | Ubicación de residencia | No |
| **Dirección** | Dirección específica | No |
| **Nacionalidad** | País de origen | No |
| **Asegurado** | Marque si el residente tiene seguro de la CCSS | No |
| **Contacto de emergencia** | Nombre de la persona a contactar en caso de emergencia | No |
| **Teléfono de emergencia** | Teléfono del contacto de emergencia | No |

4. Haga clic en el botón **Crear residente**.
5. El sistema lo llevará automáticamente al perfil del residente recién creado.

> **Nota:** Los campos marcados con asterisco (\*) son obligatorios. El sistema no le permitirá guardar si están vacíos. El resto de la información puede completarse o actualizarse en cualquier momento.

---

## El perfil del residente

Al hacer clic en **Ver** junto a cualquier residente de la lista, accede a su perfil completo.

[CAPTURA: pantalla de perfil de residente mostrando: (1) encabezado con código y nombre, (2) cuadrícula de datos demográficos, (3) tabla de admisiones, (4) sección de alergias, (5) botones de acción en la parte superior]

El perfil está organizado en estas secciones:

### Encabezado
Muestra el **código único** del residente (en formato especial) y su **nombre completo**, además de los botones de acción principales.

### Datos demográficos
Muestra en una cuadrícula los datos personales: edad calculada automáticamente a partir de la fecha de nacimiento, número de cédula, teléfono, provincia, y los datos del contacto de emergencia.

### Historial de admisiones
Tabla con todas las admisiones que ha tenido este residente, incluyendo:
- Número de admisión
- Fecha de ingreso
- Tipo (Primera vez / Reingreso)
- Estado actual de la admisión

Haga clic en cualquier admisión para abrir su expediente completo.

### Alergias
Lista de las alergias conocidas del residente (ver sección siguiente).

---

## Editar los datos del residente

Si necesita corregir o actualizar información:

1. Abra el perfil del residente.
2. Haga clic en el botón **Editar** en la parte superior del perfil.
3. El formulario se abrirá con los datos actuales pre-llenados.
4. Modifique los campos que necesite.
5. Haga clic en **Guardar cambios**.

---

## Registrar alergias

Las alergias son muy importantes: aparecerán como alertas de advertencia en el módulo de Pase de medicamentos para que el personal esté siempre informado.

[CAPTURA: sección de alergias mostrando una alergia existente con badge de severidad "Moderada" en color naranja, y el botón "+ Agregar alergia"]

### Agregar una alergia

1. En el perfil del residente, desplácese hasta la sección **Alergias**.
2. Haga clic en **+ Agregar alergia**.
3. Complete los campos:

| Campo | Descripción |
|---|---|
| **Sustancia** | La sustancia a la que el residente es alérgico (ej. Penicilina, maní, látex). *Obligatorio.* |
| **Reacción** | Descripción de cómo reacciona el residente (ej. "sarpullido", "dificultad para respirar"). |
| **Severidad** | Seleccione una de las tres opciones: **Leve**, **Moderada** o **Severa**. |

4. Haga clic en **Guardar alergia**.

La alergia aparecerá en la lista y, a partir de ese momento, se mostrará como una alerta de color en el pase de medicamentos:
- 🟡 **Amarillo** = Leve
- 🟠 **Naranja** = Moderada
- 🔴 **Rojo** = Severa

### Eliminar una alergia

1. En la lista de alergias, haga clic en el botón **Eliminar** junto a la alergia.
2. El sistema pedirá confirmación. Haga clic en **Sí, eliminar** para confirmar.

> **Importante:** Solo elimine una alergia si fue registrada por error. Si el residente ya no presenta esa alergia clínicamente, consúltelo con el personal médico antes de borrarla.

---

## Gestionar la red familiar

El sistema permite registrar a los familiares y personas cercanas al residente. Esta información es útil para la red de apoyo y para el trabajo social.

1. En el perfil del residente, haga clic en el botón **Familiares**.
2. Verá la lista de familiares registrados.

[CAPTURA: página de familiares mostrando tarjetas expandibles para cada familiar con nombre, relación y edad]

### Agregar un familiar

1. Haga clic en **+ Agregar familiar**.
2. Complete el formulario:

| Campo | Descripción |
|---|---|
| **Tipo de relación** | Parentesco con el residente (ej. Madre, Padre, Hermano, Cónyuge) |
| **Nombre** | Primer nombre del familiar |
| **Apellido** | Apellido(s) del familiar |
| **Cédula** | Número de identificación |
| **Fecha de nacimiento** | Para calcular edad |
| **Estado civil** | Soltero, Casado, etc. |
| **Teléfono** | Número de contacto |
| **Nivel educativo** | Ninguno, Primaria, Secundaria, Técnico, Universidad, Posgrado |
| **Situación judicial** | Si tiene alguna situación legal relevante |
| **Dirección** | Lugar de residencia |

3. Haga clic en **Guardar familiar**.

### Editar o desvincular un familiar

- Para editar: haga clic en la tarjeta del familiar para expandirla y modifique los campos que necesite.
- Para desvincular: haga clic en **Desvincular** y confirme la acción. El registro del familiar no se borra del sistema, solo se elimina la relación con este residente.

---

## Archivar un residente

> **Solo para administradores:** Esta acción solo la puede realizar el Administrador.

Archivar un residente lo oculta de la lista principal pero **no borra su información**. Todo su historial, expedientes y registros se conservan. Use esta opción cuando un residente ya no tiene vinculación activa con el Hogar y no espera un reingreso próximo.

1. Abra el perfil del residente.
2. Haga clic en el botón **Archivar** en la parte superior del perfil.
3. El sistema mostrará un mensaje de confirmación.

[CAPTURA: cuadro de confirmación de archivo con el mensaje "¿Está seguro de que desea archivar a este residente?" y los botones "Sí, archivar" y "Cancelar"]

4. Haga clic en **Sí, archivar** para confirmar.

El residente desaparecerá de la lista principal. Para encontrarlo nuevamente, marque la casilla **Mostrar archivados** en la lista de residentes.

> **Nota:** El archivado no es permanente. Si necesita volver a activar a un residente archivado (por ejemplo, si reingresa), comuníquese con el administrador del sistema.

---

## Crear una nueva admisión

Una vez que el residente está registrado en el sistema, el siguiente paso es crear una admisión cuando ingresa al Hogar. Esto se hace desde el perfil del residente.

1. Abra el perfil del residente.
2. Haga clic en el botón **+ Nueva admisión**.
3. Se abrirá el formulario de admisión.

Para más detalles sobre el proceso de admisión, continúe con el **Capítulo 4: El Expediente de Admisión**.

---

## En resumen

- Acceda a los residentes desde **Clínica → Residentes** en el menú lateral.
- Puede buscar residentes por nombre o cédula usando el campo de búsqueda.
- Al crear un residente, solo nombre y apellidos son obligatorios; el resto puede completarse después.
- Las alergias registradas aparecen como alertas de color en el pase de medicamentos.
- Archivar un residente lo oculta de la lista principal pero conserva toda su información.
- Para ingresar a un residente al programa, cree una nueva admisión desde su perfil.
