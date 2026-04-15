# RFC: Client Services Page - Visualización y Gestión de Servicios Fibex

## Introducción

La **Client Services Page** es el componente central de visualización de servicios de la aplicación **Oficina Móvil V2** que permite a los usuarios consultar y gestionar todos los servicios contratados con **Fibex Telecom**. Esta página implementa una interfaz de grid responsiva que muestra información detallada de cada servicio incluyendo tipo de servicio, plan, mensualidad, estado y opciones de acción como mejora de plan o reactivación.

Este RFC documenta la arquitectura técnica, flujo de usuario, gestión de estados y consideraciones de implementación de la página de servicios, que sirve como panel central para que los clientes puedan visualizar y administrar su portafolio de servicios Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/client-services.png" alt="Client Services Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | ClientServicesPage (src/app/pages/client-services/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/client-services/
    client-services.page.ts          # Componente principal con lógica de servicios
    client-services.page.html        # Template con grid de servicios
    client-services.page.scss        # Estilos específicos del componente
    client-services.page.spec.ts     # Pruebas unitarias
    client-services-routing.module.ts # Configuración de rutas
    client-services.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Angular Core**
- **Propósito:** Framework base para el componente
- **Configuración:** Component lifecycle management, dependency injection
- **Integración:** Mediante decoradores @Component, @Injectable
- **Documentación:** [Angular Documentation](https://angular.dev/)

#### **Ionic Framework**
- **Propósito:** Componentes UI nativos y navegación
- **Configuración:** ion-content, ion-icon, ion-button
- **Integración:** Componentes optimizados para móviles
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

#### **Angular Common**
- **Propósito:** Pipes y utilidades comunes
- **Configuración:** CommonModule para directivas estructurales
- **Integración:** *ngFor, *ngIf en templates
- **Documentación:** [Angular Common Documentation](https://www.npmjs.com/package/@angular/common)

#### **Angular Forms**
- **Propósito:** Gestión de formularios (potencial uso futuro)
- **Configuración:** FormsModule para template-driven forms
- **Integración:** Validaciones y manejo de datos
- **Documentación:** [Angular Forms Documentation](https://angular.dev/guide/forms)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura de Visualización

La página implementa una interfaz basada en grid que muestra diferentes estados según los servicios disponibles:

#### **Estado: Sin Servicios**
- **Componente:** Mensaje informativo con CTA
- **Propósito:** Guiar al usuario a adquirir servicios
- **Features:** 
  - Mensaje descriptivo
  - Botón "Adquirir uno" para redirección

#### **Estado: Con Servicios**
- **Componente:** Grid responsivo de tarjetas de servicio
- **Propósito:** Mostrar información detallada de cada servicio
- **Features:** 
  - Grid adaptativo (1 columna móvil, 2 columnas desktop)
  - Tarjetas con información completa
  - Estados visuales diferenciados

#### **Tarjeta de Servicio Individual**
- **Header:** Número de abonado y estado (activo/inactivo)
- **Iconos:** FibexPlay o ícono de Internet según tipo
- **Información:** Tipo, plan, mensualidad, estado exoneración
- **Acciones:** Mejorar plan (activo) o Reactivar plan (inactivo)

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
// Datos del usuario y contrato
public servicios: any[] = [];
public contrato: ItmContratoTable | null = null;
public userDatos: IContract | null = null;

// Estados de UI
public loading = false;
private subscriptionContrato: Subscription | undefined;
```

#### **Carga de Servicios**
```typescript
async ngOnInit() {
  try {
    this.loading = true;
    this.subscriptionContrato = this.userService.GetContratoSelected().subscribe(contrato => {
      this.contrato = contrato;
      
      this.userDatos = {
        nro_abonado: this.contrato?.nro_abonado || '',
        is_exonerado: this.contrato?.is_exonerado || 0,
      };
      
      this.utils
        .show('Obteniendo información')
        .then(loading => {
          this.userService
            .GetServicios()
            .then(servicios => {
              this.servicios = servicios.map(servItem => this.procesarServicio(servItem));
              this.loading = false;
            })
            .finally(() => {
              loading.dismiss().catch(console.error);
            });
        });
    });
  } catch (error) {
    this.loading = false;
    console.error(error);
  }
}
```

### 3.2 Procesamiento de Servicios

#### **Clasificación de Servicios**
```typescript
procesarServicio(servicio: any) {
  let tipoServicio = 'Desconocido';
  if (servicio.nombre_servicio.includes('FTTH')) {
    tipoServicio = 'INTERNET';
  } else if (servicio.nombre_servicio.includes('FIBEXPLAY')) {
    tipoServicio = 'FIBEXPLAY';
  }
  return {
    ...servicio,
    tipoServicio: tipoServicio,
  };
}
```

#### **Navegación a Acciones**
```typescript
public goToService(action: string) {
  if (action === 'upgrade') {
    this.utils.navigateToPage('tabs/plan-upgrade');
  } else {
    this.utils.navigateToPage('tabs/payment-now');
  }
}
```

---

## 4. Componentes Compartidos Integrados

### 4.1 Componente Principal

#### **ContentHeaderComponent**
- **Ruta:** `importsComponents/headers/content-header/content-header.component`
- **Propósito:** Header estándar con título y navegación
- **Features:** 
  - Título "Servicios"
  - Botón de retroceso
  - Layout consistente con otras páginas

### 4.2 Estructura de Template

#### **Grid Responsivo**
```html
<div class="grid grid-cols-1 md:grid-cols-2 grid-flow-row items-center justify-center p-4 gap-4 place-items-center max-w-7xl mx-auto">
  <!-- Tarjetas de servicio -->
  @for (servicio of servicios; track $index) {
    <div class="servicio-card">
      <!-- Contenido de la tarjeta -->
    </div>
  }
</div>
```

#### **Tarjeta de Servicio**
```html
<div class="servicio-card" [ngClass]="{ 'is-exonerado': userDatos?.is_exonerado === 1 }">
  <!-- Header con número y estado -->
  <div [class]="servicio.estatus === 'ACTIVO' ? 'abonado-title' : 'abonado-title-inactive'">
    <p>{{ userDatos?.nro_abonado }}</p>
  </div>
  
  <!-- Detalles del servicio -->
  <div class="servicio-details">
    <!-- Icono y estado -->
    <section class="flex items-center justify-between">
      @if (servicio.tipoServicio === 'FIBEXPLAY') {
        <img src="../../../assets/images/icons/fibexplay-icon.png" alt="Fibexplay" class="service-icon" />
      } @else {
        <ion-icon name="globe-outline" class="service-icon text-[#0154E9]"></ion-icon>
      }
      <!-- Estado del servicio -->
    </section>
    
    <!-- Información detallada -->
    <section class="service-info">
      <div class="flex justify-between">
        <p class="service-text">Tipo de servicio</p>
        <span>{{ servicio.tipoServicio }}</span>
      </div>
      <div class="flex justify-between">
        <p class="service-text">Plan</p>
        <span>{{ servicio.nombre_servicio }}</span>
      </div>
      <div class="flex justify-between">
        <p class="service-text">Mensualidad</p>
        <span>${{ servicio.tarifa }}</span>
      </div>
    </section>
  </div>
  
  <!-- Acciones -->
  <div class="bg-blue flex-center rounded-b-lg absolute bottom-0 right-0 left-0">
    @if (servicio.estatus === 'ACTIVO') {
      <button (click)="goToService('upgrade')" class="service-button">
        Mejorar plan
        <ion-icon name="rocket" class="size-icon"></ion-icon>
      </button>
    } @else {
      <button (click)="goToService('pay-now')" class="service-button hover-scale">
        Reactivar plan
      </button>
    }
  </div>
</div>
```

---

## 5. Integración con Servicios

### 5.1 Servicios Principales

#### **UserService**
- **Propósito:** Gestión de datos de usuario y servicios
- **Métodos clave:** `GetServicios()`, `GetContratoSelected()`
- **Flujo:** Observable para cambios en contrato, Promise para servicios
- **Datos:** Array de servicios con información completa

#### **UtilService**
- **Propósito:** Utilidades de navegación y UI
- **Métodos clave:** `show()`, `navigateToPage()`
- **Uso:** Loading indicators, navegación programática
- **Features:** Manejo de modales, redirección con parámetros

### 5.2 Flujo de Datos

#### **Obtención de Servicios**
```typescript
// 1. Suscripción a cambios de contrato
this.subscriptionContrato = this.userService.GetContratoSelected().subscribe(contrato => {
  this.contrato = contrato;
  
  // 2. Preparación de datos de usuario
  this.userDatos = {
    nro_abonado: this.contrato?.nro_abonado || '',
    is_exonerado: this.contrato?.is_exonerado || 0,
  };
  
  // 3. Obtención de servicios con loading
  this.userService.GetServicios()
    .then(servicios => {
      this.servicios = servicios.map(servItem => this.procesarServicio(servItem));
    });
});
```

---

## 6. Estilos y Diseño Visual

### 6.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.servicio-card {
  @apply drop-shadow-lg w-full max-w-md lg:max-w-xl flex flex-col lg:flex-row border-2 relative ease-in-out duration-300;
}

.is-exonerado {
  @apply h-64;
}

.is-not-exonerado {
  @apply h-56 lg:h-60;
}

.abonado-title {
  @apply -top-2 left-0 right-0 bg-blue-600 h-6 w-16 mx-auto rounded-md absolute flex items-center justify-center text-xs text-white font-semibold;
}

.abonado-title-inactive {
  @apply -top-2 left-0 right-0 bg-red-500 h-6 w-16 mx-auto rounded-md absolute flex items-center justify-center text-xs text-white font-semibold;
}
```

#### **Diseño Responsivo**
- **Grid Adaptativo:** 1 columna en móvil, 2 columnas en desktop
- **Tarjetas Flexibles:** Layout horizontal en desktop, vertical en móvil
- **Iconos Escalables:** Tamaño adaptativo según pantalla
- **Botones Interactivos:** Hover effects y animaciones suaves

### 6.2 Optimizaciones de UI

- **Loading States:** Indicadores durante carga de servicios
- **Empty States:** Manejo elegante cuando no hay servicios
- **Status Indicators:** Diferenciación visual activo/inactivo
- **Hover Effects:** Feedback visual en elementos interactivos
- **Transitions Suaves:** Animaciones entre estados

---

## 7. Flujo de Usuario Detallado

### 7.1 Caminos Principales

#### **Usuario con Servicios Activos**
1. Carga de página con loading indicator
2. Visualización de grid con tarjetas de servicio
3. Cada tarjeta muestra: tipo, plan, mensualidad, estado
4. Opción "Mejorar plan" para servicios activos
5. Redirección a plan-upgrade con datos del servicio

#### **Usuario con Servicios Inactivos**
1. Misma visualización que usuario activo
2. Tarjetas con indicador visual rojo
3. Opción "Reactivar plan" para servicios inactivos
4. Redirección a payment-now para reactivación

#### **Usuario sin Servicios**
1. Mensaje informativo centralizado
2. Botón "Adquirir uno" como CTA principal
3. Redirección a flujo de adquisición

#### **Usuario Exonerado**
1. Visualización especial con altura aumentada
2. Indicador "Cuenta exonerada" en cada servicio
3. Sin opciones de pago disponibles

### 7.2 Estados de Error y Recuperación

- **Error de Carga:** Manejo con try-catch y loading states
- **Servicios Vacíos:** Empty state con CTA apropiado
- **Error de Navegación:** Manejo de errores en redirecciones
- **Timeout:** Manejo de timeouts en carga de datos

---

## 8. Consideraciones de Performance

### 8.1 Optimizaciones Implementadas

1. **Lazy Loading:** Componente cargado bajo demanda
2. **Subscription Management:** Cleanup apropiado de observables
3. **Image Optimization:** Iconos optimizados para diferentes tamaños
4. **CSS Efficient:** Uso de Tailwind para estilos optimizados

### 8.2 Manejo de Memoria

```typescript
ngOnDestroy(): void {
  if (this.subscriptionContrato) {
    this.subscriptionContrato.unsubscribe();
    this.subscriptionContrato = undefined;
  }
}
```

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Visualización de servicios múltiples**
2. **Servicios activos vs inactivos**
3. **Usuarios exonerados**
4. **Responsive design móvil/desktop**
5. **Navegación a mejora de plan**
6. **Navegación a reactivación**
7. **Empty states sin servicios**
8. **Error handling en carga**

### 9.2 Pruebas Unitarias Requeridas

- Carga inicial de servicios
- Procesamiento de tipos de servicio
- Manejo de estados de UI
- Navegación a otras páginas
- Limpieza de subscriptions
- Renderizado condicional

---

## 10. Consideraciones de Accesibilidad

### 10.1 Features de Accesibilidad

- **Semantic HTML:** Uso apropiado de elementos semánticos
- **ARIA Labels:** Labels descriptivos para screen readers
- **Keyboard Navigation:** Navegación por teclado funcional
- **Color Contrast:** Contraste adecuado para texto y estados
- **Focus States:** Indicadores visuales de foco claros

### 10.2 Validaciones de Accesibilidad

- **WCAG Compliance:** Nivel AA de conformidad
- **Screen Reader Testing:** Compatibilidad con lectores de pantalla
- **Mobile Accessibility:** Features específicas para dispositivos móviles
- **Voice Navigation:** Compatibilidad con comandos de voz

---

## 11. Mejoras Futuras Sugeridas

### 11.1 Features Potenciales

1. **Service Analytics:** Estadísticas de uso por servicio
2. **Bulk Actions:** Acciones múltiples sobre servicios
3. **Service Comparison:** Herramienta de comparación de planes
4. **Real-time Status:** Actualización en tiempo real de estados
5. **Service History:** Historial de cambios y upgrades

### 11.2 Optimizaciones Técnicas

1. **Virtual Scrolling:** Para grandes cantidades de servicios
2. **Service Caching:** Cache inteligente de datos de servicios
3. **Progressive Loading:** Carga progresiva de información
4. **Offline Support:** Visualización offline de servicios cacheados
5. **Service Notifications:** Notificaciones de cambios de estado

---

## 12. Notas para Mantenimiento

### 12.1 Puntos Críticos

1. **Subscription Management:** Proper cleanup para evitar memory leaks
2. **Service Data Structure:** Mantener compatibilidad con backend
3. **Responsive Design:** Testing en múltiples dispositivos
4. **State Management:** Coordinación con otros componentes
5. **Error Handling:** Manejo robusto de errores de red

### 12.2 Buenas Prácticas

- Mantener estructura de datos consistente
- Implementar proper loading states
- Validar todos los datos del servicio
- Documentar cambios en la estructura de servicios
- Realizar testing cross-browser y cross-platform

---

## 13. APIs y Servicios Internos

### 13.1 UserService API

- **Propósito:** Gestión centralizada de datos de usuario y servicios
- **Métodos principales:** 
  - `GetServicios()`: Promise que retorna array de servicios
  - `GetContratoSelected()`: Observable para cambios de contrato
- **Uso en la aplicación:** 
  - Carga inicial de servicios al montar componente
  - Actualización automática cuando cambia el contrato
  - Procesamiento de datos para visualización

### 13.2 UtilService API

- **Propósito:** Utilidades compartidas de UI y navegación
- **Métodos principales:** 
  - `show()`: Muestra loading indicator
  - `navigateToPage()`: Navegación programática
- **Uso en la aplicación:** 
  - Indicadores de carga durante operaciones asíncronas
  - Redirección a páginas de mejora de plan o pago
  - Manejo consistente de navegación

---

## 14. Componentes y Código Destacable

### 14.1 Grid Responsivo

```html
<div class="grid grid-cols-1 md:grid-cols-2 grid-flow-row items-center justify-center p-4 gap-4 place-items-center max-w-7xl mx-auto">
  @for (servicio of servicios; track $index) {
    <div class="servicio-card">
      <!-- Contenido de la tarjeta -->
    </div>
  }
</div>
```

**Características:**
- Layout adaptativo con Tailwind CSS
- Centrado automático de elementos
- Máximo ancho para mejor legibilidad
- Gap consistente entre elementos

### 14.2 Tarjeta de Servicio Dinámica

```typescript
procesarServicio(servicio: any) {
  let tipoServicio = 'Desconocido';
  if (servicio.nombre_servicio.includes('FTTH')) {
    tipoServicio = 'INTERNET';
  } else if (servicio.nombre_servicio.includes('FIBEXPLAY')) {
    tipoServicio = 'FIBEXPLAY';
  }
  return {
    ...servicio,
    tipoServicio: tipoServicio,
  };
}
```

**Características:**
- Clasificación automática de servicios
- Extensión de datos con tipo procesado
- Lógica flexible para nuevos tipos de servicio

### 14.3 Gestión de Estados con Tailwind

```scss
.servicio-card {
  @apply drop-shadow-lg w-full max-w-md lg:max-w-xl flex flex-col lg:flex-row border-2 relative ease-in-out duration-300;
}

.is-exonerado {
  @apply h-64;
}

.is-not-exonerado {
  @apply h-56 lg:h-60;
}
```

**Características:**
- Clases condicionales según estado
- Diseño responsivo con breakpoints
- Transiciones suaves entre estados
- Altura variable según exoneración

---

## 15. Conclusión

La Client Services Page representa un componente fundamental en la arquitectura de Oficina Móvil para la visualización y gestión de servicios Fibex. Su implementación mediante grid responsivo permite mostrar información completa de manera clara y accesible, con diferentes estados según la situación del usuario (activo, inactivo, exonerado, sin servicios).

La arquitectura modular, la integración con servicios centrales y el manejo robusto de estados la convierten en un componente esencial que requiere especial atención durante el mantenimiento y evolución de la aplicación. Su diseño actual proporciona una base sólida para futuras mejoras como analytics de servicios, acciones bulk y notificaciones en tiempo real.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
