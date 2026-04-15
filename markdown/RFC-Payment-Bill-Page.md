# RFC: Payment Bill Page - Gestión de Facturas y Estado de Cuenta

## Introducción

La **Payment Bill Page** es el componente central de gestión de facturas de la aplicación **Oficina Móvil V2** que permite a los usuarios consultar, descargar y administrar todas sus facturas y el estado de cuenta de servicios **Fibex Telecom**. Esta página implementa un sistema de paginación avanzada con descarga de PDFs tanto nativa como web, mostrando información detallada de cada factura incluyendo número, fecha, monto y opciones de descarga directa.

Este RFC documenta la arquitectura técnica, flujo de usuario, sistema de paginación, manejo de archivos y consideraciones de implementación de la página de facturas, que sirve como portal central para la gestión documental financiera de los clientes Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/payment-bill.jpeg" alt="Payment Bill Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | PaymentBillPage (src/app/pages/payment-bill/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/payment-bill/
    payment-bill.page.ts          # Componente principal con lógica de facturas
    payment-bill.page.html        # Template con tarjeta de estado y lista de facturas
    payment-bill.page.scss        # Estilos específicos del componente
    payment-bill.page.spec.ts     # Pruebas unitarias
    payment-bill-routing.module.ts # Configuración de rutas
    payment-bill.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **@capacitor/filesystem**
- **Propósito:** Acceso al sistema de archivos nativo para guardar PDFs
- **Configuración:** Directory.Documents, recursive path creation
- **Integración:** Mediante `Filesystem.writeFile()` para descargas nativas
- **Documentación:** [Capacitor Filesystem Documentation](https://capacitorjs.com/docs/apis/filesystem)

#### **@capacitor-community/file-opener**
- **Propósito:** Apertura de archivos en aplicaciones nativas
- **Configuración:** contentType 'application/pdf', filePath handling
- **Integración:** Mediante `FileOpener.open()` para visualizar PDFs descargados
- **Documentación:** [Capacitor File Opener Documentation](https://github.com/capacitor-community/file-opener)

#### **Angular Core**
- **Propósito:** Framework base con lifecycle management
- **Configuración:** Component lifecycle, dependency injection
- **Integración:** Decoradores @Component, @ViewChild, @HostListener
- **Documentación:** [Angular Documentation](https://angular.dev/)

#### **Ionic Framework**
- **Propósito:** Componentes UI nativos y navegación
- **Configuración:** ion-spinner, ion-icon, ion-content
- **Integración:** ViewWillEnter, ViewWillLeave lifecycle hooks
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura de Visualización

La página implementa una interfaz de dos secciones principales: estado de cuenta y lista de facturas paginada:

#### **Sección: Estado de Cuenta**
- **Componente:** Tarjeta con información resumida
- **Propósito:** Mostrar última factura y estado general
- **Features:** 
  - Última fecha y monto de factura
  - Botón de actualización con animación
  - Toggle para mostrar/ocultar facturas
  - Loading states durante carga

#### **Sección: Lista de Facturas**
- **Componente:** Lista paginada con navegación avanzada
- **Propósito:** Mostrar todas las facturas disponibles
- **Features:** 
  - Paginación responsiva (6 facturas por página)
  - Navegación con ellipsis para muchas páginas
  - Descarga individual de PDFs
  - Estados de carga y error

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
// Datos de facturas
public facturas: (IFactura & { disabled?: boolean })[] = [];
public paginatedFacturas: (IFactura & { disabled?: boolean })[] = [];
public lastPayment: { date: string; monto: number } | undefined;

// Estados de paginación
public paginaActual = 1;
public facturasPorPagina = 6;
public totalPaginas: number[] = [];
public paginasVisibles: (number | string)[] = [];

// Estados de UI
public loading = true;
public showFacturas: boolean = false;
public isOpenDownloading: boolean = false;
public progressDownloading: number = 0;
```

#### **Carga de Facturas**
```typescript
public loadFacturas(force: boolean = false) {
  this.loading = true;
  this.facturas = [];
  
  if (this.facturasSubscription) {
    this.facturasSubscription.unsubscribe();
  }
  
  this.facturasSubscription = this.facturaService.GetFacturas(force).subscribe(facturas => {
    this.facturas = facturas;
    
    this.user.GetUserPromise().then(user => {
      if (!user) throw new Error('Usuario no autenticado!');
      
      this.loading = false;
      
      if (facturas.length > 0) {
        this.lastPayment = {
          date: new Date(facturas[0].fecha_factura).toLocaleDateString(),
          monto: facturas[0].neto_bs,
        };
      }
      
      this.facturas = facturas;
      this.ordenarFacturas();
      this.calcularTotalPaginas();
      this.actualizarPaginas();
      this.calcularPaginasVisibles(window.innerWidth);
    });
  });
}
```

### 3.2 Sistema de Paginación Avanzada

#### **Cálculo de Páginas Visibles**
```typescript
calcularPaginasVisibles(width: number) {
  const totalPages = this.totalPaginas.length;

  if (width < 640) {
    this.paginasVisibles = this.calcularRangoPaginas();
  } else if (width < 1024) {
    this.paginasVisibles = this.calcularRangoPaginas();
  } else {
    this.paginasVisibles = this.totalPaginas; // Display all pages on large screens
  }
}

calcularRangoPaginas(): (number | string)[] {
  const totalPages = this.totalPaginas.length;
  const currentPage = this.paginaActual;

  if (totalPages <= 3) {
    return this.totalPaginas;
  }

  if (currentPage === 1) {
    return [1, 2, '...', totalPages];
  }

  if (currentPage === totalPages) {
    return [1, '...', totalPages - 1, totalPages];
  }

  return [1, currentPage, '...', totalPages];
}
```

#### **Navegación de Páginas**
```typescript
cambiarPagina(pagina: number | string) {
  if (typeof pagina === 'number') {
    this.paginaActual = pagina;
    this.actualizarPaginas();
    this.calcularPaginasVisibles(window.innerWidth);
    this.scrollToTop();
  }
}

actualizarPaginas() {
  const startIndex = (this.paginaActual - 1) * this.facturasPorPagina;
  const endIndex = startIndex + this.facturasPorPagina;
  this.paginatedFacturas = this.facturas.slice(startIndex, endIndex);
}
```

---

## 4. Gestión de Archivos y Descargas

### 4.1 Sistema de Descarga Híbrido

#### **Lógica Multi-Plataforma**
```typescript
DownloadPaymentBill(nro_documento: string) {
  return new Promise<void>((resolve, reject) => {
    this.isOpenDownloading = true;
    
    this.dialog.showLoader({
      mode: 'ios',
      spinner: 'circular',
      message: 'Obteniendo factura...',
    }).then(loading => {
      this.facturaService.DownloadFactura(nro_documento)
        .then(factura => {
          if (factura) {
            if (this.platform.is('hybrid')) {
              // Native (Android/iOS) logic
              return Filesystem.writeFile({
                path: 'Fibex Oficina Movil/factura_' + nro_documento + '.pdf',
                data: factura.archivo,
                directory: Directory.Documents,
                recursive: true,
              }).then(writeResult =>
                FileOpener.open({
                  filePath: writeResult.uri,
                  contentType: 'application/pdf',
                })
              );
            } else {
              // Web logic
              const byteCharacters = atob(factura.archivo);
              const byteNumbers = new Array(byteCharacters.length);
              for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
              }
              const byteArray = new Uint8Array(byteNumbers);
              const blob = new Blob([byteArray], { type: 'application/pdf' });
              const url = window.URL.createObjectURL(blob);

              const a = document.createElement('a');
              a.href = url;
              a.download = `factura_${nro_documento}.pdf`;
              document.body.appendChild(a);
              a.click();
              document.body.removeChild(a);
              window.URL.revokeObjectURL(url);
              return Promise.resolve();
            }
          }
        })
        .finally(() => {
          loading?.dismiss();
          this.isOpenDownloading = false;
        });
    });
  });
}
```

---

## 5. Componentes Compartidos Integrados

### 5.1 Componente Principal

#### **ContentHeaderComponent**
- **Ruta:** `importsComponents/headers/content-header/content-header.component`
- **Propósito:** Header estándar con título y navegación
- **Features:** 
  - Título "Facturas"
  - Botón de retroceso
  - Layout consistente con otras páginas

### 5.2 Estructura de Template

#### **Tarjeta de Estado de Cuenta**
```html
<div class="estado-cuenta-card">
  <h2 class="estado-cuenta-header">
    <i class="fas fa-wallet mr-2"></i> Estado de Cuenta
    <button class="button" [ngClass]="{'loading': loading}" (click)="loadFacturas(true)">
      <!-- Refresh icon -->
    </button>
  </h2>
  <p class="estado-cuenta-fecha">
    Última Fecha factura<br />
    <span>{{ lastPayment?.date || "No disponible" }}</span>
  </p>
  <p class="estado-cuenta-monto">
    Último monto factura<br />
    <span>{{ lastPayment?.monto || "No disponible" }} {{ lastPayment?.monto ? "bs" : "" }}</span>
  </p>
</div>
```

#### **Lista de Facturas Paginada**
```html
<div class="lista-recibos">
  <div class="lista-recibos-card">
    <p class="lista-recibos-header">
      <span class="fas fa-file-invoice mr-2">Mis facturas</span>
    </p>
    <ul class="lista-recibos-items">
      @for (facturaItem of paginatedFacturas; track $index) {
        <li class="lista-recibo-item">
          <div class="lista-recibo-info">
            <div class="info-first-items">
              <span class="text-md">N°-{{ facturaItem.nro_factura }}</span>
              <span class="text-xs">{{ facturaItem.fecha_factura }}</span>
            </div>
            <div class="flex gap-0 md:gap-8 lg:gap-12 items-start">
              <span class="text-sm">{{ facturaItem.neto_bs }}bs</span>
              <button class="recibo-boton" (click)="DownloadPaymentBill(facturaItem.nro_factura)">
                <ion-icon name="download"></ion-icon>
              </button>
            </div>
          </div>
        </li>
      }
    </ul>
  </div>
</div>
```

---

## 6. Integración con Servicios

### 6.1 Servicios Principales

#### **FacturasService**
- **Propósito:** Gestión centralizada de facturas
- **Métodos clave:** `GetFacturas()`, `DownloadFactura()`, `DownloadEstadoCuenta()`
- **Flujo:** Observable para lista de facturas, Promise para descargas
- **Datos:** Array de facturas con información completa

#### **UserService**
- **Propósito:** Gestión de datos de usuario
- **Métodos clave:** `GetUserPromise()`
- **Uso:** Validación de autenticación y datos de usuario

#### **DialogsService**
- **Propósito:** Gestión de modales y notificaciones
- **Métodos clave:** `showLoader()`, `showToast()`
- **Uso:** Indicadores de carga y retroalimentación

#### **NetworkStatusService**
- **Propósito:** Validación de conectividad
- **Métodos clave:** `validateNetworkAccess()`
- **Uso:** Verificación de conexión antes de operaciones

---

## 7. Estilos y Diseño Visual

### 7.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.estado-cuenta-card {
  background: linear-gradient(to right, #2563eb, #1e3a8a);
  color: #ffffff;
  padding: 1.5rem;
  border-radius: 1rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;
}

.lista-recibos-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.lista-recibo-item {
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem;
  transition: all 0.3s ease;
  
  &:hover {
    background-color: #f9fafb;
  }
}
```

#### **Diseño Responsivo**
- **Adaptativo:** Layout se ajusta según tamaño de pantalla
- **Paginación:** Diferente comportamiento en móvil vs desktop
- **Botones:** Tamaño y espaciado adaptativos
- **Tarjetas:** Ancho máximo en desktop, completo en móvil

### 7.2 Animaciones y Transiciones

#### **Loading Animation**
```scss
@keyframes loading-button {
  from {
    transform: rotateZ(0deg);
  }
  to {
    transform: rotateZ(360deg);
  }
}

.button.loading {
  animation-name: loading-button;
  animation-duration: 1s;
  animation-fill-mode: both;
  animation-iteration-count: infinite;
}
```

---

## 8. Flujo de Usuario Detallado

### 8.1 Caminos Principales

#### **Usuario con Facturas Disponibles**
1. Carga inicial con loading indicator
2. Visualización de tarjeta de estado con última factura
3. Click en "Ver mis facturas" para expandir lista
4. Navegación por páginas con paginación avanzada
5. Descarga individual de facturas en PDF

#### **Usuario sin Facturas**
1. Carga inicial con loading indicator
2. Tarjeta de estado con "No disponible"
3. Lista vacía con mensaje apropiado
4. Opción de actualizar datos

#### **Descarga de Facturas**
1. Click en botón de descarga de factura específica
2. Loading indicator durante procesamiento
3. Detección automática de plataforma (nativo vs web)
4. Descarga y apertura del PDF según plataforma
5. Retroalimentación de éxito o error

### 8.2 Estados de Error y Recuperación

- **Factura No Disponible:** Deshabilitar botón específico, mostrar toast
- **Error de Red:** Reintentar automáticamente, mostrar mensaje
- **Error de Descarga:** Retroalimentación clara con opción de reintentar
- **Error de Archivo:** Manejo de errores de filesystem o blob

---

## 9. Consideraciones de Performance

### 9.1 Optimizaciones Implementadas

1. **Lazy Loading:** Facturas cargadas bajo demanda
2. **Pagination:** División de datos para mejor rendimiento
3. **Subscription Management:** Cleanup apropiado de observables
4. **Responsive Pagination:** Cálculo adaptativo de páginas visibles

### 9.2 Manejo de Memoria

```typescript
ionViewWillLeave(): void {
  if (this.facturasSubscription) {
    this.facturasSubscription.unsubscribe();
    this.facturasSubscription = undefined;
  }
}
```

---

## 10. Testing y Calidad

### 10.1 Casos de Uso Críticos

1. **Carga inicial de facturas**
2. **Paginación avanzada con ellipsis**
3. **Descarga nativa de PDFs**
4. **Descarga web de PDFs**
5. **Responsive design móvil/desktop**
6. **Manejo de errores de descarga**
7. **Actualización de datos**
8. **Empty states sin facturas**

### 10.2 Pruebas Unitarias Requeridas

- Carga y ordenamiento de facturas
- Cálculo de paginación
- Navegación entre páginas
- Descarga de archivos (mock)
- Manejo de estados de carga
- Responsive behavior
- Error handling

---

## 11. Consideraciones de Seguridad

### 11.1 Manejo de Datos Sensibles

- **Validación de Usuario:** Verificación de autenticación antes de descargas
- **Sanitización de Datos:** Manejo seguro de datos base64
- **File System Security:** Paths controlados y validados
- **Blob Security:** Creación segura de objetos URL

### 11.2 Validaciones de Entrada

- **Número de Factura:** Validación de formato antes de descarga
- **File Paths:** Validación de paths para filesystem
- **Platform Detection:** Verificación segura de plataforma
- **Network Status:** Validación de conectividad

---

## 12. APIs y Servicios Externos

### 12.1 Capacitor Filesystem API

- **URL:** https://capacitorjs.com/docs/apis/filesystem
- **Propósito:** Acceso nativo al sistema de archivos
- **Uso en la aplicación:** 
  - Guardar PDFs descargados en Documents folder
  - Creación recursiva de directorios
  - Manejo de paths cross-platform
- **Características:** 
  - Soporte para Android, iOS, Web
  - APIs consistentes across platforms
  - Manejo de permisos automático

### 12.2 Capacitor File Opener API

- **URL:** https://github.com/capacitor-community/file-opener
- **Propósito:** Apertura de archivos en aplicaciones nativas
- **Uso en la aplicación:** 
  - Abrir PDFs descargados en visor nativo
  - Manejo de content types
  - Integración con filesystem API
- **Características:** 
  - Soporte para múltiples formatos
  - Integración con apps nativas
  - Cross-platform compatibility

---

## 13. Componentes y Código Destacable

### 13.1 Sistema de Paginación Responsiva

```typescript
@HostListener('window:resize', ['$event'])
onResize(event: any) {
  this.calcularPaginasVisibles(event.target.innerWidth);
}

calcularRangoPaginas(): (number | string)[] {
  const totalPages = this.totalPaginas.length;
  const currentPage = this.paginaActual;

  if (totalPages <= 3) {
    return this.totalPaginas;
  }

  if (currentPage === 1) {
    return [1, 2, '...', totalPages];
  }

  if (currentPage === totalPages) {
    return [1, '...', totalPages - 1, totalPages];
  }

  return [1, currentPage, '...', totalPages];
}
```

**Características:**
- Detección automática de cambios de tamaño
- Lógica de ellipsis para muchas páginas
- Comportamiento diferente por breakpoint
- Optimización para mobile vs desktop

### 13.2 Descarga Híbrida Multi-Plataforma

```typescript
if (this.platform.is('hybrid')) {
  // Native (Android/iOS) logic
  return Filesystem.writeFile({
    path: 'Fibex Oficina Movil/factura_' + nro_documento + '.pdf',
    data: factura.archivo,
    directory: Directory.Documents,
    recursive: true,
  }).then(writeResult =>
    FileOpener.open({
      filePath: writeResult.uri,
      contentType: 'application/pdf',
    })
  );
} else {
  // Web logic
  const byteCharacters = atob(factura.archivo);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  // ... download logic
}
```

**Características:**
- Detección automática de plataforma
- Conversión de base64 a binario
- Manejo de filesystem nativo
- Descarga web con blob URLs

### 13.3 Gestión de Estados con Animaciones

```scss
.button {
  border: none;
  background-color: none;
  cursor: pointer;
  float: right;
  padding: 10px;
  border-radius: 100%;
  transition: all 0.3s ease;

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  &.loading {
    animation-name: loading-button;
    animation-duration: 1s;
    animation-iteration-count: infinite;
  }
}
```

**Características:**
- Animación de rotación durante carga
- Estados hover y active
- Feedback visual claro
- Transiciones suaves

---

## 14. Mejoras Futuras Sugeridas

### 14.1 Features Potenciales

1. **Bulk Download:** Descarga múltiple de facturas
2. **Email Sending:** Envío de facturas por email
3. **Advanced Filtering:** Filtros por fecha, monto, estado
4. **Search Functionality:** Búsqueda rápida de facturas
5. **Offline Mode:** Cache de facturas para acceso offline

### 14.2 Optimizaciones Técnicas

1. **Virtual Scrolling:** Para grandes cantidades de facturas
2. **Progressive Loading:** Carga progresiva de páginas
3. **Background Sync:** Sincronización en segundo plano
4. **Compression:** Compresión de PDFs para descarga más rápida
5. **Caching Strategy:** Cache inteligente de facturas descargadas

---

## 15. Notas para Mantenimiento

### 15.1 Puntos Críticos

1. **Platform Detection:** Mantener compatibilidad cross-platform
2. **File System Paths:** Validar paths en diferentes sistemas
3. **Pagination Logic:** Mantener consistencia en cálculos
4. **Subscription Management:** Proper cleanup para evitar memory leaks
5. **Error Handling:** Manejo robusto de errores de red y filesystem

### 15.2 Buenas Prácticas

- Mantener validación de usuario antes de descargas
- Implementar proper error handling para filesystem
- Validar todos los datos de facturas
- Documentar cambios en APIs externas
- Realizar testing cross-platform regularmente

---

## 16. Conclusión

La Payment Bill Page representa un componente esencial en la arquitectura de Oficina Móvil para la gestión documental financiera. Su implementación con sistema de paginación avanzada, descarga híbrida multi-plataforma y manejo robusto de estados la convierten en una solución completa para la gestión de facturas Fibex.

La arquitectura modular, la integración con Capacitor para funcionalidades nativas y el manejo inteligente de archivos proporcionan una base sólida para futuras mejoras como descargas bulk, filtros avanzados y sincronización offline. Su diseño actual ofrece una experiencia de usuario consistente y eficiente tanto en plataformas móviles como web.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
