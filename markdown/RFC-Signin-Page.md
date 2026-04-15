# RFC: Signin Page - Authentication Flow

## Introducción

La **Signin Page** es el componente central de autenticación de la aplicación **Oficina Móvil V2** que gestiona el flujo completo de inicio de sesión para clientes de **Fibex Telecom**. Esta página implementa un sistema multi-step basado en Swiper.js que guía al usuario a través de diferentes etapas: identificación, sincronización de datos, autenticación, registro de nuevos usuarios y agendamiento de servicios.

Este RFC documenta la arquitectura técnica, flujo de usuario, estados de navegación y consideraciones de implementación de la página de signin, que sirve como puerta de entrada principal al ecosistema de servicios de Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/signin.png" alt="Signin Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | SigninPage (src/app/pages/signin/)       |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-12                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/signin/
    signin.page.ts          # Componente principal con lógica de autenticación
    signin.page.html        # Template con 8 slides de flujo
    signin.page.scss        # Estilos específicos del componente
    signin.page.spec.ts     # Pruebas unitarias
    signin-routing.module.ts # Configuración de rutas
    signin.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Swiper.js v9.4.1**
- **Propósito:** Navegación multi-step entre diferentes estados del flujo
- **Configuración:** `slides-per-view="1"`, `autoplay="true"`, `allowTouchMove="false"`
- **Integración:** Mediante `<swiper-container>` con 8 slides distintos
- **Documentación:** [Swiper.js Documentation](https://swiperjs.com/)

#### **Angular Forms**
- **ReactiveFormsModule:** Para gestión de formularios reactivos
- **FormsModule:** Para formularios template-driven
- **Validaciones:** Validators para cédula y contraseña
- **Documentación:** [Angular Forms Documentation](https://angular.dev/guide/forms)

#### **Ionic Framework**
- **ModalController:** Para modales de autenticación biométrica
- **Platform Detection:** Detección de plataforma iOS/Android
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura Multi-Step

La página implementa 8 slides distintos que manejan diferentes estados del flujo de autenticación:

#### **Slide 0: Identificación Inicial**
- **Componente:** `app-dni-form`
- **Propósito:** Capturar cédula y nacionalidad del usuario
- **Eventos:** 
  - `passwordRegistered` - Usuario ya tiene contraseña
  - `passwordRequired` - Usuario requiere registrar contraseña
  - `syncronizing` - Sincronización de datos necesaria
  - `unregistered` - Usuario no registrado
  - `prelogin` - Usuario con agendamiento previo

#### **Slide 1: Sincronización**
- **Estado:** `syncronizing = true`
- **Componente:** `app-loading-cubes`
- **Propósito:** Mostrar progreso durante sincronización de datos
- **Lógica:** Espera evento `account-synscronized` via NucleoService

#### **Slide 2: Autenticación**
- **Estado Dual:** `typePassword` boolean
- **Componentes:** 
  - `app-password-form` (si `typePassword = true`)
  - `app-credential-contact-form` (si `typePassword = false`)
- **Propósito:** Validar credenciales del usuario

#### **Slide 3: Welcome Kit**
- **Estado:** `isUnregistered` o `isWelcomeKit`
- **Componente:** `app-welcome-kit-swiper`
- **Propósito:** Presentar beneficios a usuarios no registrados

#### **Slide 4: Formulario Agendamiento**
- **Estado:** `isUnregistered`
- **Componente:** `app-agenda-form`
- **Propósito:** Capturar datos de contacto para agendamiento

#### **Slide 5: Calendario Agendamiento**
- **Estado:** `isUnregistered`
- **Componente:** `app-calendar-agenda`
- **Propósito:** Seleccionar fecha y hora para agendamiento

#### **Slide 6: Seguridad**
- **Componente:** `app-set-password`
- **Propósito:** Configurar seguridad adicional de la cuenta

#### **Slide 7: Pre-Login**
- **Estado:** `user.isSchedulingPreLogged`
- **Componente:** `app-pre-login-swiper`
- **Propósito:** Flujo especial para usuarios con agendamiento previo

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
@ViewChild('swiper') swiper?: ElementRef<{ swiper: Swiper }>;

// Formularios reactivos
public formGroupCedula = new FormGroup({
  nacionalidad: new FormControl('V', [Validators.required]),
  cedula: new FormControl('', [Validators.minLength(6), Validators.maxLength(9), Validators.required]),
});

public formGroupClave = new FormGroup({
  password: new FormControl('', [Validators.required, Validators.minLength(6), Validators.maxLength(20)]),
});

// Estados de navegación
public typePassword: boolean = false;
public syncronizing: boolean = false;
public isUnregistered: boolean = false;
public isWelcomeKit: boolean = false;
public hasAgendamiento: boolean = false;
public canPay: boolean = false;
public isLoading: boolean = false;
public isFirstTime: boolean = false;
```

#### **Control de Swiper**
```typescript
public ngAfterViewInit() {
  if (this.swiper) {
    this.swiper.nativeElement.swiper.allowTouchMove = false; // Deshabilita touch
    this.swiper.nativeElement.swiper.update();
  }
}

public ngOnDestroy() {
  this.swiper?.nativeElement.swiper?.destroy();
  this.$userSchedulingSub?.unsubscribe();
}
```

### 3.2 Manejo de Eventos

#### **Eventos de Autenticación**
```typescript
public onPasswordRegistered(ev: { cedula: string; nacionalidad: string }) {
  this.cedula = ev.cedula;
  this.nacionalidad = ev.nacionalidad;
  this.typePassword = true;
  this.swiper?.nativeElement.swiper.slideTo(2);
}

public onSyncronizing(ev: { cedula: string; nacionalidad: string }) {
  this.cedula = ev.cedula;
  this.nacionalidad = ev.nacionalidad;
  this.syncronizing = true;
  this.swiper?.nativeElement.swiper.slideTo(1);
  
  // Suscripción a eventos de sincronización
  const subscription = this.nucleo.subscribe('syncronize:' + ev.cedula);
  this.nucleo.on('account-synscronized', dni => {
    if (dni === 'syncronize:' + ev.cedula) {
      subscription.unsubscribe();
      this.swiper?.nativeElement.swiper.slideTo(2);
      setTimeout(() => { this.syncronizing = false; }, 700);
    }
  });
}
```

#### **Gestión de Agendamiento**
```typescript
public sendAppointment(ev: { date: string; time_hour: string }) {
  this.isLoading = true;
  
  this.user.SendAgendamiento(this.sendToAgenda)
    .then(res => {
      if (res && Array.isArray(res) && res.length > 0) {
        this.user.userScheduling = res[0];
        this.user.isSchedulingPreLogged = true;
        this.isFirstTime = true;
        this.swiper?.nativeElement.swiper.slideTo(7);
      }
    })
    .finally(() => { this.isLoading = false; });
}
```

---

## 4. Componentes Compartidos Integrados

### 4.1 Componentes de Swiper

#### **DniFormComponent**
- **Ruta:** `src/app/shared/components/swiper/dni-form/dni-form.component`
- **Propósito:** Captura y validación de cédula venezolana
- **Validaciones:** Nacionalidad (V/E) y cédula (6-9 dígitos)

#### **PasswordFormComponent**
- **Ruta:** `src/app/shared/components/swiper/password-form/password-form.component`
- **Propósito:** Formulario de contraseña con opciones de recuperación
- **Features:** Toggle visibilidad, enlace a recuperación, auth biométrica

#### **CredentialContactFormComponent**
- **Ruta:** `src/app/shared/components/swiper/credential-contact-form/credential-contact-form.component`
- **Propósito:** Captura de datos de contacto para usuarios nuevos

### 4.2 Componentes de Agendamiento

#### **WelcomeKitSwiperComponent**
- **Ruta:** `src/app/shared/components/swiper/welcome-kit-swiper/welcome-kit-swiper.component`
- **Propósito:** Presentación de beneficios y servicios

#### **CalendarAgendaComponent**
- **Ruta:** `src/app/shared/components/swiper/calendar-agenda/calendar-agenda.component`
- **Propósito:** Selección de fechas disponibles para agendamiento

---

## 5. Integración con Servicios

### 5.1 Servicios Principales

#### **UserService**
- **Propósito:** Gestión de datos de usuario y agendamiento
- **Métodos clave:** `SendAgendamiento()`, `userScheduling`
- **Estados:** `isSchedulingPreLogged`, `userScheduling`

#### **NucleoService**
- **Propósito:** Comunicación en tiempo real para sincronización
- **Eventos:** `account-synscronized`, `syncronize:${cedula}`
- **Patrón:** Pub/Sub para sincronización asíncrona

#### **OneSignalService**
- **Propósito:** Notificaciones push y puente nativo
- **Métodos:** `isBridgeAvailable()`, `testBridge()`
- **Integración:** Verificación de disponibilidad al iniciar

#### **DialogsService**
- **Propósito:** Gestión de modales informativos
- **Uso:** Confirmación de agendamiento, mensajes de error

### 5.2 UtilService Integration

```typescript
public goToDashboard() {
  this.isLoading = true;
  this.util.navigateToPage('/tabs/home', { replaceUrl: true });
  this.swiper?.nativeElement.swiper.slideTo(0);
  this.formGroupCedula.reset();
  this.formGroupClave.reset();
}

public onPasswordForgot() {
  const cedulaField: string = this.cedula.trim();
  if (cedulaField) {
    this.util.navigateToPage('/verification', {
      queryParams: { cedula: cedulaField, nacionalidad: this.nacionalidad }
    });
  } else {
    this.util.navigateToPage('/recover-password');
  }
}
```

---

## 6. Estilos y Diseño Visual

### 6.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.loading-sync-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem;
  margin-top: 4rem;
}

swiper-slide {
  &::-webkit-scrollbar { display: none; }
  scrollbar-width: none;
  -ms-overflow-style: none;
}
```

#### **Diseño Responsivo**
- **Layout Fullscreen:** `[fullscreen]="true"` en ion-content
- **Background Transparent:** `bg-transparent` para integración visual
- **Logo Positioning:** Posicionamiento fijo del logo Fibex

### 6.2 Optimizaciones de UI

- **Ocultar Scrollbars:** Mejora visual en slides
- **Loading States:** Indicadores visuales durante operaciones asíncronas
- **Platform Detection:** Adaptación específica para iOS

---

## 7. Flujo de Autenticación Detallado

### 7.1 Caminos Principales

#### **Usuario Registrado**
1. Slide 0: Ingresar cédula
2. Slide 1: Sincronización (si aplica)
3. Slide 2: Ingresar contraseña
4. Slide 6: Configurar seguridad (opcional)
5. Dashboard

#### **Usuario No Registrado**
1. Slide 0: Ingresar cédula
2. Slide 3: Welcome Kit
3. Slide 4: Formulario de contacto
4. Slide 5: Agendamiento
5. Slide 7: Pre-login con agendamiento

#### **Usuario con Agendamiento Previo**
1. Slide 0: Detección automática
2. Slide 7: Flujo pre-login directo

### 7.2 Estados de Error y Recuperación

- **Contraseña Olvidada:** Navegación a `/verification` o `/recover-password`
- **Sincronización Fallida:** Manejo de errores con modales informativos
- **Agendamiento Fallido:** Retroalimentación al usuario con opciones de reintentar

---

## 8. Consideraciones de Performance

### 8.1 Optimizaciones Implementadas

1. **Lazy Loading:** Componentes cargados bajo demanda
2. **Suscripción Controlada:** Cleanup de subscriptions en ngOnDestroy
3. **Swiper Optimization:** Deshabilitado touch movement para control programático
4. **Form Validation:** Validaciones reactivas eficientes

### 8.2 Manejo de Memoria

```typescript
public ngOnDestroy() {
  this.swiper?.nativeElement.swiper?.destroy();
  this.$userSchedulingSub?.unsubscribe();
}
```

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Flujo completo usuario registrado**
2. **Flujo completo usuario no registrado**
3. **Recuperación de contraseña**
4. **Sincronización de datos**
5. **Agendamiento de servicios**
6. **Autenticación biométrica**
7. **Manejo de errores de red**

### 9.2 Pruebas Unitarias Requeridas

- Validación de formularios
- Navegación entre slides
- Manejo de eventos asíncronos
- Integración con servicios
- Estados de carga y error

---

## 10. Consideraciones de Seguridad

### 10.1 Validaciones de Entrada

- **Cédula:** 6-9 dígitos, nacionalidad V/E
- **Contraseña:** 6-20 caracteres, requerida
- **Email:** Validación en formulario de contacto
- **Teléfono:** Formato venezolano estándar

### 10.2 Manejo de Datos Sensibles

- **Autenticación Biométrica:** Integración con `FingureLockPage`
- **Cifrado de Contraseñas:** Manejo seguro en tránsito
- **Sanitización de Inputs:** Prevención de XSS
- **Session Management:** Limpieza de datos al salir

---

## 11. Mejoras Futuras Sugeridas

### 11.1 Features Potenciales

1. **Biometric Authentication Advanced:** Face ID/Touch ID mejorado
2. **Multi-language Support:** Internacionalización completa
3. **Progressive Web App:** Mejoras offline
4. **Analytics Integration:** Tracking de conversión
5. **A/B Testing:** Diferentes flujos de onboarding

### 11.2 Optimizaciones Técnicas

1. **State Management:** Implementación con NgRx o Signals
2. **Error Boundaries:** Mejor manejo de errores
3. **Performance Monitoring:** Métricas de rendimiento
4. **Accessibility:** Mejoras WCAG compliance

---

## 12. Notas para Mantenimiento

### 12.1 Puntos Críticos

1. **Swiper Control:** Mantener control programático sobre navegación
2. **Subscription Management:** Proper cleanup para evitar memory leaks
3. **Form Validation:** Coordinación con backend validation rules
4. **Platform Differences:** Testing específico por plataforma

### 12.2 Buenas Prácticas

- Mantener estados desacoplados del UI
- Validar todos los inputs del usuario
- Implementar proper error handling
- Documentar cambios en el flujo de autenticación
- Realizar testing cross-platform

---

## 13. Conclusión

La Signin Page representa un componente crítico y complejo en la arquitectura de Oficina Móvil. Su implementación multi-step mediante Swiper.js permite manejar múltiples flujos de usuario de manera eficiente y escalable, desde usuarios existentes hasta nuevos clientes que requieren agendamiento de servicios.

La arquitectura modular, la integración con múltiples servicios y el manejo robusto de estados la convierten en un componente central que requiere especial atención durante el mantenimiento y evolución de la aplicación. Su diseño actual proporciona una base sólida para futuras mejoras y optimizaciones en la experiencia de autenticación.

---

*Documentación actualizada: 2026-04-12*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
