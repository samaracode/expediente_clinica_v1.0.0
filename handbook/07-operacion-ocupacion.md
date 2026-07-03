# Capítulo 7: Ocupación y Lista de Espera

> Este capítulo le explica cómo ver el estado de ocupación del Hogar y cómo gestionar la lista de personas que esperan un cupo.

---

## ¿Para qué sirve este módulo?

El módulo de Ocupación le permite:

- Ver en tiempo real cuántos residentes hay en el Hogar y cuántos cupos quedan disponibles.
- Ajustar la capacidad total del Hogar si se agregan o retiran camas.
- Gestionar la lista de espera de personas que han solicitado ingreso pero aún no tienen cupo.

---

## Abrir el módulo

1. En el menú lateral, haga clic en **Operación**.
2. Seleccione **Ocupación**.

[CAPTURA: pantalla completa del módulo de Ocupación mostrando las 4 tarjetas en la parte superior, la barra de progreso debajo y la tabla de lista de espera más abajo]

---

## Las tarjetas de capacidad

En la parte superior de la pantalla encontrará cuatro tarjetas:

[CAPTURA: las 4 tarjetas de capacidad mostrando: Total camas, Ocupadas, Disponibles, y un desglose por estado de admisión]

| Tarjeta | Qué muestra |
|---|---|
| **Total de camas** | El número de camas configurado en el sistema. Este es el número que puede ajustar (ver sección "Editar la capacidad"). |
| **Camas ocupadas** | Número de residentes con estado **Tratamiento activo** en este momento. |
| **Camas disponibles** | La diferencia entre el total y las camas ocupadas. |
| **Distribución por estado** | Cuántas admisiones hay en cada etapa del proceso (tratamiento activo, en evaluación, etc.). |

---

## La barra de ocupación

[CAPTURA: barra de progreso horizontal mostrando el porcentaje de ocupación con color verde, seguida de texto indicando el porcentaje]

Debajo de las tarjetas encontrará una barra visual que muestra el porcentaje de ocupación actual. El color de la barra cambia según el nivel:

| Color | Rango | Qué significa |
|---|---|---|
| 🟢 **Verde** | Menos del 70 % | Buena disponibilidad. |
| 🟡 **Amarillo** | Entre 70 % y 90 % | Ocupación alta. Conviene revisar la lista de espera. |
| 🔴 **Rojo** | 90 % o más | Casi sin cupos. Evalúe si puede ampliar la capacidad. |

---

## Editar la capacidad total

Si el Hogar agrega camas, las retira temporalmente (por ejemplo, durante una remodelación) o ajusta su capacidad operativa, actualice este número en el sistema:

1. Haga clic en el botón **Editar capacidad**.
2. Se abrirá un pequeño cuadro de diálogo.

[CAPTURA: cuadro de diálogo con el campo "Capacidad total" pre-llenado con el número actual y los botones "Guardar" y "Cancelar"]

3. Borre el número actual y escriba el nuevo número de camas disponibles.
4. Haga clic en **Guardar**.

El porcentaje de ocupación y las tarjetas se actualizarán automáticamente con el nuevo número.

> **Consejo:** Actualice la capacidad cada vez que haya un cambio físico en las camas disponibles. Mantener este número actualizado garantiza que el panel principal y los reportes reflejen la realidad del Hogar.

---

## La lista de espera

La parte inferior de la pantalla muestra la lista de personas que han solicitado ingreso al Hogar pero aún no tienen un cupo asignado.

[CAPTURA: tabla de lista de espera con columnas: Nombre, Teléfono, Correo, Fecha de solicitud, Referido por, Estado, Notas; y el botón "+ Agregar a lista de espera" en la parte superior derecha]

Las columnas de la tabla son:

| Columna | Descripción |
|---|---|
| **Nombre** | Nombre completo de la persona en espera. |
| **Teléfono** | Número de contacto. |
| **Correo** | Correo electrónico (si se registró). |
| **Fecha de solicitud** | Fecha en que se registró la solicitud de ingreso. |
| **Referido por** | Quién refirió a esta persona al Hogar. |
| **Estado** | Estado actual en la lista de espera (ver abajo). |
| **Notas** | Observaciones adicionales. |

### Los estados de la lista de espera

| Estado | Badge | Significado |
|---|---|---|
| **En espera** | Amarillo | La persona está esperando un cupo disponible. |
| **Admitido** | Verde | La persona fue admitida al Hogar. |
| **Rechazado** | Rojo | La solicitud fue rechazada. |
| **Cancelado** | Gris | La persona canceló la solicitud o ya no está disponible. |

---

## Agregar una persona a la lista de espera

Cuando alguien contacta al Hogar solicitando ingreso pero no hay cupo disponible:

1. Haga clic en el botón **+ Agregar a lista de espera**.
2. Se abrirá un cuadro de diálogo con el formulario.

[CAPTURA: cuadro de diálogo de nueva entrada en lista de espera con todos los campos]

3. Complete los campos:

| Campo | Descripción | ¿Obligatorio? |
|---|---|---|
| **Nombre completo** | Nombre de la persona interesada en ingresar. | Sí |
| **Teléfono de contacto** | Número para llamarle cuando haya cupo. | No |
| **Correo electrónico** | Correo alternativo de contacto. | No |
| **Fecha de solicitud** | La fecha en que se recibió la solicitud. Por defecto es hoy. | No |
| **Referido por** | Quién refirió a esta persona. | No |
| **Notas** | Cualquier observación relevante (condición de ingreso, urgencia, etc.). | No |

4. Haga clic en **Agregar**.

La persona aparecerá en la lista con el estado **En espera**.

---

## Actualizar el estado de una persona en espera

Cuando la situación de una persona en la lista de espera cambia, actualice su estado:

1. En la tabla, busque la fila de la persona.
2. Haga clic en el botón de acción correspondiente al nuevo estado:
   - **Admitir:** Use este estado cuando haya un cupo disponible y la persona va a ingresar. Recuerde también crear al residente en el sistema (Capítulo 3) y registrar su admisión (Capítulo 4).
   - **Rechazar:** Use este estado si la solicitud no puede ser atendida.
   - **Cancelar:** Use este estado si la persona ya no desea ingresar o no fue posible contactarla.

> **Nota:** Si admite a una persona desde la lista de espera, el sistema **no crea automáticamente** la ficha del residente ni la admisión. Debe hacerlo manualmente en el módulo de Residentes (Capítulo 3).

---

## Filtrar la lista de espera

Si la lista tiene muchas personas, puede filtrarla por estado usando el menú desplegable ubicado sobre la tabla. Por ejemplo, puede mostrar solo las personas con estado **En espera** para ver quiénes están pendientes de una llamada de seguimiento.

---

## En resumen

- El módulo de Ocupación muestra en tiempo real cuántas camas están ocupadas y cuántas están disponibles.
- La barra de ocupación cambia de verde a amarillo a rojo según el nivel de ocupación.
- Actualice la capacidad total cuando haya cambios físicos en el número de camas del Hogar.
- La lista de espera registra a las personas que solicitan ingreso cuando no hay cupo.
- Cuando una persona de la lista de espera ingresa al Hogar, recuerde también crear su ficha de residente y su admisión en el sistema.
