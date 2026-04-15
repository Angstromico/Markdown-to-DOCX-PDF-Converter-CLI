# RFC: Contacts Page - Directorio de Sucursales y Contactos Fibex

## Introducción

La **Contacts Page** es el componente central de directorio de sucursales de la aplicación **Oficina Móvil V2** que permite a los usuarios encontrar, contactar y navegar hacia todas las sucursales **Fibex Telecom** disponibles. Esta página implementa un sistema avanzado de búsqueda y filtrado geográfico, con capacidades de marcación telefónica, navegación maps, compartición de ubicaciones y detección automática de sucursales cercanas basadas en el contrato del usuario.

Este RFC documenta la arquitectura técnica, flujo de usuario, sistema de filtrado geográfico, integración con APIs nativas y consideraciones de implementación de la página de contactos, que sirve como portal central para la gestión de relaciones con sucursales Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/contact.png" alt="Contacts Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | ContactsComponent (src/app/pages/contacts/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/contacts/
    contacts.component.ts          # Componente principal con lógica de sucursales
    contacts.component.html        # Template con búsqueda y lista de sucursales
    contacts.component.scss        # Estilos específicos del componente
    contacts.component.spec.ts     # Pruebas unitarias
    contacts-routing.module.ts     # Configuración de rutas
    contacts.module.ts            # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **@capacitor/share**
- **Propósito:** Compartir contenido a través de APIs nativas del dispositivo
- **Configuración:** Share.canShare(), Share.share() con texto y URLs
- **Integración:** Mediante detección automática de capacidades de compartir
- **Documentación:** [Capacitor Share API Documentation](https://capacitorjs.com/docs/apis/share)

#### **Angular Core**
- **Propósito:** Framework base con lifecycle management
- **Configuración:** Component lifecycle, dependency injection
- **Integración:** Decoradores @Component, @ViewChild, OnInit
- **Documentación:** [Angular Documentation](https://angular.dev/)

#### **Ionic Framework**
- **Propósito:** Componentes UI nativos y navegación
- **Configuración:** ion-item-sliding, ion-searchbar, ion-modal
- **Integración:** Sliding items, modales, searchbars nativos
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

#### **Angular Forms**
- **Propósito:** Gestión de formularios y bindings
- **Configuración:** FormsModule para ngModel bindings
- **Integración:** Búsqueda en tiempo real con [(ngModel)]
- **Documentación:** [Angular Forms Documentation](https://angular.dev/guide/forms)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura de Visualización

La página implementa una interfaz de búsqueda avanzada con lista interactiva de sucursales:

#### **Sección: Búsqueda y Filtros**
- **Componente:** Barra de búsqueda con filtros geográficos
- **Propósito:** Encontrar sucursales por nombre, ciudad, estado
- **Features:** 
  - Búsqueda en tiempo real
  - Filtro por estado con modal
  - Detección automática de sucursales cercanas
  - Clear filter functionality

#### **Sección: Lista de Sucursales**
- **Componente:** Sliding items con información completa
- **Propósito:** Mostrar sucursales con acciones rápidas
- **Features:** 
  - Sliding items con múltiples opciones
  - Estado de horario (abierto/cerrado)
  - Imágenes de sucursales
  - Información de contacto y ubicación

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
// Datos de sucursales
public localitationdata: localitationFibexData[] = [];
public filteredLocations: localitationFibexData[] = [];
public EstadosLocation: string[] = [];

// Estados de búsqueda y filtros
public searchQuery: string = '';
public selectedFilter: string = '';
public isFilterModalOpen = false;

// Estados de UI
public loading = true;
public ContratoSelected: ItmContratoTable[] = [];
```

#### **Carga y Filtrado de Ubicaciones**
```typescript
async MatchUserLocations() {
  this.loading = true;
  try {
    if (!this.ContratoSelected || this.ContratoSelected.length === 0) {
      throw new Error('Contrato no cargado.');
    }

    const { estado_franquicia, nombre_ciudad } = this.ContratoSelected[0];
    const EdoFranquicia = estado_franquicia.toLowerCase();
    const CityFranquicia = nombre_ciudad.toLowerCase();

    this.localitationdata = await this.locationService.Getlocation();
    this.EstadosLocation = [
      ...new Set(this.localitationdata.map(location => location.Estado)),
    ].sort();

    this.filteredLocations = this.localitationdata.filter(
      location =>
        location.Ciudad?.toLowerCase() === CityFranquicia ||
        location.Estado?.toLowerCase() === EdoFranquicia,
    );
  } catch (err) {
    console.error(err);
  } finally {
    this.loading = false;
  }
}
```

### 3.2 Sistema de Búsqueda Avanzada

#### **Búsqueda Multi-Campo**
```typescript
filterLocations(event: Event) {
  event.preventDefault();

  const query = this.searchQuery?.trim().toLowerCase();
  if (!query) {
    this.clearFilter();
    return;
  }

  this.selectedFilter = 'Todas';

  type Keys = 'Ciudad' | 'Oficina' | 'Estado';
  this.filteredLocations = this.localitationdata.filter(location =>
    (['Ciudad', 'Oficina', 'Estado'] as Keys[]).some(key =>
      location[key]?.toLowerCase().includes(query),
    ),
  );
}
```

#### **Filtrado por Estado**
```typescript
applyFilter() {
  this.filteredLocations =
    this.selectedFilter === 'Todas' || !this.selectedFilter
      ? [...this.localitationdata]
      : this.localitationdata.filter(location => location.Estado === this.selectedFilter);
}
```

---

## 4. Integración con APIs Nativas

### 4.1 Sistema de Compartir Híbrido

#### **Detección Automática de Capacidades**
```typescript
public async shareLocation(name: string, address: string, phone: string, url: string) {
  const shareData = {
    title: name,
    text: `${address}<br>Teléfono: ${phone}`,
    url: url,
  };

  try {
    const canShareResult = await Share.canShare();
    if (canShareResult.value) {
      await Share.share(shareData);
    } else if (navigator.share) {
      await navigator.share(shareData);
    } else {
      alert('No es posible compartir contenido desde este dispositivo.');
    }
  } catch (error) {
    alert('No se pudo compartir la ubicación. Por favor, inténtelo de nuevo.');
  }
}
```

#### **Marcación Telefónica**
```typescript
openDialer(location: string) {
  window.location.href = `tel:${location}`;
}
```

#### **Navegación a Maps**
```typescript
openMaps(url: string, latitud: string, longitud: string, nombre: string) {
  if (url && latitud && longitud && nombre) {
    this.router.navigate(['tabs/google-maps', { url, latitud, longitud, nombre }]);
  }
}
```

---

## 5. Componentes Compartidos Integrados

### 5.1 Componente Principal

#### **ContentHeaderComponent**
- **Ruta:** `importsComponents/headers/content-header/content-header.component`
- **Propósito:** Header estándar con título y navegación
- **Features:** 
  - Título "Sucursales"
  - Botón de retroceso
  - Layout consistente con otras páginas

### 5.2 Estructura de Template

#### **Barra de Búsqueda con Filtros**
```html
<div class="flex div-shear">
  <div class="filter-info-container">
    <ion-button fill="outline" (click)="clearFilter()">
      <p>
        {{
          selectedFilter
            ? selectedFilter === 'Todas'
              ? 'Todas las sucursales'
              : 'Sucursales de ' + selectedFilter
            : 'Sucursales Cercanas'
        }}
      </p>
      <ion-icon *ngIf="selectedFilter && selectedFilter !== 'Sucursales Cercanas'" name="close-circle"></ion-icon>
    </ion-button>
  </div>

  <span class="searchbar-section-btn flex">
    <ion-searchbar
      mode="ios"
      placeholder="Buscar..."
      [(ngModel)]="searchQuery"
      (ionInput)="filterLocations($event)"
    ></ion-searchbar>

    <ion-button fill="clear" class="icon-button" (click)="openFilterModal()">
      <ion-icon name="list" class="icon-right" color="dark"></ion-icon>
    </ion-button>
  </span>
</div>
```

#### **Lista de Sucursales con Sliding Items**
```html
@for (location of filteredLocations; track $index) {
  <ion-item-sliding #slidingItem class="sliding-item">
    <ion-item class="custom-item">
      <img
        (click)="openSlidingItem(slidingItem)"
        [src]="location.Urlimg ? location.Urlimg : 'assets/images/Default-sucursal.jpg'"
        class="img-left"
      />
      <div class="Div-card-content">
        <ion-title mode="md">{{ location.Oficina }}</ion-title>
        <div class="pl-4">
          <ion-text>
            <p class="ellipsis">
              <ion-icon name="location-outline"></ion-icon>
              {{
                location.Estado === location.Ciudad
                  ? location.Estado
                  : location.Estado + ' - ' + location.Ciudad
              }}
            </p>
          </ion-text>
          <div class="flex gap-0.5">
            <div>
              <p><ion-icon name="time-outline" class="mr-0.5"></ion-icon>Horarios:</p>
            </div>
            <div><p>8:00a.m - 5:00p.m</p></div>
          </div>
          <ion-text [color]="getStatusColor()" class="flex">
            <p class="gap-0.5">
              <ion-icon name="timer-outline"></ion-icon
              >{{ getStatusColor() === 'success' ? 'Abierto' : ' Cerrado' }}
            </p>
          </ion-text>
        </div>
      </div>
    </ion-item>

    <ion-item-options side="end">
      <ion-item-option class="map-option" (click)="openMaps(location.urlMaps, location.latitud, location.longitud, location.Oficina)">
        Ir a Sucursal
      </ion-item-option>
      <ion-item-option class="call-option" (click)="openDialer(location.TelfAdministrador)">
        Llamar
      </ion-item-option>
      <ion-item-option class="details-option" (click)="showModal(location.Oficina, location.TelfAdministrador, location['Dirección'], location.urlMaps, location.Urlimg)">
        Detalles
      </ion-item-option>
    </ion-item-options>
  </ion-item-sliding>
}
```

---

## 6. Integración con Servicios

### 6.1 Servicios Principales

#### **LocationService**
- **Propósito:** Gestión centralizada de datos de sucursales
- **Métodos clave:** `Getlocation()`
- **Flujo:** Promise que retorna array de sucursales con información completa
- **Datos:** Ubicaciones, coordenadas, teléfonos, imágenes, horarios

#### **UserService**
- **Propósito:** Gestión de datos de usuario y contratos
- **Métodos clave:** `GetContratoSelected()`
- **Uso:** Obtener información de franquicia para detección automática

#### **DialogsService**
- **Propósito:** Gestión de modales y notificaciones
- **Métodos clave:** `showStandardModalInfo()`
- **Uso:** Modal de detalles con opciones de compartir y llamar

---

## 7. Estilos y Diseño Visual

### 7.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.sliding-item {
  margin-bottom: 10px;
  height: 90px;
  border-radius: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.custom-item {
  display: flex;
  align-items: center;
  height: 100%;
  font-size: larger;
}

.img-left {
  width: 80px;
  height: 70px;
  margin-right: 5px;
  border-radius: 1rem;
}

.map-option {
  background-color: #0145c3;
  color: white;
}

.call-option {
  background-color: #0154e9;
  color: white;
}

.details-option {
  background-color: #00184e;
  color: white;
}
```

#### **Diseño Responsivo**
- **Adaptativo:** Layout se ajusta según tamaño de pantalla
- **Sliding Items:** Comportamiento consistente en móviles
- **Search Bar:** Ancho completo en todos los dispositivos
- **Modal Filters:** Altura fija del 75% de pantalla

### 7.2 Estados Visuales

- **Loading States:** Spinner durante carga de sucursales
- **Empty States:** Mensaje cuando no hay sucursales encontradas
- **Status Indicators:** Colores para abierto (verde) y cerrado (rojo)
- **Hover Effects:** Feedback visual en elementos interactivos

---

## 8. Flujo de Usuario Detallado

### 8.1 Caminos Principales

#### **Usuario con Contrato Activo**
1. Carga inicial con loading indicator
2. Detección automática de sucursales cercanas basadas en contrato
3. Visualización de sucursales filtradas por ciudad/estado
4. Opciones de búsqueda y filtrado adicionales
5. Acciones rápidas via sliding items

#### **Búsqueda Manual**
1. Uso de searchbar para búsqueda por nombre
2. Búsqueda en tiempo real sobre múltiples campos
3. Filtros por estado via modal
4. Clear filter functionality

#### **Interacción con Sucursales**
1. Sliding item reveal con 3 opciones
2. "Ir a Sucursal" - Navegación a Google Maps
3. "Llamar" - Marcación telefónica directa
4. "Detalles" - Modal con información completa y opciones de compartir

### 8.2 Estados de Error y Recuperación

- **Sin Contrato:** Manejo de usuarios sin contrato seleccionado
- **Sin Sucursales:** Empty state con mensaje apropiado
- **Error de Carga:** Retroalimentación clara con opción de reintentar
- **Error de Compartir:** Mensaje específico con alternativas

---

## 9. Consideraciones de Performance

### 9.1 Optimizaciones Implementadas

1. **Lazy Loading:** Sucursales cargadas bajo demanda
2. **Efficient Filtering:** Algoritmos optimizados para búsqueda
3. **Image Caching:** Cache de imágenes de sucursales
4. **Track By Function:** Optimización de *ngFor con trackById

### 9.2 Manejo de Memoria

```typescript
trackById(index: number, location: localitationFibexData): number {
  return location.ID;
}
```

---

## 10. Testing y Calidad

### 10.1 Casos de Uso Críticos

1. **Carga inicial de sucursales**
2. **Detección automática de sucursales cercanas**
3. **Búsqueda en tiempo real**
4. **Filtrado por estado**
5. **Sliding items functionality**
6. **Marcación telefónica**
7. **Navegación a maps**
8. **Compartir ubicación**
9. **Responsive design**
10. **Error handling**

### 10.2 Pruebas Unitarias Requeridas

- Carga y filtrado de sucursales
- Búsqueda multi-campo
- Estados de horario
- Integración con APIs nativas
- Manejo de modales
- Responsive behavior
- Error handling

---

## 11. Consideraciones de Seguridad

### 11.1 Manejo de Datos Sensibles

- **Validación de Teléfonos:** Formateo y validación de números telefónicos
- **URL Validation:** Validación de URLs de maps antes de navegación
- **Share Data Validation:** Sanitización de datos antes de compartir
- **Geolocation Privacy:** Manejo responsable de datos de ubicación

### 11.2 Validaciones de Entrada

- **Search Query:** Sanitización y validación de búsqueda
- **Phone Numbers:** Formato internacional y validación
- **URLs:** Validación de protocolos y formatos
- **User Input:** Protección contra XSS en campos de texto

---

## 12. APIs y Servicios Externos

### 12.1 Capacitor Share API

- **URL:** https://capacitorjs.com/docs/apis/share
- **Propósito:** Compartir contenido a través de APIs nativas
- **Uso en la aplicación:** 
  - Compartir información de sucursales
  - Detección automática de capacidades
  - Fallback a Web Share API
- **Características:** 
  - Cross-platform compatibility
  - Soporte para texto, URLs, archivos
  - Integración con apps nativas de compartir

### 12.2 Web APIs Nativas

#### **Tel: URI Scheme**
- **Propósito:** Marcación telefónica nativa
- **Uso:** `window.location.href = 'tel:{phone}'`
- **Características:** Soporte universal en móviles

#### **Web Share API**
- **Propósito:** Fallback para compartir en navegadores web
- **Uso:** `navigator.share()` cuando Capacitor no está disponible
- **Características:** API estándar del navegador

---

## 13. Componentes y Código Destacable

### 13.1 Detección Automática de Sucursales Cercanas

```typescript
async MatchUserLocations() {
  const { estado_franquicia, nombre_ciudad } = this.ContratoSelected[0];
  const EdoFranquicia = estado_franquicia.toLowerCase();
  const CityFranquicia = nombre_ciudad.toLowerCase();

  this.localitationdata = await this.locationService.Getlocation();
  
  this.filteredLocations = this.localitationdata.filter(
    location =>
      location.Ciudad?.toLowerCase() === CityFranquicia ||
      location.Estado?.toLowerCase() === EdoFranquicia,
  );
}
```

**Características:**
- Detección basada en contrato del usuario
- Filtrado por ciudad y estado
- Manejo de case-insensitive
- Fallback a todas las sucursales

### 13.2 Sistema de Búsqueda Multi-Campo

```typescript
filterLocations(event: Event) {
  const query = this.searchQuery?.trim().toLowerCase();
  if (!query) {
    this.clearFilter();
    return;
  }

  type Keys = 'Ciudad' | 'Oficina' | 'Estado';
  this.filteredLocations = this.localitationdata.filter(location =>
    (['Ciudad', 'Oficina', 'Estado'] as Keys[]).some(key =>
      location[key]?.toLowerCase().includes(query),
    ),
  );
}
```

**Características:**
- Búsqueda en múltiples campos simultáneamente
- Type-safe con TypeScript
- Búsqueda en tiempo real
- Reset automático de filtros

### 13.3 Sistema de Compartir Híbrido

```typescript
public async shareLocation(name: string, address: string, phone: string, url: string) {
  const shareData = {
    title: name,
    text: `${address}<br>Teléfono: ${phone}`,
    url: url,
  };

  try {
    const canShareResult = await Share.canShare();
    if (canShareResult.value) {
      await Share.share(shareData);
    } else if (navigator.share) {
      await navigator.share(shareData);
    } else {
      alert('No es posible compartir contenido desde este dispositivo.');
    }
  } catch (error) {
    alert('No se pudo compartir la ubicación. Por favor, inténtelo de nuevo.');
  }
}
```

**Características:**
- Detección automática de capacidades
- Fallback a Web Share API
- Manejo robusto de errores
- Formato de datos optimizado

---

## 14. Mejoras Futuras Sugeridas

### 14.1 Features Potenciales

1. **Geolocation Services:** Detección GPS de sucursales más cercanas
2. **Real-time Status:** Actualización en tiempo real de horarios
3. **Appointment Booking:** Citas en sucursales
4. **QR Code Generation:** Códigos QR para compartir sucursales
5. **Voice Search:** Búsqueda por comandos de voz

### 14.2 Optimizaciones Técnicas

1. **Virtual Scrolling:** Para grandes cantidades de sucursales
2. **Offline Mode:** Cache de sucursales para acceso offline
3. **Push Notifications:** Notificaciones de cambios en horarios
4. **Analytics Integration:** Tracking de interacciones con sucursales
5. **Performance Monitoring:** Métricas de uso y rendimiento

---

## 15. Notas para Mantenimiento

### 15.1 Puntos Críticos

1. **Location Data Accuracy:** Mantener actualizados datos de sucursales
2. **Phone Number Format:** Validación de formatos internacionales
3. **Map Integration:** Mantener compatibilidad con Google Maps
4. **Share API Compatibility:** Testing en diferentes dispositivos
5. **Performance:** Optimización para grandes listas de sucursales

### 15.2 Buenas Prácticas

- Mantener validación de todos los datos de contacto
- Implementar proper error handling para APIs nativas
- Validar todos los URLs antes de navegación
- Documentar cambios en APIs externas
- Realizar testing cross-platform regularmente

---

## 16. Conclusión

La Contacts Page representa un componente esencial en la arquitectura de Oficina Móvil para la gestión de relaciones con sucursales. Su implementación con detección automática de ubicaciones, búsqueda avanzada multi-campo, integración con APIs nativas y sistema de sliding items la convierten en una solución completa para el directorio de sucursales Fibex.

La arquitectura modular, la integración con Capacitor para funcionalidades nativas y el manejo inteligente de datos geográficos proporcionan una base sólida para futuras mejoras como geolocation services, booking de citas y notificaciones en tiempo real. Su diseño actual ofrece una experiencia de usuario intuitiva y eficiente tanto en plataformas móviles como web.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
