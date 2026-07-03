# Capítulo 9: Módulo de Finanzas

> Este capítulo le explica cómo ver el resumen financiero del Hogar, generar cobros mensuales y gestionar los pagos de cada residente.

---

## ¿Quién puede ver las finanzas?

El módulo de Finanzas requiere que el Administrador le haya habilitado ese módulo específico a su usuario (ver Capítulo 11). Típicamente lo tienen el Administrador y el personal de Recepción, pero esto se configura persona por persona, no de forma automática por rol. Si tiene el módulo habilitado, verá la opción **Finanzas** en el menú lateral.

> **Nota:** Esta restricción es intencional para proteger la privacidad financiera de los residentes y del Hogar. Si necesita acceso y no lo tiene, pídaselo al Administrador.

---

## Abrir el módulo

1. En el menú lateral, haga clic en **Finanzas**.
2. Seleccione **Resumen y morosidad**.

[CAPTURA: pantalla del módulo de finanzas mostrando: el selector de período en la parte superior, el botón "Generar cobros", las tarjetas de resumen, la tabla de desglose por tipo de pagador y la tabla de morosidad]

---

## Seleccionar el período

En la parte superior de la pantalla encontrará un selector de período (mes y año). El sistema mostrará únicamente los datos del mes seleccionado.

1. Haga clic en el campo de período.
2. Seleccione el mes y año que desea consultar.
3. La información en la pantalla se actualizará automáticamente.

---

## Generar cobros mensuales

Al inicio de cada mes, el sistema puede generar automáticamente los cobros para todos los residentes que tienen un **acuerdo de pago activo**.

1. Asegúrese de tener seleccionado el período del mes actual.
2. Haga clic en el botón **Generar cobros**.
3. El sistema creará un registro de cobro para cada residente con acuerdo activo, usando el monto y la frecuencia establecidos en su acuerdo de pago.
4. Aparecerá un mensaje de confirmación en verde cuando el proceso termine.

> **Importante:** Solo genere los cobros **una vez por mes**. Si genera cobros más de una vez en el mismo período, se duplicarán los registros de cobro, lo que causará errores en los saldos. Si esto ocurre por accidente, comuníquese con el administrador técnico del sistema.

> **Consejo:** Establezca como rutina generar los cobros el primer día hábil de cada mes.

---

## El resumen financiero del período

Después de seleccionar un período, la pantalla mostrará:

### Total recibido

[CAPTURA: tarjeta grande mostrando el total recibido en el período con el símbolo ₡ y el monto en negrita]

Suma de todos los pagos recibidos durante el mes seleccionado, sin importar el método de pago ni quién pagó.

### Residentes con morosidad

[CAPTURA: dos tarjetas pequeñas mostrando: "Residentes con saldo pendiente" (número) y "Total de morosidad" (monto en ₡)]

- **Residentes con saldo pendiente:** Cuántos residentes activos tienen un saldo sin pagar.
- **Total de morosidad:** La suma total de todos esos saldos pendientes.

### Desglose por tipo de pagador

[CAPTURA: tabla de desglose mostrando filas para cada tipo de pagador: Familia/Responsable, IAFA, IMAS, Iglesia, Donante, Otro; con el monto total recibido de cada uno]

Esta tabla muestra cuánto se recibió durante el período según quién realizó el pago:

| Tipo de pagador | Descripción |
|---|---|
| **Familia / Responsable** | Pagos realizados por la familia o el patrocinador del residente. |
| **IAFA** | Pagos cubiertos por el Instituto sobre Alcoholismo y Farmacodependencia. |
| **IMAS** | Pagos cubiertos por el Instituto Mixto de Ayuda Social. |
| **Iglesia** | Pagos realizados por una iglesia u organización religiosa. |
| **Donante** | Pagos realizados por donantes individuales o institucionales. |
| **Otro** | Pagos de cualquier otra fuente. |

Esta información es especialmente útil para los reportes de rendición de cuentas a donantes y para las solicitudes de renovación de convenios con el IAFA o el IMAS.

---

## La tabla de morosidad

[CAPTURA: tabla de morosidad mostrando columnas: Residente (enlace en azul), Saldo pendiente (en rojo), Cargo más antiguo, Días de mora (badge rojo)]

La tabla de morosidad muestra todos los residentes activos que tienen saldo pendiente:

| Columna | Descripción |
|---|---|
| **Residente** | Nombre del residente. Haga clic para ir a su cuenta individual. |
| **Saldo pendiente** | Cuánto debe en total (en colones). |
| **Cargo más antiguo** | La fecha del cobro sin pagar más antiguo. |
| **Días de mora** | Cuántos días han pasado desde ese cargo más antiguo. |

Los residentes con más días de mora aparecen primero en la lista.

