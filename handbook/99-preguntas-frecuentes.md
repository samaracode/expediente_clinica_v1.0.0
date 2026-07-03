# Preguntas Frecuentes y Solución de Problemas

> Esta sección reúne las dudas más comunes que pueden surgir al usar el sistema, con respuestas directas y pasos para resolverlas.

---

## Acceso y contraseñas

**¿Qué hago si olvidé mi contraseña?**

El sistema no permite restablecer la contraseña por su cuenta desde la pantalla de inicio de sesión. Debe comunicarse con el Administrador del sistema (el dueño o director del Hogar) para que la restablezca desde **Administración → Usuarios**. Una vez restablecida, inicie sesión con la nueva contraseña y cámbiela desde **Mi Perfil** (Capítulo 13).

---

**¿Por qué el sistema dice "Credenciales incorrectas"?**

Esto significa que el correo o la contraseña escritos no coinciden con ninguna cuenta activa. Verifique:
- Que su correo esté escrito correctamente (sin espacios al principio ni al final).
- Que las mayúsculas y minúsculas de la contraseña sean las correctas.
- Que su cuenta esté activa (si fue desactivada por el Administrador, no podrá entrar).

Si todo parece correcto y sigue sin poder entrar, comuníquese con el Administrador.

---

**¿Por qué no veo la opción "Administración" en el menú?**

La sección de Administración solo es visible para el rol de **Administrador**, y esto no se puede habilitar a otros usuarios por módulo. Si necesita realizar una gestión de usuarios o del catálogo de medicamentos, pídaselo a la persona con rol Administrador.

---

**¿Por qué no veo alguna sección que antes sí veía (o un compañero sí ve)?**

Desde que el sistema usa módulos habilitados por usuario, el acceso ya no depende únicamente del rol: dos personas con el mismo rol pueden tener módulos distintos si el Administrador así lo configuró. Si le falta acceso a una sección que necesita para su trabajo, pídale al Administrador que revise sus módulos habilitados desde **Administración → Usuarios** (Capítulo 11).

---

**El Administrador me cambió los módulos habilitados pero sigo viendo lo mismo (o sigo sin ver la sección nueva). ¿Qué pasa?**

Los cambios de módulos se aplican la próxima vez que inicia sesión, no de manera instantánea si ya tiene el sistema abierto. Cierre sesión (esquina superior derecha → Cerrar sesión) y vuelva a entrar con su usuario y contraseña. Debería ver el cambio reflejado de inmediato.

---

**¿Por qué no veo la tarjeta de "Saldo por cobrar" en el panel principal?**

Esta tarjeta solo es visible para los roles de **Administrador** y **Recepcionista**. Si tiene otro rol, el sistema la oculta automáticamente. Esto es intencional para proteger la privacidad financiera del Hogar.

---

## Residentes y admisiones

**¿Puedo borrar un residente del sistema?**

No. El sistema no permite borrar registros de residentes de manera permanente. Solo es posible **archivarlos**, lo que los oculta de la lista principal pero conserva toda su información. Esto protege el historial del Hogar ante cualquier revisión futura. Para archivar un residente, consulte el Capítulo 3.

---

**¿Cuántas admisiones puede tener un residente?**

No hay límite. Un residente puede tener tantas admisiones como episodios de ingreso haya tenido en el Hogar. Cada admisión queda registrada de manera independiente con su propio expediente completo. Esto es especialmente útil para los reingresos, donde puede ver el historial completo de estadías anteriores.

---

**¿Qué significa que una admisión dice "Egresado"?**

Significa que ese episodio de ingreso fue cerrado formalmente. El residente fue dado de alta y el proceso de esa admisión específica está concluido. Si el mismo residente reingresa al Hogar en el futuro, se creará una nueva admisión con su propio expediente.

---

**¿Puedo crear una nueva admisión si el residente ya tiene una activa?**

Sí, el sistema lo permite técnicamente. Sin embargo, en la práctica, un residente solo debe tener una admisión activa a la vez. Si necesita crear una nueva admisión porque el residente está reingresando, asegúrese primero de que la admisión anterior esté cerrada (con estado "Egresado" o "Abandono").

---

**¿Por qué no puedo editar (o ni siquiera ver) la evaluación médica de un expediente?**

Cada evaluación clínica (médica, psicológica, terapéutica, trabajo social, terapia ocupacional) tiene su propio módulo de acceso. Solo puede verla y editarla quien tenga ese módulo específico habilitado (o el Administrador, que siempre tiene acceso a todo). Si necesita acceso a una evaluación para hacer su trabajo, pídale al Administrador que le habilite ese módulo desde **Administración → Usuarios** (Capítulo 11).

---

## Operaciones diarias

**¿Qué hago si registré mal una toma de medicamento?**

Los registros de medicamentos no pueden modificarse directamente una vez confirmados, por razones de trazabilidad clínica. Si cometió un error, comuníquese con el Administrador del sistema o con el médico responsable para que documente la corrección en una nota diaria del expediente del residente. En casos donde el error sea significativo clínicamente, notifique también al médico de referencia.

