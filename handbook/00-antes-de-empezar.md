# Capítulo 0: Antes de Empezar

> Este capítulo le explica los conceptos fundamentales del sistema para que, cuando llegue a los capítulos prácticos, ya conozca el vocabulario y entienda cómo está organizado el Expediente Clínico ZOE.

---

## ¿Qué es el Expediente Clínico ZOE?

El Expediente Clínico ZOE es un programa de computadora diseñado específicamente para el Hogar Zoé. Su función principal es reemplazar los expedientes en papel: toda la información de los residentes — desde su ficha de ingreso hasta sus registros de medicamentos — se guarda de forma segura en el sistema.

Gracias al sistema, el personal puede:

- Consultar el expediente de cualquier residente desde cualquier computadora con acceso al sistema.
- Registrar las actividades diarias (medicamentos, asistencia, turno) sin necesidad de formularios físicos.
- Ver el estado del Hogar de un vistazo en el panel principal.
- Generar reportes para uso interno o para entidades como el IAFA.

---

## ¿Qué necesita para usar el sistema?

Antes de comenzar, asegúrese de tener lo siguiente:

1. **Una computadora, tableta o teléfono inteligente** con acceso a internet.
2. **Google Chrome o Microsoft Edge** instalado como navegador. Estos son los navegadores recomendados para un funcionamiento óptimo.
3. **Sus credenciales de acceso:** un correo electrónico y una contraseña, que le habrá asignado el administrador del sistema.

> **Nota:** Si no tiene sus credenciales, comuníquese con la persona encargada de administrar el sistema antes de continuar.

---

## Glosario: términos del sistema

A continuación encontrará los términos que el sistema usa con más frecuencia y lo que significan en la práctica diaria del Hogar.

| Término en el sistema | Qué significa en la práctica |
|---|---|
| **Residente** | Persona ingresada al Hogar Zoé para recibir tratamiento de rehabilitación. |
| **Admisión** | Un episodio de ingreso. Un residente puede tener varias admisiones a lo largo del tiempo (por ejemplo, si reingresa después de un egreso). |
| **Expediente** | El conjunto completo de documentos y registros que corresponden a una admisión específica. |
| **Panel principal** *(Dashboard)* | La primera pantalla que aparece al entrar al sistema. Muestra un resumen estadístico del estado del Hogar. |
| **Estado de admisión** | La etapa del proceso en que se encuentra un residente en este momento (por ejemplo: "En evaluación" o "Tratamiento activo"). |
| **Franja horaria** | El horario en que se deben administrar los medicamentos (por ejemplo: medicamentos de la mañana, del mediodía, de la noche). |
| **Turno** | El período de trabajo del personal: Mañana, Tarde o Noche. |
| **Rol** | El nivel de acceso asignado a cada usuario del sistema. Define qué puede ver y hacer cada persona. |
| **Archivar** | Desactivar un registro sin borrarlo permanentemente. Un residente archivado ya no aparece en la lista principal, pero su información se conserva y se puede recuperar. |
| **Lista de espera** | Registro de personas que solicitan ingreso al Hogar pero aún no tienen un cupo disponible. |
| **Morosidad / Saldo por cobrar** | El total de cobros pendientes de pago de los residentes activos. |

---

## Los estados de una admisión

Cada admisión avanza por una serie de etapas desde que el residente llega hasta que egresa. El sistema refleja en qué etapa se encuentra en todo momento.

```
Pendiente de ingreso
       ↓
Consentimientos pendientes
       ↓
Evaluación en progreso
       ↓
Tratamiento activo
       ↓
  Egresado  ←→  Abandono
```

**¿Qué significa cada estado?**

- **Pendiente de ingreso:** La admisión fue registrada en el sistema, pero el proceso de recepción aún no ha comenzado.
- **Consentimientos pendientes:** El residente está en proceso de firmar los documentos de consentimiento informado.
- **Evaluación en progreso:** El equipo clínico está completando las evaluaciones iniciales (médica, psicológica, social, etc.).
- **Tratamiento activo:** El residente está participando activamente en el programa de rehabilitación. Esta es la etapa de mayor duración.
- **Egresado:** El residente completó el programa y fue dado de alta de manera formal.
- **Abandono:** El residente dejó el programa antes de completarlo.

> **Nota:** El estado de la admisión lo actualiza el personal autorizado conforme avanza el proceso. No cambia automáticamente.

---

## Roles y módulos: dos conceptos distintos

Cada persona que usa el sistema tiene asignado un **rol** y una lista de **módulos habilitados**. Son cosas distintas:

- El **rol** es una etiqueta que describe qué es esa persona (Médico, Psicólogo, Consejero, etc.). Se usa para identificarla en reportes y expedientes.
- Los **módulos habilitados** son las secciones del sistema a las que esa persona puede entrar. Los define el Administrador para cada usuario individualmente, con casillas de verificación (ver Capítulo 11).

| Rol | Quién suele tenerlo |
|---|---|
| **Administrador** | Dueños o directores del Hogar |
| **Recepcionista** | Personal de recepción o administración |
| **Consejero** | Consejeros y coordinadores clínicos |
| **Médico** | Médico del centro o de referencia |
| **Trabajador Social** | Trabajador(a) social |
| **Psicólogo** | Psicólogo(a) |
| **Terapeuta Ocupacional** | Terapeuta ocupacional |

La única excepción es el **Administrador**: este rol siempre tiene acceso a **todas** las secciones del sistema, incluyendo Administración, Finanzas y todas las evaluaciones clínicas — sin necesidad de marcar módulos, y sin poder restringirse.

> **Solo para administradores:** Este manual está escrito principalmente para el rol de **Administrador**, que tiene acceso a todas las funciones descritas. Algunos capítulos (como Finanzas y Administración) dependen de qué módulos tenga habilitados cada persona.

---

## ¿Quién puede ver qué?

El acceso a cada sección depende de los **módulos habilitados** de cada usuario, que el Administrador configura individualmente (Capítulo 11):

- Las secciones de **Finanzas** solo las ven quienes tengan el módulo Finanzas habilitado (típicamente Administrador y Recepcionista, pero esto se define persona por persona).
- La sección de **Administración** (gestión de usuarios y profesionales) solo la ve el Administrador — no es configurable.
- Las evaluaciones clínicas del expediente (médica, psicológica, terapéutica, trabajo social, terapia ocupacional) tienen cada una su propio módulo; solo las ve quien tenga ese módulo habilitado.
- Las funciones de **operación diaria** (medicamentos, asistencia, ocupación, turno) y **Residentes** también son módulos que el Administrador debe habilitar para cada persona — no están abiertas por defecto.
- El **Panel principal** (Dashboard) y **Mi Perfil** están siempre disponibles para cualquier usuario con una cuenta activa.

---

## En resumen

- El sistema reemplaza los expedientes en papel del Hogar Zoé.
- Necesita internet, Chrome o Edge, y sus credenciales de acceso para usarlo.
- Un **residente** puede tener varias **admisiones**; cada admisión tiene su propio **expediente**.
- Las admisiones avanzan por etapas: desde "Pendiente de ingreso" hasta "Egresado" o "Abandono".
- Cada usuario tiene un **rol** (etiqueta descriptiva) y **módulos habilitados** (lo que realmente determina qué puede ver y hacer). El Administrador siempre tiene acceso a todo.
