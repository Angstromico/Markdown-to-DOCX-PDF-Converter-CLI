

RFC: Oficina Móvil
## Introducción
Oficina Móvil es una aplicación híbrida desarrollada con Angular 17, Ionic 8 y Capacitor 7
que permite a los clientes de Fibex Telecom gestionar pagos, facturación, servicios, tickets y
notificaciones desde dispositivos móviles (Android e iOS). La app interactúa con múltiples
APIs (JSON, TLS y Gateway) para autenticación, gestión de cuentas, procesamiento de
pagos y consulta de servicios.

Este RFC documenta los cambios realizados en la rama feature/password-change,
cuyo objetivo es agregar la funcionalidad de cambio de contraseña para el servicio
FibexPlay directamente desde la aplicación móvil.

Cambio: Implementación del Flujo de Cambio de
Contraseña FibexPlay

## Campo Valor
Estado Pendiente — Esperando endpoint de backend
## Rama
Feature/MM/password-change-fibexplay
## Autor Manuel Morales
## Fecha 2026-04-06
App Oficina Móvil (Oficina_Movil_V2) v3.3.1


- Resumen de Cambios
1.1 Commit: feat: add frontend UI for change
password flow (no backend integration yet)
Archivos modificados:
● src/app/services/user.service.ts

● src/app/pages/fibexplay/fibexplay-password/fibexplay-
password.page.ts
● src/app/pages/fibexplay/fibexplay-password/fibexplay-
password.page.html

## Detalle:
a) user.service.ts — Nuevo método changeFibexPlayPassword()
Se añadió el método changeFibexPlayPassword(data: { currentPassword,
newPassword }) al servicio de usuario. Este método:

● Realiza validación mock de la contraseña actual contra clave_fibexplay del usuario.
● Simula un delay de API de 1.5s.
● Retorna { success: boolean, message: string }.
● Incluye comentada la implementación de producción lista para conectar con el endpoint
real:POST ${environment.url_backend}/api/fibexplay/change-password
● Se añadió además el helper privado AuthUser() para centralizar la construcción del
header de autorización.

Nota: La implementación actual es mock. Se requiere el endpoint de backend para la
integración real.

b) fibexplay-password.page.ts — Lógica del componente
Se añadieron las siguientes propiedades y métodos al componente:

## Propiedades:
● showChangePassword — Controla la visibilidad del formulario de cambio.
● newPassword / confirmPassword — Campos del formulario.
● isChangingPassword — Estado de carga durante la operación.
● passwordErrors — Objeto para mensajes de error por campo y general.
● showNewPassword / showConfirmPassword — Toggle de visibilidad de campos.

## Métodos:
● isPasswordValid() — Valida: mínimo 8 caracteres, coincidencia de contraseñas, y
presencia de mayúsculas, minúsculas, números y caracteres especiales.

● changePassword() — Ejecuta el cambio llamando al servicio, actualiza el modelo
local y muestra toast de éxito o error.
● cancelPasswordChange() — Resetea el formulario y oculta la vista de cambio.
● maskPassword() — Enmascara la contraseña con asteriscos.
● togglePasswordVisibility() / getPasswordInputType() /
getEyeIconName() — Helpers para el toggle de visibilidad de los campos de
contraseña.
● createMockUser() — Genera datos mock del usuario para testing (se usa cuando no
hay usuario disponible en el servicio).

Modificaciones existentes:
● copyToClipboard() — Se refactorizó para obtener el texto a copiar directamente del
modelo (user.usuario_fibexplay / user.clave_fibexplay) en lugar de leer
del DOM, mejorando la confiabilidad.
● ngOnInit() — Se añadió fallback a mock user cuando no se dispone de datos reales,
para facilitar pruebas en desarrollo.

c) fibexplay-password.page.html — Interfaz de usuario
Se añadió al template existente:

● Formulario de cambio de contraseña con:
○ Campo "Nueva Contraseña" con toggle de visibilidad (icono de ojo).
○ Campo "Confirmar Contraseña" con toggle de visibilidad.
○ Mensajes de error inline por campo y mensaje general.
○ Botones "Cancelar" y "Cambiar Contraseña" (este último con spinner de carga).
● Botón "Cambiar Contraseña" principal que despliega el formulario (visible cuando
showChangePassword es falso).
● El formulario y los botones respetan el estado isChangingPassword para
deshabilitarse durante la operación.



## Detalle:
Se creó un suite de pruebas unitarias completo que cubre:


## Categoría Casos
Inicialización Valores por defecto, suscripción al user service, creación de
mock user, loading en update, unsubscribe en destroy
Validación de
contraseña
Longitud mínima, coincidencia, mayúsculas, minúsculas,
números, caracteres especiales, password válido, limpieza de
errores previos
Cambio de contraseña Bloqueo si validación falla, payload correcto, estado de carga,
éxito con actualización de modelo y toast, error con mensaje del
backend, error genérico, error con mensaje personalizado
Interacción UI Cancelar y resetear formulario, enmascaramiento de contraseña,
toggle de visibilidad (nueva y confirmar), tipos de input, iconos
de ojo
Navegación por
plataforma
iOS → fibexplay.tv, Android → Google Play
Portapapeles Copiar username, copiar password, manejo de error
Estado del formulario Botón habilitado/deshabilitado según validez y carga, errores
visibles en template
Casos borde Contraseñas vacías, usuario null, clave_fibexplay null, reset
post-éxito


- Dependencias y Bloqueantes
2.1 Endpoint de backend no disponible
El bloqueante principal para completar esta funcionalidad es la falta del endpoint real para
el cambio de contraseña. Se indicó que el endpoint ya estaría listo, pero no se ha
proporcionado la URL definitiva ni la documentación del contrato de request/response.

Implementación mock actual:

POST ${environment.url_backend}/api/fibexplay/change-password



Implementación de producción (comentada en el código):

const response = await this.crud.PostFetch<
{ success: boolean; message: string },
{ currentPassword: string; newPassword: string },
any
## >(
## `${environment.url_backend}/api/fibexplay/change-password`,
data,
header
## );
return response.data;




## 3. Próximos Pasos
- Recibir endpoint de backend — Confirmar URL, método HTTP, contrato de
request/response y autenticación requerida.
- Descomentar implementación de producción en user.service.ts y eliminar el
mock.
- Eliminar mock user (createMockUser()) y el fallback en ngOnInit() una vez se
confirme que el flujo real funciona.
- Crear Pull Request hacia la rama principal (develop o main según el flujo del equipo).



- Notas para Futuros Contribuidores
Este RFC sigue un formato reutilizable. Si deseas documentar cambios en una rama de
características, copia esta estructura y adapta las secciones según corresponda:

- Encabezado con estado, rama, autor, fecha y app.
- Introducción breve del contexto.

- Resumen de cambios organizado por commit, con archivos modificados y detalle de cada
cambio.
- Dependencias y bloqueantes que impiden la integración completa.
- Próximos pasos para completar la funcionalidad.