---

**¿El pase de asistencia se guarda automáticamente?**

No. Debe hacer clic en el botón **Guardar pase** o **Actualizar pase** para que los cambios queden guardados. Si cierra la pestaña del navegador sin guardar, perderá todos los cambios realizados durante esa sesión. Acostúmbrese a guardar después de cada cambio importante.

---

**¿Puedo registrar el pase de asistencia de días anteriores?**

Sí. En el módulo de Asistencia, cambie la fecha al día anterior usando el selector de fecha. Podrá ingresar o modificar el registro de ese día. Esto es útil si el pase de un turno anterior quedó incompleto por alguna razón.

---

**¿Por qué aparece una fila en rojo en el pase de asistencia?**

Una fila roja significa que el residente está marcado con el estado **Ausente sin permiso**. Esto es una alerta de seguridad: el residente no está en el Hogar y no tiene una autorización de salida registrada. Siga el protocolo descrito en el Capítulo 6: guarde el pase, notifique al director, contacte al familiar y registre un incidente en la entrega de turno.

---

**¿Qué significa el símbolo ⚠ en rojo junto a la hora de un medicamento?**

Significa que ya pasó la hora pautada para ese medicamento y aún no ha sido registrado. El sistema lo marca como "vencido". Debe registrar ese medicamento de inmediato con el estado que corresponda (Administrado, Rechazado u Omitido) y anotar en el campo de Motivo o Notas la razón del retraso.

---

## Finanzas

**¿Qué pasa si genero los cobros dos veces en el mismo mes?**

Se duplicarán los cobros para todos los residentes, lo que causará que sus saldos aparezcan incorrectos (el doble de lo que deberían). Si esto ocurre, comuníquese de inmediato con el administrador técnico del sistema para que corrija los registros duplicados. Para evitarlo, genere los cobros **una sola vez por mes**, idealmente el primer día hábil.

---

**¿Cómo registro un pago recibido por SINPE Móvil?**

1. Abra la cuenta del residente desde el módulo de Finanzas.
2. Haga clic en **+ Registrar pago**.
3. En el campo **Método de pago**, seleccione **SINPE Móvil**.
4. En el campo **Referencia**, escriba el número de confirmación que aparece en el mensaje de texto del SINPE (ej. "123456789").
5. Complete los demás campos y haga clic en **Guardar pago**.

Guardar el número de confirmación es importante para poder verificar el pago en caso de discrepancias futuras.

---

**¿Por qué el saldo de un residente aparece en negativo?**

Un saldo negativo significa que el residente (o su familia) pagó **más de lo que se le ha cobrado**. Es decir, tiene un crédito a favor. Esto puede ocurrir si se hicieron pagos anticipados o si hubo un cambio en el acuerdo de pago. No es un error — simplemente significa que hay un saldo a favor que se aplicará a cobros futuros.

---

## Errores técnicos comunes

**La pantalla se queda en blanco o muestra solo el símbolo de carga sin avanzar.**

Esto generalmente ocurre por una conexión a internet inestable o una interrupción del servicio. Intente lo siguiente:
1. Presione **F5** o el botón de actualizar del navegador.
2. Verifique que su dispositivo tenga conexión a internet.
3. Si el problema persiste más de 5 minutos, comuníquese con soporte técnico.

---

**El sistema muestra el mensaje "Error al cargar".**

Este mensaje indica que el sistema no pudo recuperar los datos del servidor en ese momento. Generalmente es temporal:
1. Espere 30 segundos y presione **F5** para intentar de nuevo.
2. Si el error persiste durante varios minutos, comuníquese con soporte técnico e indique qué sección estaba intentando usar.

---

**Guardé la información pero no aparece en la pantalla.**

Esto puede ocurrir cuando la pantalla no se actualiza automáticamente después de guardar. Pruebe:
1. Presione **F5** para recargar la página.
2. Si la información guardada tampoco aparece después de recargar, comuníquese con soporte técnico.

---

**El formulario no me deja guardar y no entiendo por qué.**

Los formularios del sistema tienen campos obligatorios (marcados con \*). Si alguno está vacío, el sistema no permitirá guardar y resaltará los campos que necesitan completarse en rojo. Revise todos los campos del formulario, especialmente los que están al final de la página.

---

## ¿Necesita más ayuda?

Si tiene una duda que no está cubierta en este manual, o si encuentra un problema que no puede resolver con las instrucciones de esta sección, comuníquese con el equipo de soporte técnico:

| | |
|---|---|
| **Correo de soporte** | `[correo de soporte técnico]` |
| **Teléfono / WhatsApp** | `[número de soporte técnico]` |
| **Horario de atención** | `[horario de atención del soporte]` |

Al contactar a soporte, tenga lista la siguiente información para agilizar la atención:
- Su nombre y rol en el sistema.
- Descripción de lo que estaba intentando hacer.
- El mensaje de error exacto que vio (si aplica).
- La fecha y hora aproximada en que ocurrió el problema.
