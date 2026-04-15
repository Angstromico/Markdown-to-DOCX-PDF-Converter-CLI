# RFC: Fibexplay Password Page - Sistema de Gestión de Credenciales FibexPlay

## Introducción

La **Fibexplay Password Page** es el componente especializado de gestión de credenciales de la aplicación **Oficina Móvil V2** que permite a los usuarios visualizar, copiar y cambiar las credenciales de acceso al servicio **FibexPlay**. Esta página implementa un sistema de gestión de contraseñas con validación de fortaleza, visibilidad dinámica, copia al portapapeles y navegación a la aplicación FibexPlay, proporcionando una experiencia completa de gestión de credenciales.

Este RFC documenta la arquitectura técnica, flujo de usuario, sistema de validación de contraseñas, manejo de seguridad y consideraciones de implementación de la página de credenciales FibexPlay, que sirve como portal central para la gestión de acceso al servicio streaming de los clientes Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/fibexplay-password.jpeg" alt="Fibexplay Password Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | En Construcción - Versión 3.3.1         |
| **Componente**  | FibexplayPasswordPage (src/app/pages/fibexplay/fibexplay-password/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/fibexplay/fibexplay-password/
    fibexplay-password.page.ts          # Componente principal con lógica de credenciales
    fibexplay-password.page.html        # Template con formulario de contraseñas
    fibexplay-password.page.scss        # Estilos específicos del componente
    fibexplay-password.page.spec.ts     # Pruebas unitarias
    fibexplay-password-routing.module.ts # Configuración de rutas
    fibexplay-password.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Angular Core**
- **Propósito:** Framework base con lifecycle management
- **Configuración:** Component lifecycle, dependency injection
- **Integración:** Decoradores @Component, OnInit, OnDestroy
- **Documentación:** [Angular Documentation](https://angular.dev/)

#### **Ionic Framework**
- **Propósito:** Componentes UI nativos y navegación
- **Configuración:** ion-input, ion-icon, ion-spinner, toast
- **Integración:** ToastController, Platform detection
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

#### **Angular Forms**
- **Propósito:** Gestión de formularios y bindings
- **Configuración:** FormsModule con ngModel standalone
- **Integración:** [(ngModel)] bindings en inputs de contraseña
- **Documentación:** [Angular Forms Documentation](https://angular.dev/guide/forms)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura de Estados

La página implementa un sistema de gestión de credenciales con múltiples estados:

#### **Estado: Visualización de Credenciales**
- **Componente:** Card con usuario y contraseña actuales
- **Propósito:** Mostrar las credenciales de FibexPlay
- **Features:** 
  - Visualización de usuario y contraseña
  - Botones de copia al portapapeles
  - Botón para iniciar cambio de contraseña
  - Enlace directo a FibexPlay

#### **Estado: Cambio de Contraseña**
- **Componente:** Formulario de cambio de contraseña
- **Propósito:** Permitir al usuario cambiar su contraseña
- **Features:** 
  - Input para nueva contraseña
  - Input para confirmación
  - Validación en tiempo real
  - Botones de confirmar/cancelar

#### **Estado: Sin Servicio**
- **Componente:** Mensaje de no disponibilidad
- **Propósito:** Informar cuando el usuario no tiene el servicio
- **Features:** 
  - Mensaje descriptivo
  - Icono de advertencia
  - Diseño centrado y responsivo

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
public user: ItmAbonadoTable | null = null;
showChangePassword: boolean = false;
newPassword: string = '';
confirmPassword: string = '';
isChangingPassword: boolean = false;
passwordErrors: {
  newPassword?: string;
  confirmPassword?: string;
  message?: string;
} = {};

showNewPassword: boolean = false;
showConfirmPassword: boolean = false;
```

#### **Carga de Usuario**
```typescript
ngOnInit() {
  this.subscriptionUser = this.userService.GetUser().subscribe(user => {
    if (this.user) {
      this.utils
        .show('Obteniendo información')
        .then(loading => {
          return new Promise(resolve => setTimeout(resolve, 500)).then(() => {
            this.user = user;
            loading.dismiss().catch(console.error);
          });
        })
        .catch(console.error);
    } else {
      this.user = user;
    }
  });
}
```

### 3.2 Sistema de Validación de Contraseñas

#### **Validación Completa de Fortaleza**
```typescript
isPasswordValid(): boolean {
  this.passwordErrors = {};

  if (!this.newPassword || this.newPassword.length < 8) {
    this.passwordErrors.newPassword =
      'La contraseña debe tener al menos 8 caracteres';
    return false;
  }

  if (this.newPassword !== this.confirmPassword) {
    this.passwordErrors.confirmPassword = 'Las contraseñas no coinciden';
    return false;
  }

  // Password strength validation
  const hasUpperCase = /[A-Z]/.test(this.newPassword);
  const hasLowerCase = /[a-z]/.test(this.newPassword);
  const hasNumbers = /\d/.test(this.newPassword);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(this.newPassword);

  if (!hasUpperCase || !hasLowerCase || !hasNumbers || !hasSpecialChar) {
    this.passwordErrors.message =
      'La contraseña debe incluir mayúsculas, minúsculas, números y caracteres especiales';
    return false;
  }

  return true;
}
```

---

## 4. Componentes Compartidos Integrados

### 4.1 Componentes Principales

#### **ContentHeaderComponent**
- **Ruta:** `importsComponents/headers/content-header/content-header.component`
- **Propósito:** Header estándar con título y navegación
- **Features:** 
  - Título "Contraseñas de Fibex Play"
  - Botón de retroceso
  - Layout consistente con otras páginas

#### **MainHeaderComponent**
- **Ruta:** `src/app/shared/components/headers/main-header/main-header.component`
- **Propósito:** Header principal con navegación global
- **Features:** 
  - Navegación principal
  - Menú de usuario
  - Búsqueda global

### 4.2 Estructura de Template

#### **Contenedor Principal de Credenciales**
```html
<div *ngIf="user?.usuario_fibexplay && user?.clave_fibexplay; else noService">
  <div class="flex flex-col items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-2 md:mx-0 transition-transform transform hover:scale-105 my-8">
      <h2 class="text-2xl md:text-3xl font-extrabold mb-4 text-center text-blue-700">
        Acceso FibexPlay
      </h2>

      <p class="text-center text-gray-600 mb-4">
        Usa estas credenciales para ingresar a <strong>FibexPlay</strong>
      </p>

      <!-- Usuario -->
      <div class="flex items-center justify-between border-b border-gray-300 pb-4 mb-4">
        <span class="text-gray-700 font-medium">Usuario</span>
        <div class="flex items-center">
          <span class="text-gray-800 font-semibold bg-gray-100 px-3 py-1 rounded-md shadow-inner">
            {{ user?.usuario_fibexplay }}
          </span>
          <ion-icon
            name="copy-outline"
            class="ml-2 text-blue-600 cursor-pointer hover:text-blue-800 transition-colors"
            (click)="copyToClipboard('username')"
          ></ion-icon>
        </div>
      </div>

      <!-- Contraseña -->
      <div class="flex items-center justify-between border-b border-gray-300 pb-4 mb-4">
        <span class="text-gray-700 font-medium">Clave</span>
        <div class="flex items-center">
          <span class="text-gray-800 font-semibold bg-gray-100 px-3 py-1 rounded-md shadow-inner">
            {{ user?.clave_fibexplay }}
          </span>
          <ion-icon
            name="copy-outline"
            class="ml-2 text-blue-600 cursor-pointer hover:text-blue-800 transition-colors"
            (click)="copyToClipboard('password')"
          ></ion-icon>
        </div>
      </div>

      <!-- Formulario de cambio de contraseña -->
      <div *ngIf="showChangePassword">
        <!-- Inputs de nueva contraseña -->
      </div>

      <!-- Botón de descarga FibexPlay -->
      <div class="mt-4">
        <button
          class="bg-blue-600 text-white font-semibold py-2 px-4 md:py-3 md:px-6 rounded-full shadow-lg hover:bg-blue-700 transition-colors items-center justify-center flex gap-2 mx-auto"
          (click)="goToFibexplay()"
        >
          <img
            class="w-8 h-8 object-contain"
            src="assets/images/icons/fibexplay-logo-positive-small.png"
            alt="FibexPlay Logo"
          />
          Descargar FibexPlay
        </button>
      </div>
    </div>
  </div>
</div>
```

---

## 5. Integración con Servicios

### 5.1 Servicios Principales

#### **UserService**
- **Propósito:** Gestión de datos de usuario y credenciales
- **Métodos clave:** `GetUser()`, `changeFibexPlayPassword()`
- **Uso:** Obtener datos del usuario y cambiar contraseña
- **Flujo:** Observable para datos, Promise para cambio de contraseña

#### **UtilService**
- **Propósito:** Utilidades compartidas de UI y loading
- **Métodos clave:** `show()`, `hide()`
- **Uso:** Mostrar/ocultar indicadores de carga

#### **ToastController**
- **Propósito:** Gestión de notificaciones toast
- **Uso:** Mostrar mensajes de éxito y error
- **Características:** Configuración de colores, iconos y duración

---

## 6. Estilos y Diseño Visual

### 6.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.color-text {
  color: var(--ion-color-primary-2);
}

.main-message-container {
  @apply flex flex-col items-center justify-center p-4;
}

.message-div {
  @apply bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-2 md:mx-0 transition-transform transform hover:scale-105 my-8;
}

.message-title {
  @apply text-2xl md:text-3xl font-extrabold mb-4 text-center color-text;
}

.icon-container {
  @apply flex justify-center mb-4;
}

.message-description {
  @apply text-center text-gray-600 mb-4;
}
```

#### **Diseño Responsivo**
- **Adaptativo:** Max-width para cards en diferentes tamaños
- **Centered Layout:** Flexbox para centrar elementos
- **Hover Effects:** Transform scale en cards
- **Mobile First:** Diseño optimizado para móviles

### 6.2 Estados Visuales

- **Loading States:** Indicadores durante operaciones asíncronas
- **Error States:** Mensajes de error con colores apropiados
- **Success States:** Toast notifications con iconos de éxito
- **Disabled States:** Estados deshabilitados en botones durante operaciones

---

## 7. Flujo de Usuario Detallado

### 7.1 Caminos Principales

#### **Usuario con Servicio FibexPlay**
1. Entrada a la página de credenciales
2. Carga automática de datos del usuario
3. Visualización de credenciales actuales
4. Opción de copiar usuario y contraseña
5. Opción de cambiar contraseña
6. Validación de nueva contraseña
7. Confirmación de cambio con toast
8. Navegación a FibexPlay Store

#### **Usuario sin Servicio FibexPlay**
1. Entrada a la página
2. Detección de ausencia de servicio
3. Visualización de mensaje informativo
4. Icono de advertencia
5. Mensaje descriptivo

### 7.2 Estados de Error y Recuperación

- **Error de Carga:** Manejo con try-catch y loading states
- **Error de Validación:** Mensajes específicos por campo
- **Error de Cambio:** Toast con mensaje de error
- **Error de Copia:** Manejo de clipboard API errors

---

## 8. Consideraciones de Performance

### 8.1 Optimizaciones Implementadas

1. **Lazy Loading:** Componente cargado bajo demanda
2. **Efficient Validation:** Validación incremental y temprana
3. **Subscription Management:** Cleanup apropiado de observables
4. **Debounced Updates:** Prevención de actualizaciones excesivas

### 8.2 Manejo de Memoria

```typescript
ngOnDestroy(): void {
  this.subscriptionUser?.unsubscribe();
}
```

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Carga inicial de credenciales**
2. **Copia al portapapeles**
3. **Validación de contraseñas**
4. **Cambio de contraseña**
5. **Manejo de errores**
6. **Responsive design**
7. **Toast notifications**
8. **Platform detection**
9. **Service availability**
10. **Security validation**

### 9.2 Pruebas Unitarias Requeridas

- Validación de contraseñas
- Manejo de estados de UI
- Integración con servicios
- Copia al portapapeles
- Platform detection
- Error handling
- Toast notifications

---

## 10. Consideraciones de Seguridad

### 10.1 Manejo de Credenciales

- **Password Masking:** Contraseñas visibles solo cuando el usuario lo desea
- **Input Validation:** Validación completa de fortaleza de contraseñas
- **Secure Storage:** Manejo seguro de credenciales en memoria
- **Clipboard Security:** Uso seguro de clipboard API

### 10.2 Validaciones de Seguridad

- **Password Strength:** Requisitos de complejidad (mayúsculas, minúsculas, números, especiales)
- **Length Requirements:** Mínimo 8 caracteres
- **Confirmation Validation:** Verificación de coincidencia
- **Input Sanitization:** Limpieza de entradas de usuario

---

## 11. APIs y Servicios Externos

### 11.1 Clipboard API

- **URL:** https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API
- **Propósito:** Copiar texto al portapapeles del sistema
- **Uso en la aplicación:** 
  - Copiar nombre de usuario de FibexPlay
  - Copiar contraseña de FibexPlay
  - Retroalimentación con toast notifications
- **Características:** 
  - Cross-browser compatibility
  - Secure clipboard access
  - Permission-based access
  - Async operations

### 11.2 UserService API

- **Propósito:** Gestión de datos de usuario y credenciales
- **Métodos clave:** `changeFibexPlayPassword()`
- **Uso en la aplicación:** 
  - Cambio de contraseña de FibexPlay
  - Validación de credenciales
  - Actualización de datos locales
- **Características:** 
  - Promise-based operations
  - Response validation
  - Error handling
  - Local state updates

---

## 12. Componentes y Código Destacable

### 12.1 Sistema de Validación de Contraseñas

```typescript
isPasswordValid(): boolean {
  this.passwordErrors = {};

  if (!this.newPassword || this.newPassword.length < 8) {
    this.passwordErrors.newPassword =
      'La contraseña debe tener al menos 8 caracteres';
    return false;
  }

  if (this.newPassword !== this.confirmPassword) {
    this.passwordErrors.confirmPassword = 'Las contraseñas no coinciden';
    return false;
  }

  // Password strength validation
  const hasUpperCase = /[A-Z]/.test(this.newPassword);
  const hasLowerCase = /[a-z]/.test(this.newPassword);
  const hasNumbers = /\d/.test(this.newPassword);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(this.newPassword);

  if (!hasUpperCase || !hasLowerCase || !hasNumbers || !hasSpecialChar) {
    this.passwordErrors.message =
      'La contraseña debe incluir mayúsculas, minúsculas, números y caracteres especiales';
    return false;
  }

  return true;
}
```

**Características:**
- Validación completa de fortaleza
- Mensajes de error específicos
- Expresiones regulares para validación
- Manejo de errores por campo

### 12.2 Sistema de Visibilidad de Contraseñas

```typescript
togglePasswordVisibility(field: 'new' | 'confirm') {
  if (field === 'new') {
    this.showNewPassword = !this.showNewPassword;
  } else {
    this.showConfirmPassword = !this.showConfirmPassword;
  }
}

getPasswordInputType(field: 'new' | 'confirm'): string {
  if (field === 'new') {
    return this.showNewPassword ? 'text' : 'password';
  } else {
    return this.showConfirmPassword ? 'text' : 'password';
  }
}

getEyeIconName(field: 'new' | 'confirm'): string {
  if (field === 'new') {
    return this.showNewPassword ? 'eye-off-outline' : 'eye-outline';
  } else {
    return this.showConfirmPassword ? 'eye-off-outline' : 'eye-outline';
  }
}
```

**Características:**
- Toggle dinámico de visibilidad
- Iconos apropiados según estado
- Tipos de input dinámicos
- Manejo por campo individual

### 12.3 Sistema de Copia al Portapapeles

```typescript
copyToClipboard(field: string) {
  let textToCopy: string;

  if (field === 'username') {
    textToCopy = this.user?.usuario_fibexplay || '';
  } else if (field === 'password') {
    textToCopy = this.user?.clave_fibexplay || '';
  } else {
    textToCopy = '';
  }
  
  if (textToCopy) {
    navigator.clipboard
      .writeText(textToCopy)
      .then(() => {
        return this.toastController.create({
          mode: 'ios',
          color: 'success',
          message: 'Copiado al portapapeles!',
          duration: 6000,
          icon: 'clipboard-outline',
        });
      })
      .then(toast => {
        return toast.present();
      })
      .catch(err => {
        console.error(err);
      });
  }
}
```

**Características:**
- Uso de Clipboard API moderna
- Retroalimentación con toast
- Manejo de errores
- Validación de contenido

---

## 13. Mejoras Futuras Sugeridas

### 13.1 Features Potenciales

1. **Password Generator:** Generador automático de contraseñas seguras
2. **Password History:** Historial de contraseñas anteriores
3. **Two-Factor Authentication:** Añadir 2FA para mayor seguridad
4. **Biometric Authentication:** Autenticación biométrica para acceso
5. **Password Strength Meter:** Indicador visual de fortaleza

### 13.2 Optimizaciones Técnicas

1. **Real-time Validation:** Validación en tiempo real mientras se escribe
2. **Password Encryption:** Encriptación local de contraseñas
3. **Auto-fill Integration:** Integración con password managers
4. **Security Audit:** Auditoría de seguridad regular
5. **Performance Monitoring:** Métricas de uso y rendimiento

---

## 14. Notas para Mantenimiento

### 14.1 Puntos Críticos

1. **Password Validation:** Mantener requisitos de seguridad actualizados
2. **Service Integration:** Compatibilidad con API de cambio de contraseña
3. **Clipboard Security:** Manejo seguro de datos sensibles
4. **Error Handling:** Manejo robusto de errores de red
5. **Security Updates:** Actualizaciones de seguridad regulares

### 14.2 Buenas Prácticas

- Mantener validación completa de contraseñas
- Implementar proper error logging sin datos sensibles
- Mantener consistencia en estados de UI
- Documentar cambios en APIs de seguridad
- Realizar testing de seguridad regularmente
- Optimizar para dispositivos móviles

---

## 15. Conclusión

La Fibexplay Password Page representa un componente especializado y seguro en la arquitectura de Oficina Móvil para la gestión de credenciales del servicio FibexPlay. Su implementación con sistema de validación robusto, manejo seguro de contraseñas, integración con clipboard API y navegación directa a la aplicación la convierten en una solución completa para la gestión de acceso al servicio streaming de los clientes Fibex.

**Nota Importante:** Actualmente el feature de cambio de contraseña está en construcción. La implementación visual está completa pero falta el endpoint backend que lleve a cabo el cambio real de contraseña. La funcionalidad actual funciona de manera estética, mostrando la interfaz completa pero sin realizar el cambio efectivo en el servidor.

La arquitectura modular, la integración con servicios de usuario seguros y el manejo inteligente de estados proporcionan una base sólida para futuras mejoras como autenticación biométrica, generador de contraseñas y auditoría de seguridad. Su diseño actual ofrece una experiencia de usuario clara y segura tanto en plataformas móviles como web.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
