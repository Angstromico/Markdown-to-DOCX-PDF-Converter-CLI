# RFC: Averia Page - Sistema de Soporte Técnico y Gestión de Averías

## Introducción

La **Averia Page** es el componente central de soporte técnico de la aplicación **Oficina Móvil V2** que permite a los usuarios reportar, gestionar y dar seguimiento a averías de servicios **Fibex Telecom**. Esta página implementa un sistema multi-step con Swiper para navegación fluida, clasificación de tipos de soporte, gestión de órdenes de servicio y seguimiento detallado del estado de cada reporte.

Este RFC documenta la arquitectura técnica, flujo de usuario, sistema de reporte de averías, integración con componentes especializados y consideraciones de implementación de la página de soporte, que sirve como portal central para la gestión de incidencias técnicas de los clientes Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/averia.jpeg" alt="Averia Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | AveriaPage (src/app/pages/averia/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/averia/
    averia.page.ts          # Componente principal con lógica de soporte
    averia.page.html        # Template con Swiper y formularios
    averia.page.scss        # Estilos específicos del componente
    averia.page.spec.ts     # Pruebas unitarias
    averia-routing.module.ts # Configuración de rutas
    averia.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Swiper.js**
- **Propósito:** Biblioteca de carrusel moderno para navegación fluida
- **Configuración:** slides-per-view="1", autoplay="true", touch control
- **Integración:** Mediante swiper-container y swiper-slide elements
- **Documentación:** [Swiper.js Documentation](https://swiperjs.com/)

#### **Angular Core**
- **Propósito:** Framework base con lifecycle management
- **Configuración:** Component lifecycle, dependency injection
- **Integración:** Decoradores @Component, @ViewChild, OnInit
- **Documentación:** [Angular Documentation](https://angular.dev/)

#### **Ionic Framework**
- **Propósito:** Componentes UI nativos y navegación
- **Configuración:** ion-segment, ion-spinner, ion-content
- **Integración:** ViewWillEnter, ViewDidLeave lifecycle hooks
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

#### **Angular Forms**
- **Propósito:** Gestión de formularios y bindings
- **Configuración:** FormsModule para formularios reactivos
- **Integración:** [(ngModel)] bindings en componentes
- **Documentación:** [Angular Forms Documentation](https://angular.dev/guide/forms)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura Multi-Step

La página implementa una interfaz de 3 pasos mediante Swiper:

#### **Paso 1: Selección de Tipo de Soporte**
- **Componente:** Grid de cards con tipos de avería
- **Propósito:** Clasificar el tipo de problema técnico
- **Features:** 
  - Cards con iconos representativos
  - Descripción detallada de cada tipo
  - Botón "Continuar" con loading state
  - Detección de servicios Express

#### **Paso 2: Formulario de Reporte**
- **Componente:** Formulario especializado según tipo seleccionado
- **Propósito:** Capturar detalles específicos del problema
- **Features:** 
  - Campos dinámicos según tipo de avería
  - Validación en tiempo real
  - Opciones predefinidas para servicios Express
  - Botón de envío con confirmación

#### **Paso 3: Lista de Órdenes**
- **Componente:** Lista de órdenes de servicio con estados
- **Propósito:** Mostrar historial y estado actual
- **Features:** 
  - Órdenes ordenadas por fecha
  - Indicadores visuales de estado
  - Contador de órdenes en header
  - Empty state para usuarios sin órdenes

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
// Datos de soporte
public types: ISoporteType[] = [];
public typeSoporte: ISoporteType;
public gettingDetallesOrdenes: number | undefined;
public detallesOrdenes: ItmDetalleOrden[] = [];

// Estados de UI
public titleHeader: string = 'Soporte Técnico';
public contractStatus: string = '';
public loading: boolean = true;
public ordenes: ItmOrdenServicio[] = [];

// Control de Swiper
public value: number = 1;
@ViewChild('swiper') swiperRef?: ElementRef<{ swiper: Swiper }>;
@ViewChild('swiperContainer') swiperContainerRef: ElementRef<{ swiper: Swiper }>;
```

#### **Carga de Tipos de Soporte**
```typescript
ionViewWillEnter() {
  this.networkService.validateNetworkAccess();
  this.reporte.getTypes((types: ISoporteType[]) => {
    this.types = types;
  });

  // Cargar órdenes existentes
  this.Subscriptionuser = this.user.GetContratoSelected().subscribe(contrato => {
    this.changeValue(1);
    this.loading = true;
    this.reporte
      .GetOrdenesReclamos()
      .then(ordenes => {
        this.ordenes = ordenes.sort((a, b) => {
          const dateA = new Date(a.fecha_orden).getTime();
          const dateB = new Date(b.fecha_orden).getTime();
          return dateB - dateA;
        });
      })
      .finally(() => {
        this.loading = false;
      });
  });
}
```

### 3.2 Sistema de Navegación con Swiper

#### **Control de Slides**
```typescript
public changeValue(value: number) {
  this.value = value;
  this.swiperContainerRef.nativeElement.swiper.slideTo(this.value - 1);
}

public slideBack() {
  if (this.swiperRef) {
    this.swiperRef.nativeElement.swiper.slidePrev();
  }
}

slideBack() {
  if (this.swiperRef) {
    this.swiperRef.nativeElement.swiper.slidePrev();
  }
}
```

#### **Configuración de Swiper**
```typescript
public ngAfterViewInit() {
  if (this.swiperRef) {
    this.swiperRef.nativeElement.swiper.allowTouchMove = false; // Disables touch control
    this.swiperRef.nativeElement.swiper.update(); // Update Swiper instance
  }
  if (this.swiperContainerRef) {
    this.swiperContainerRef.nativeElement.swiper.allowTouchMove = false; // Disables touch control
    this.swiperContainerRef.nativeElement.swiper.update(); // Update Swiper instance
  }
}
```

---

## 4. Componentes Compartidos Integrados

### 4.1 Componentes Principales

#### **ContentHeaderComponent**
- **Ruta:** `importsComponents/headers/content-header/content-header.component`
- **Propósito:** Header estándar con título dinámico y navegación
- **Features:** 
  - Título dinámico según paso activo
  - Función de retroceso personalizada
  - Layout consistente con otras páginas

#### **ReportProblemComponent**
- **Ruta:** `importsComponents/swiper/report-problem/report-problem.component`
- **Propósito:** Formulario especializado para reporte de problemas
- **Features:** 
  - Campos dinámicos según tipo de soporte
  - Validación en tiempo real
  - Integración con servicios Express
  - Evento de retroceso

#### **IframeTemplateComponent**
- **Ruta:** `importsComponents/iframe-template/iframe-template.component`
- **Propósito:** Template para contenido iframe
- **Features:** 
  - Manejo de contenido externo
  - Responsive design
  - Loading states

### 4.2 Estructura de Template

#### **Segment Control**
```html
<ion-segment [value]="value" (ionChange)="changeValueEv($event)" mode="md">
  <ion-segment-button [value]="1">
    <ion-label>Crear orden</ion-label>
  </ion-segment-button>
  <ion-segment-button [value]="2">
    <ion-label>Mis ordenes{{ this.ordenes.length ? (" (" + this.ordenes.length + ")") : ""}}</ion-label>
  </ion-segment-button>
</ion-segment>
```

#### **Swiper Container**
```html
<swiper-container
  class="swiper-container-averia"
  #swiperContainer
  slides-per-view="1"
  autoplay="true"
  style="width: 100%"
>
  <swiper-slide class="averia-main-slide">
    <!-- Slide 1: Tipos de Soporte -->
    <div>
      <swiper-container #swiper slides-per-view="1" autoplay="true" style="width: 100%">
        <swiper-slide>
          @for (type of types; track $index) {
            <div class="bg-white rounded-xl shadow-lg transition flex-1">
              <div class="flex items-center p-6 rounded-t-xl border-blue-600 border-t-2 border-l-2 border-r-2">
                <ion-icon [name]="type.ionIcon" class="h-12 w-12 text-blue-500"></ion-icon>
                <div class="ml-6">
                  <div class="text-blue-600 font-bold text-lg">{{ type.title }}</div>
                  <p class="text-gray-600 mt-1">{{ type.description }}</p>
                </div>
              </div>
              <button
                class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-3 rounded-b-xl"
                (click)="SelectTypeToReport(type)"
                [disabled]="gettingDetallesOrdenes"
              >
                @if(gettingDetallesOrdenes === type.id) {
                  <ion-spinner name="crescent" style="color: white"></ion-spinner>
                  } @else { Continuar }
                </button>
            </div>
          }
        </swiper-slide>
      </swiper-container>
    </div>
  </swiper-slide>

  <swiper-slide>
    <!-- Slide 2: Formulario de Reporte -->
    @if (typeSoporte) {
      <div class="overflow-auto h-full px-2">
        <app-report-problem
          [typeSoporte]="typeSoporte"
          [detallesOrdenes]="detallesOrdenes"
          (back)="slideBack()"
        ></app-report-problem>
      </div>
    }
  </swiper-slide>

  <swiper-slide class="averia-main-slide">
    <!-- Slide 3: Lista de Órdenes -->
    @if (loading) {
      <div class="w-full text-blue-600 flex items-center justify-center pt-12">
        <ion-spinner style="width: 80px; height: 80px" name="circular"></ion-spinner>
      </div>
    } @else { @if (ordenes.length) { @for (orden of ordenes; track $index) {
        <div class="flex flex-col bg-white shadow-md rounded-lg p-4 mb-4 border border-gray-200">
          <!-- Contenido de orden -->
        </div>
      } } @else {
        <div class="flex justify-center items-center gap-4 flex-col mx-4 mt-6 py-6 border font-bold border-blue-500 text-blue-500 rounded-3xl smooth">
          <span>No hay ordenes registradas</span>
        </div>
      } }
    }
  </swiper-slide>
</swiper-container>
```

---

## 5. Integración con Servicios

### 5.1 Servicios Principales

#### **SoporteService**
- **Propósito:** Gestión centralizada de soporte técnico
- **Métodos clave:** `getTypes()`, `GetOrdenesReclamos()`, `getReasonForReport()`
- **Flujo:** Observable para tipos, Promise para órdenes y detalles
- **Datos:** Tipos de soporte, órdenes de servicio, razones de reporte

#### **UserService**
- **Propósito:** Gestión de datos de usuario y contratos
- **Métodos clave:** `GetContratoSelected()`, `GetServicios()`
- **Uso:** Obtener contrato activo y servicios para validación

#### **NetworkStatusService**
- **Propósito:** Validación de conectividad
- **Métodos clave:** `validateNetworkAccess()`
- **Uso:** Verificar conexión antes de operaciones críticas

#### **UtilService**
- **Propósito:** Utilidades compartidas de UI y navegación
- **Métodos clave:** `onBack()`
- **Uso:** Navegación consistente y retroceso

---

## 6. Estilos y Diseño Visual

### 6.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.swiper-container-averia {
  width: 100%;
  height: 100%;
  border: 0 !important;
  outline: 0 !important;
}

.averia-main-slide {
  padding: 1rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.go-back {
  position: absolute;
  width: 5rem;
  height: 5rem;
  font-size: 2rem;
  place-content: center;
  display: flex;
  align-items: center;
  background: #0154e9;
}
```

#### **Diseño Responsivo**
- **Adaptativo:** Layout se ajusta según tamaño de pantalla
- **Swiper Navigation:** Control programático sin touch
- **Cards Grid:** Layout responsivo para tipos de soporte
- **Form Containers:** Ancho completo en todos los dispositivos

### 6.2 Estados Visuales

- **Loading States:** Spinners durante carga de datos
- **Empty States:** Mensaje apropiado sin órdenes
- **Status Indicators:** Colores diferentes para estados de órdenes
- **Hover Effects:** Feedback visual en elementos interactivos

---

## 7. Flujo de Usuario Detallado

### 7.1 Caminos Principales

#### **Usuario Nuevo (Sin Órdenes)**
1. Carga inicial con loading indicator
2. Visualización de tipos de soporte disponibles
3. Selección de tipo de problema
4. Carga de formulario específico
5. Llenado y envío de reporte
6. Confirmación y creación de orden

#### **Usuario con Órdenes Existentes**
1. Carga inicial con lista de órdenes
2. Navegación a "Mis órdenes"
3. Visualización de historial con estados
4. Opción de crear nueva orden
5. Seguimiento de estado actual

#### **Detección de Servicios Express**
```typescript
const isExpress = servicios.some(
  s =>
    s.tipo_servicio?.trim() === 'FIBEX EXPRESS PYME' ||
    s.tipo_servicio?.trim() === 'FIBEX EXPRESS HOGAR',
);

if (this.swiperRef) {
  this.detallesOrdenes = isExpress
    ? detalles.filter(detalle => detalle.nombre_det_orden !== 'FALLA LOS')
    : detalles;
}
```

### 7.2 Estados de Error y Recuperación

- **Error de Carga:** Manejo con try-catch y loading states
- **Error de Red:** Validación de conectividad antes de operaciones
- **Error de Envío:** Retroalimentación clara con opciones de reintentar
- **Error de Navegación:** Manejo de errores en Swiper navigation

---

## 8. Consideraciones de Performance

### 8.1 Optimizaciones Implementadas

1. **Lazy Loading:** Componentes cargados bajo demanda
2. **Swiper Optimization:** Configuración para performance óptimo
3. **Subscription Management:** Cleanup apropiado de observables
4. **Efficient Sorting:** Algoritmo optimizado para ordenamiento de fechas

### 8.2 Manejo de Memoria

```typescript
ionViewDidLeave(): void {
  this.Subscriptionuser.unsubscribe();
  if (this.swiperRef) {
    this.swiperRef.nativeElement.swiper.slideTo(0);
  }
}
```

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Carga inicial de tipos de soporte**
2. **Navegación entre slides con Swiper**
3. **Selección de tipo de soporte**
4. **Carga dinámica de formulario**
5. **Detección de servicios Express**
6. **Creación de nueva orden**
7. **Visualización de lista de órdenes**
8. **Ordenamiento por fecha**
9. **Responsive design**
10. **Error handling**

### 9.2 Pruebas Unitarias Requeridas

- Carga y filtrado de tipos de soporte
- Navegación con Swiper
- Manejo de estados de UI
- Integración con servicios
- Manejo de errores
- Responsive behavior
- Performance de ordenamiento

---

## 10. Consideraciones de Seguridad

### 10.1 Manejo de Datos Sensibles

- **Validación de Entrada:** Sanitización de datos de formulario
- **Network Validation:** Verificación de conectividad antes de envío
- **Data Encryption:** Manejo seguro de información de órdenes
- **Access Control:** Validación de usuario antes de operaciones

### 10.2 Validaciones de Formulario

- **Campos Requeridos:** Validación de datos obligatorios
- **Format Validation:** Validación de formatos específicos
- **Length Limits:** Límites de caracteres para campos
- **Cross-Site Scripting:** Protección contra XSS

---

## 11. APIs y Servicios Externos

### 11.1 Swiper.js API

- **URL:** https://swiperjs.com/
- **Propósito:** Biblioteca de carrusel moderna y performante
- **Uso en la aplicación:** 
  - Navegación multi-step fluida
  - Control programático de slides
  - Autoplay y configuración avanzada
  - Touch control deshabilitado para control preciso
- **Características:** 
  - Cross-browser compatibility
  - Touch y mouse support
  - Performance optimizada
  - Extensible con plugins

---

## 12. Componentes y Código Destacable

### 12.1 Sistema de Navegación con Swiper

```typescript
public changeValue(value: number) {
  this.value = value;
  this.swiperContainerRef.nativeElement.swiper.slideTo(this.value - 1);
}

public slideBack() {
  if (this.swiperRef) {
    this.swiperRef.nativeElement.swiper.slidePrev();
  }
}

public goBack() {
  if (this.swiperRef && this.swiperRef.nativeElement.swiper.activeIndex > 0) {
    this.slideBack();
  } else {
    this.router.navigate(['/tabs/home']);
  }
}
```

**Características:**
- Control programático preciso de slides
- Navegación condicional según posición
- Integración con navegación global de la app
- Manejo de bordes del Swiper

### 12.2 Detección de Servicios Express

```typescript
SelectTypeToReport(soporte: ISoporteType) {
  if (!this.gettingDetallesOrdenes) {
    this.gettingDetallesOrdenes = soporte.id;

    Promise.all([this.user.GetServicios(), this.reporte.getReasonForReport(soporte)])
      .then(([servicios, detalles]) => {
        this.typeSoporte = soporte;
        const isExpress = servicios.some(
          s =>
            s.tipo_servicio?.trim() === 'FIBEX EXPRESS PYME' ||
            s.tipo_servicio?.trim() === 'FIBEX EXPRESS HOGAR',
        );

        if (this.swiperRef) {
          this.detallesOrdenes = isExpress
            ? detalles.filter(detalle => detalle.nombre_det_orden !== 'FALLA LOS')
            : detalles;
          this.swiperRef.nativeElement.swiper.slideNext();
          this.handleActiveHeaderTitle();
        }
      });
  }
}
```

**Características:**
- Detección automática de servicios Express
- Filtrado dinámico de opciones disponibles
- Carga asíncrona de servicios y detalles
- Navegación automática al siguiente paso

### 12.3 Gestión Dinámica de Header

```typescript
public handleActiveHeaderTitle = () => {
  if (this.swiperRef) {
    switch (this.swiperRef.nativeElement.swiper.activeIndex) {
      case 1:
        this.titleHeader = 'Reportar avería';
        break;
      default:
        this.titleHeader = 'Soporte Técnico';
        break;
    }
  }
};
```

**Características:**
- Título dinámico según slide activo
- Integración con ContentHeaderComponent
- Manejo centralizado de estados visuales
- Fallback a título por defecto

---

## 13. Mejoras Futuras Sugeridas

### 13.1 Features Potenciales

1. **Real-time Updates:** Actualización en tiempo real de estados de órdenes
2. **File Attachments:** Adjuntar imágenes o documentos a reportes
3. **Chat Integration:** Chat directo con técnicos asignados
4. **Notifications Push:** Alertas de cambios en estado de órdenes
5. **Analytics Dashboard:** Métricas de soporte técnico

### 13.2 Optimizaciones Técnicas

1. **Virtual Scrolling:** Para grandes cantidades de órdenes
2. **Offline Mode:** Cache de órdenes para acceso offline
3. **Progressive Loading:** Carga progresiva de componentes
4. **Service Worker:** Caching inteligente de datos
5. **Performance Monitoring:** Métricas de uso y rendimiento

---

## 14. Notas para Mantenimiento

### 14.1 Puntos Críticos

1. **Swiper Configuration:** Mantener configuración óptima para performance
2. **Service Integration:** Mantener compatibilidad con APIs de soporte
3. **State Management:** Coordinación entre slides y componentes
4. **Error Handling:** Manejo robusto de errores de red
5. **Performance:** Optimización para grandes volúmenes de datos

### 14.2 Buenas Prácticas

- Mantener validación de todos los datos de entrada
- Implementar proper loading states
- Mantener consistencia en navegación
- Documentar cambios en APIs externas
- Realizar testing cross-browser regularmente
- Optimizar para dispositivos móviles

---

## 15. Conclusión

La Averia Page representa un componente esencial en la arquitectura de Oficina Móvil para la gestión de soporte técnico. Su implementación con sistema multi-step mediante Swiper, clasificación inteligente de problemas, detección de servicios Express y gestión completa de órdenes la convierten en una solución integral para el soporte técnico de clientes Fibex.

La arquitectura modular, la integración con Swiper.js para navegación fluida y el manejo inteligente de estados proporcionan una base sólida para futuras mejoras como actualizaciones en tiempo real, adjuntos de archivos y chat directo con técnicos. Su diseño actual ofrece una experiencia de usuario intuitiva y eficiente tanto en plataformas móviles como web.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
