# RFC: Home Page - Dashboard Principal

## Introducción

La **Home Page** es el dashboard principal de la aplicación **Oficina Móvil V2** que sirve como centro de control para clientes de **Fibex Telecom**. Esta página proporciona una vista consolidada del estado de la cuenta, balance financiero, servicios contratados, promociones y herramientas de gestión. Implementa una arquitectura modular basada en componentes especializados que presentan información crítica y facilitan la navegación a funcionalidades clave del sistema.

Este RFC documenta la implementación técnica, arquitectura de componentes, integración con servicios y flujo de datos del dashboard principal, que representa el punto central de interacción del usuario con el ecosistema de servicios de Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/dashboard.png" alt="Home Page Dashboard" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | HomePage (src/app/pages/home/)           |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-13                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/home/
    home.page.ts          # Componente principal con lógica de dashboard
    home.page.html        # Template con estructura modular
    home.page.scss        # Estilos específicos del componente
    home.page.spec.ts     # Pruebas unitarias
    home-routing.module.ts # Configuración de rutas
    home.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Swiper.js v9.4.1**
- **Propósito:** Carrousel para banners promocionales y contenido dinámico
- **Configuración:** Autoplay con delay de 5000ms, loop infinito
- **Integración:** Mediante componentes BannersSwiperComponent
- **Documentación:** [Swiper.js Documentation](https://swiperjs.com/)

#### **ApexCharts v3.54.1**
- **Propósito:** Visualización de datos financieros y gráficos de consumo
- **Integración:** A través de ChartFullComponent para visualizaciones
- **Documentación:** [ApexCharts Documentation](https://apexcharts.com/docs/)

#### **Capacitor Browser**
- **Propósito:** Apertura de URLs externas en navegador nativo
- **Métodos:** `Browser.open()` con configuración de presentación
- **Documentación:** [Capacitor Browser Documentation](https://capacitorjs.com/docs/apis/browser)

#### **RxJS v7.8.0**
- **Propósito:** Gestión reactiva de suscripciones a servicios
- **Uso:** Subscriptions a UserService, contratos y datos del usuario
- **Documentación:** [RxJS Documentation](https://rxjs.dev/)

---

## 2. Arquitectura de Componentes

### 2.1 Componentes Principales Integrados

#### **BalanceSectionComponent**
- **Ruta:** `src/app/shared/components/balance-section/balance-section.component`
- **Propósito:** Visualización de balances en USD y Bs con conversión de tasa
- **Props:** `balanceUSD`, `balanceBs`, `showBalanceDetails`
- **Features:** Toggle de visibilidad, excepciones por ubicación

#### **CardLightThemeComponent**
- **Ruta:** `importsComponents/cards/card-light-theme/card-light-theme.component`
- **Propósito:** Tarjetas de acceso rápido para menú principal
- **Props:** `menu` con datos de navegación
- **Eventos:** `onItemSelected` para navegación

#### **BannersSwiperComponent**
- **Ruta:** `src/app/shared/components/swiper/banners-swiper/banners-swiper.component`
- **Propósito:** Carrousel de banners promocionales
- **Props:** `banners` array con datos de banners
- **Eventos:** `onBannerCLick` para manejo de clics

#### **TimeLineComponent**
- **Ruta:** `src/app/shared/components/time-line/time-line.component`
- **Propósito:** Línea temporal de estado de cuenta y fechas de corte
- **Eventos:** `upToDate`, `currentDay`, `daysLeftValue`
- **Features:** Indicadores visuales de estado de pago

#### **PaymentHistoryComponent**
- **Ruta:** `src/app/pages/payment-history/payment-history.component`
- **Propósito:** Historial de transacciones y pagos recientes
- **Integración:** Directamente en el dashboard principal

---

## 3. Gestión de Datos y Estado

### 3.1 Propiedades Principales

```typescript
// Datos del usuario y contrato
public user: ItmAbonadoTable | null = null;
public contrato: ItmContratoTable | null = null;
public currentBalance: number = 0;

// Configuración de Swiper
public slideOpts = {
  initialSlide: 1,
  speed: 400,
  slidesPerView: 1.2,
  spaceBetween: 10,
  centeredSlides: true,
  autoplay: { delay: 5000 }
};

// Menús y navegación
public firstMenuItems: (IMenu | undefined)[] = [];
public mainMenu: IMenu[] = [];
public allMenu: IMenu[] = [];

// Estado de UI
public isPageActive: boolean = true;
public showBalanceDetails: boolean = true;
public excepcionSaldo: boolean = false;
```

### 3.2 Gestión de Balance

```typescript
public get balanceBs(): number {
  const saldo = this.contrato ? this.contrato.saldo : 0;
  return this.tasaService.tasaDollar * saldo;
}

public get balanceUSD(): number {
  return this.contrato?.saldo || 0;
}
```

### 3.3 Suscripciones Reactivas

```typescript
async ionViewWillEnter() {
  this.subscriptionservice.subscribeall();
  
  this.subscriptionContrato = this.userService.GetContratoSelected()
    .subscribe(async contrato => {
      const isOtherContract = this.contrato?.id_contrato_adm !== contrato?.id_contrato_adm;
      this.contrato = contrato;
      
      if (contrato) {
        if (contrato.saldo <= 0.5 && contrato.saldo > 0) this.excepcionSaldo = true;
        this.showBalanceDetails = !contrato.nombre_ciudad.includes('MARGARITA');
      }
      
      Promise.all([this.userService.GetUserPromise(), this.tasaService.updateTasa()])
        .then(([user, _]) => { this.user = user; });
    });
}
```

---

## 4. Integración con Servicios

### 4.1 Servicios Principales

#### **UserService**
- **Propósito:** Gestión de datos de usuario y contratos
- **Métodos clave:** `GetContratoSelected()`, `GetUserPromise()`, `GetServicios()`
- **Integración:** Subscripción reactiva a cambios de contrato

#### **MenuService**
- **Propósito:** Gestión dinámica del menú de navegación
- **Métodos:** `GetMenuData()` para obtener pinned y main menu
- **Retorno:** Estructura con `pinnedMenu` y `mainMenu`

#### **BannerService**
- **Propósito:** Carga y gestión de banners promocionales
- **Métodos:** `GetBanners()` para obtener array de banners
- **Integración:** Actualización dinámica de contenido promocional

#### **TasaMonedaService**
- **Propósito:** Conversión de divisas y tasa de cambio
- **Métodos:** `updateTasa()` para actualizar tasa dólar/bolívar
- **Uso:** Cálculo de balance en moneda local

#### **NotificationService**
- **Propósito:** Gestión de notificaciones push
- **Integración:** OneSignal para notificaciones nativas
- **Plataformas:** iOS y Android (no web)

#### **MonitorService**
- **Propósito:** Monitoreo y analítica de uso
- **Métodos:** `UseMonitoreo('HOME')` para tracking

### 4.2 Servicios de Utilidad

#### **DialogsService**
- **Propósito:** Gestión de modales y popups informativos
- **Uso:** Popups promocionales, mensajes de confirmación

#### **LocalstorageService**
- **Propósito:** Almacenamiento local cifrado
- **Métodos:** `getEncrypt()` para datos sensibles
- **Uso:** Control de primera visita, preferencias

---

## 5. Flujo de Funcionalidades

### 5.1 Navegación Principal

```typescript
public onSendMoney() {
  this.util.navigateToPage('send-money');
}

public makePayments() {
  this.util.navigateToPage('payments');
}

public onAccount() {
  this.util.navigateToPage('/account');
}

public onNotification() {
  this.util.navigateToPage('notifications');
}
```

### 5.2 Manejo de Banners

```typescript
public onMainBannerClick = (bannerSelected: IBanner) => {
  try {
    if (bannerSelected.bannerType === 'url-internal') {
      this.util.navigateToPage(bannerSelected.redirectUrl);
    } else {
      window.open(bannerSelected.redirectUrl, '_blank');
    }
  } catch (error) {
    console.error(error);
  }
};
```

### 5.3 Sistema de Popups Promocionales

```typescript
async showPopup() {
  try {
    if (this.isShowingPopup || this.contrato?.estatus_contrato !== 'ACTIVO') {
      return;
    }
    
    this.isShowingPopup = true;
    const allServices = await this.userService.GetServicios();
    
    let popupPlan: { image: string } | undefined;
    const activeService = allServices.find(service => {
      const serviceKeyName = DECEMBER_PROMO_PLANS_LIST.find(plan =>
        service.nombre_servicio.includes(plan),
      );
      
      if (service.estatus !== 'ACTIVO' || !serviceKeyName) {
        return false;
      }
      
      const servicePopUpFound = POPUP_PLANS_LIST[serviceKeyName];
      if (servicePopUpFound) {
        popupPlan = servicePopUpFound;
      }
      return !!servicePopUpFound;
    });
    
    if (!popupPlan || !activeService?.tipo_servicio?.includes('HOGAR')) {
      return;
    }
    
    const promps: IModalInfoPromps = {
      imgSrc: popupPlan.image,
      showCloseBtn: true,
      cssClass: 'modal-info-size-xl-img',
      fullBackgroundImage: true,
    };
    
    this.dialogService.showStandardModalInfo(promps, () => {
      this.isShowingPopup = false;
    });
  } catch (error) {
    console.error('Error al obtener o mostrar el anuncio:', error);
  }
}
```

---

## 6. Optimizaciones y Performance

### 6.1 Cache Management

```typescript
private ensureCacheBusterParam(): void {
  const hasParam = this.route.snapshot.queryParamMap.has('cacheBuster');
  
  if (!hasParam) {
    const cacheBuster = Date.now();
    const currentUrl = this.router.url.split('?')[0];
    
    this.router.navigate([currentUrl], {
      queryParams: { cacheBuster },
      queryParamsHandling: 'merge',
    });
  }
}
```

### 6.2 Lazy Loading de Componentes

```typescript
private handleShowKit = () => {
  if (this.isFirstTimeView() && !this.isKitShowing) {
    this.isKitShowing = true;
    import('../welcome-kit/welcome-kit.component')
      .then(({ WelcomeKitComponent }) => {
        this.dialogService.showModal(WelcomeKitComponent, 'dialog', undefined, {
          enterAnimation: this.enterAnimationKitBienvenida,
          leaveAnimation: this.leaveAnimationKitBienvenida,
          cssClass: 'welcome-kit-modal',
        });
      });
  }
};
```

### 6.3 Animaciones Personalizadas

```typescript
private enterAnimationKitBienvenida = (baseEl: any) => {
  const root = baseEl.shadowRoot;
  const backdropAnimation = createAnimation()
    .addElement(root.querySelector('ion-backdrop'))
    .fromTo('opacity', '0', '0.4');
  
  const wrapperAnimation = createAnimation()
    .addElement(root.querySelector('.modal-wrapper'))
    .keyframes([
      { offset: 0, opacity: '0', transform: 'translateY(100%)' },
      { offset: 1, opacity: '1', transform: 'translateY(0)' },
    ]);
  
  return createAnimation()
    .addElement(baseEl)
    .easing('ease-in-out')
    .duration(500)
    .addAnimation([backdropAnimation, wrapperAnimation]);
};
```

---

## 7. Estilos y Diseño Visual

### 7.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.home-screen {
  position: relative;
  overflow: hidden;
}

.top-background {
  // Background gradient y posicionamiento
}

.border-shape {
  // Elementos decorativos de diseño
}

.main-content {
  // Contenedor principal del dashboard
}
```

#### **Animaciones Especiales**
```scss
.car {
  position: absolute;
  width: 140px;
  animation: carDriving 9s ease-in-out forwards;
}

@keyframes carDriving {
  0% { transform: translateX(-140px); }
  20% { transform: translateX(29vw); }
  25% { transform: translate(200vw); }
  100% { transform: translateX(200vw); }
}
```

### 7.2 Diseño Responsivo

- **Layout Flexible:** Uso de Flexbox para alineación
- **Componentes Modulares:** Cada sección es un componente independiente
- **Adaptación Cross-Platform:** Detalles específicos por plataforma

---

## 8. Manejo de Estados y Condiciones

### 8.1 Estados Especiales

```typescript
// Excepción para saldos bajos
if (contrato.saldo <= 0.5 && contrato.saldo > 0) this.excepcionSaldo = true;

// Ocultar detalles por ubicación
this.showBalanceDetails = !contrato.nombre_ciudad.includes('MARGARITA');

// Indicador de fecha límite
@if (upToDateStatus > 0 && currentDayValue >= 1 && currentDayValue <= 10) {
  <ion-label class="pb-16">Estás en la fecha límite de corte</ion-label>
}
```

### 8.2 Gestión de Ciclo de Vida

```typescript
ionViewWillEnter() {
  this.isPageActive = true;
  this.subscriptionservice.subscribeall();
}

ionViewWillLeave() {
  this.isPageActive = false;
  this.subscriptionContrato?.unsubscribe();
  this.subscriptionUser?.unsubscribe();
}
```

---

## 9. Integración con APIs Externas

### 9.1 API de Banners

- **Base URL:** Configurada en environment
- **Propósito:** Obtener banners promocionales dinámicos
- **Response:** Array de objetos `IBanner` con imágenes y URLs

### 9.2 API de Menú

- **Servicio:** MenuService
- **Propósito:** Configuración dinámica de navegación
- **Estructura:** Pinned items y main menu items

### 9.3 API de Tasa de Cambio

- **Servicio:** TasaMonedaService
- **Propósito:** Conversión USD/Bs en tiempo real
- **Frecuencia:** Actualización periódica

---

## 10. Consideraciones de Seguridad

### 10.1 Validaciones y Sanitización

- **Input Validation:** Validación de datos de usuario
- **URL Security:** Validación de URLs externas antes de apertura
- **Data Encryption:** Almacenamiento cifrado en localStorage

### 10.2 Manejo de Datos Sensibles

- **Balance Protection:** Opciones para ocultar detalles financieros
- **User Data:** Gestión segura de información personal
- **Session Management:** Limpieza apropiada de suscripciones

---

## 11. Testing y Calidad

### 11.1 Casos de Uso Críticos

1. **Carga inicial del dashboard**
2. **Actualización de balance en tiempo real**
3. **Navegación a funcionalidades principales**
4. **Carga y visualización de banners**
5. **Manejo de popups promocionales**
6. **Cambios de contrato y usuario**
7. **Estados especiales (saldos bajos, ubicaciones específicas)**

### 11.2 Pruebas Unitarias Requeridas

- Gestión de suscripciones y cleanup
- Cálculos de balance y conversión
- Manejo de estados de UI
- Integración con servicios
- Navegación y routing

---

## 12. Mejoras Futuras Sugeridas

### 12.1 Features Potenciales

1. **Real-time Updates:** WebSocket para actualizaciones instantáneas
2. **Advanced Analytics:** Métricas detalladas de uso
3. **Personalization:** Dashboard personalizable por usuario
4. **Offline Support:** Modo offline con caché inteligente
5. **Voice Commands:** Integración con asistentes de voz

### 12.2 Optimizaciones Técnicas

1. **State Management:** Implementación con NgRx o Signals
2. **Virtual Scrolling:** Para listas largas de transacciones
3. **Image Optimization:** Lazy loading de banners
4. **Bundle Splitting:** Mejora de tiempo de carga

---

## 13. Notas para Mantenimiento

### 13.1 Puntos Críticos

1. **Subscription Management:** Proper cleanup para evitar memory leaks
2. **Cache Strategy:** Coordinación con backend para actualizaciones
3. **Performance Monitoring:** Métricas de carga y renderizado
4. **Cross-Platform Testing:** Validación en iOS, Android y Web

### 13.2 Buenas Prácticas

- Mantener componentes desacoplados y reutilizables
- Implementar proper error handling y logging
- Validar todos los datos externos
- Mantener consistencia en el diseño y UX
- Documentar cambios en la API y estructura de datos

---

## 14. Conclusión

La Home Page representa el componente central y más complejo de la aplicación Oficina Móvil, sirviendo como hub principal para la gestión de servicios financieros y de telecomunicaciones. Su arquitectura modular basada en componentes especializados permite una mantenibilidad escalable mientras presenta una experiencia de usuario rica y funcional.

La integración con múltiples servicios, la gestión reactiva de datos, y la optimización de performance la convierten en un componente crítico que requiere especial atención durante el desarrollo y mantenimiento. Su diseño actual proporciona una base sólida para futuras mejoras y expansión de funcionalidades del dashboard.

---

*Documentación actualizada: 2026-04-13*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