> **Consejo:** Revise esta tabla al inicio de cada mes para identificar las cuentas que necesitan seguimiento prioritario.

---

## La cuenta individual del residente

Para ver el detalle financiero de un residente específico, haga clic en su nombre en la tabla de morosidad, o acceda desde la sección **Control financiero** dentro de su expediente de admisión (Capítulo 4, Sección 15).

[CAPTURA: pantalla de cuenta individual mostrando: sección de acuerdo de pago en la parte superior, luego dos columnas con la tabla de cobros a la izquierda y la tabla de pagos a la derecha, y el saldo actual destacado]

---

### Configurar el acuerdo de pago

Antes de que el sistema pueda generar cobros automáticos para un residente, debe tener un acuerdo de pago configurado.

1. En la cuenta individual del residente, busque la sección **Acuerdo de pago**.
2. Complete o actualice los campos:

| Campo | Descripción |
|---|---|
| **Tipo de acuerdo** | Mensualidad (cobro mensual fijo), Monto fijo total (una suma única), Beca total (sin costo para el residente), Beca parcial (cubre parte del costo). |
| **Monto** | La cantidad a cobrar según el tipo de acuerdo. |
| **Día de cobro** | El día del mes en que se genera el cobro (para acuerdos de mensualidad). |

3. Haga clic en **Guardar acuerdo**.

---

### Registrar un cobro manual

Si necesita agregar un cobro que no fue generado automáticamente (por ejemplo, un cobro extraordinario por ropa de cama o artículos de aseo):

1. En la cuenta individual, haga clic en **+ Agregar cobro**.
2. Complete los campos:

| Campo | Descripción | ¿Obligatorio? |
|---|---|---|
| **Concepto** | Descripción del cobro (ej. "Mensualidad enero", "Artículos de aseo"). | Sí |
| **Monto** | Cantidad en colones. | Sí |
| **Fecha** | Fecha del cobro. | Sí |
| **Notas** | Observaciones adicionales. | No |

3. Haga clic en **Guardar cobro**.

---

### Registrar un pago

Cuando el residente o su familia realiza un pago:

1. En la cuenta individual, haga clic en **+ Registrar pago**.
2. Se abrirá el formulario de pago.

[CAPTURA: formulario de registro de pago mostrando todos los campos con el campo Método desplegado mostrando las opciones: Efectivo, SINPE Móvil, Transferencia, Cheque, Otro]

3. Complete los campos:

| Campo | Descripción | ¿Obligatorio? |
|---|---|---|
| **Monto** | Cantidad pagada en colones. | Sí |
| **Fecha** | Fecha en que se recibió el pago. | Sí |
| **Método de pago** | Seleccione: Efectivo, SINPE Móvil, Transferencia, Cheque u Otro. | Sí |
| **Tipo de pagador** | Quién realizó el pago: Familia, IAFA, IMAS, Iglesia, Donante u Otro. | Sí |
| **Nombre del pagador** | Nombre de la persona o institución que pagó. | No |
| **Referencia** | Número de confirmación (para SINPE: el número de confirmación del mensaje; para cheque: el número del cheque; para transferencia: el número de la transferencia). | No |
| **Notas** | Cualquier observación adicional. | No |

4. Haga clic en **Guardar pago**.

El pago se agregará a la tabla de pagos y el saldo se actualizará automáticamente.

---

### El saldo actual

En la parte superior de la cuenta individual verá el **saldo actual** del residente:

- **Saldo positivo (en rojo):** El residente debe dinero. El número indica cuánto debe.
- **Saldo en cero:** La cuenta está al día.
- **Saldo negativo (en verde):** El residente tiene un crédito a favor (pagó de más).

El saldo se calcula automáticamente: **Saldo = Total de cobros − Total de pagos**.

---

## Consejos de gestión financiera

- Genere los cobros el primer día hábil de cada mes para tener los saldos actualizados desde el inicio.
- Registre los pagos el mismo día en que los recibe para mantener los saldos exactos.
- Al recibir un pago por **SINPE Móvil**, guarde siempre el número de confirmación del mensaje como referencia.
- Revise la tabla de morosidad mensualmente y contacte a las familias de los residentes con mayor número de días de mora.

---

## En resumen

- El módulo de Finanzas requiere que el Administrador lo habilite en su usuario (típicamente Administradores y Recepcionistas, pero se configura por persona).
- Seleccione el período (mes y año) para ver los datos de ese mes.
- Genere los cobros mensuales una sola vez al inicio de cada mes.
- La tabla de morosidad muestra quiénes tienen saldo pendiente y cuántos días llevan sin pagar.
- Para cada residente puede configurar un acuerdo de pago, registrar cobros adicionales y registrar pagos.
- El saldo se calcula automáticamente: cobros menos pagos.
