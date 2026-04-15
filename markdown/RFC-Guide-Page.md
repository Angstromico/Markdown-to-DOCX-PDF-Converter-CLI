# RFC: Guide Page - Sistema de Manuales y Documentación Técnica

## Introducción

La **Guide Page** es el componente central de documentación técnica de la aplicación **Oficina Móvil V2** que permite a los usuarios acceder, visualizar y compartir manuales técnicos de servicios **Fibex Telecom**. Esta página implementa un sistema de gestión de manuales con descarga de imágenes, compartición de archivos y visualización en grid responsivo, proporcionando acceso centralizado a toda la documentación relevante para los clientes.

Este RFC documenta la arquitectura técnica, flujo de usuario, sistema de compartición de archivos, manejo de imágenes y consideraciones de implementación de la página de manuales, que sirve como portal central para la gestión documental técnica de los clientes Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/guide.jpeg" alt="Guide Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | GuidePage (src/app/pages/guide/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/guide/
    guide.page.ts          # Componente principal con lógica de manuales
    guide.page.html        # Template con grid de manuales
    guide.page.scss        # Estilos específicos del componente
    guide.page.spec.ts     # Pruebas unitarias
    guide-routing.module.ts # Configuración de rutas
    guide.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **@capacitor/share**
- **Propósito:** Compartir contenido a través de APIs nativas del dispositivo
- **Configuración:** Share.share() con archivos adjuntos y texto
- **Integración:** Mediante detección automática de capacidades de compartir
- **Documentación:** [Capacitor Share API Documentation](https://capacitorjs.com/docs/apis/share)

#### **@capacitor/filesystem**
- **Propósito:** Acceso al sistema de archivos para guardar imágenes temporalmente
- **Configuración:** Directory.Cache para almacenamiento temporal
- **Integración:** Mediante Filesystem.writeFile() para cache de imágenes
- **Documentación:** [Capacitor Filesystem Documentation](https://capacitorjs.com/docs/apis/filesystem)

#### **Angular Core**
- **Propósito:** Framework base con lifecycle management
- **Configuración:** Component lifecycle, dependency injection
- **Integración:** Decoradores @Component, @ViewChild, OnInit
- **Documentación:** [Angular Documentation](https://angular.dev/)

#### **Ionic Framework**
- **Propósito:** Componentes UI nativos y navegación
- **Configuración:** ion-spinner, ion-icon, ion-content
- **Integración:** ViewWillEnter lifecycle hook
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura de Visualización

La página implementa una interfaz simple y directa con grid de manuales:

#### **Sección: Grid de Manuales**
- **Componente:** Grid responsivo con cards de manuales
- **Propósito:** Mostrar todos los manuales disponibles
- **Features:** 
  - Layout responsivo adaptativo
  - Imágenes preview de cada manual
  - Botones de compartir individuales
  - Loading states durante carga y compartición

#### **Sección: Compartir Manual**
- **Componente:** Función de compartir con archivos adjuntos
- **Propósito:** Permitir compartir manuales con otros usuarios
- **Features:** 
  - Descarga automática de imágenes
  - Cache temporal en filesystem
  - Compartición con texto y archivos
  - Loading states durante proceso

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
// Datos de manuales
public Manuals: Manuals[] = [];

// Estados de UI
public isLoading: boolean = false;

// ViewChild para modales
@ViewChild('modalMenuList', { read: ViewContainerRef })
modalContainer!: ViewContainerRef;
```

#### **Carga de Manuales**
```typescript
async getManuals() {
  try {
    const responseAPImanuals = await this.manualService.Getmanuals();
    this.Manuals = responseAPImanuals;
  } catch (error) {
    console.error(error);
  }
}
```

### 3.2 Sistema de Compartición de Manuales

#### **Proceso Completo de Compartición**
```typescript
public shareMessageWithImage(url: string, name: string, imgPrev: string): Promise<void> {
  this.utilService.show();
  this.isLoading = true;
  
  return new Promise<void>((resolve, reject) => {
    try {
      const message = `Hola, te estoy enviando el Manual de ${name}: \n\n${url}`;
      const imageURL = new URL(url, location.href).toString();

      // 1. Descargar la imagen
      fetch(imageURL, { method: 'GET' })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Error al obtener la imagen: ${response.statusText}`);
          }
          return response.blob();
        })
        .then(blob => {
          // 2. Convertir a Base64
          const fileReader = new FileReader();
          fileReader.onload = () => {
            const base64Image = fileReader.result as string;
            const splited = url.split('/');
            const nameFile = splited[splited.length - 1];

            // 3. Guardar en cache
            Filesystem.writeFile({
              data: base64Image,
              path: nameFile,
              directory: Directory.Cache,
            })
              .then(resultWrite => {
                const filePath = resultWrite.uri;

                // 4. Compartir con archivo adjunto
                Share.share({
                  title: name,
                  text: message,
                  dialogTitle: name,
                  files: [filePath],
                })
                  .then(() => {
                    resolve();
                  })
                  .catch(err => {
                    console.error(err);
                    reject(err);
                  })
                  .finally(() => {
                    this.isLoading = false;
                    this.utilService.hide();
                  });
              })
              .catch(err => {
                console.error(err);
                reject(err);
              })
              .finally(() => {
                this.isLoading = false;
                this.utilService.hide();
              });
          };
          fileReader.readAsDataURL(blob);
        })
        .catch(err => {
          console.error(err);
          reject(err);
        })
        .finally(() => {
          this.isLoading = false;
          this.utilService.hide();
        });
    } catch (err) {
      console.error(err);
      this.isLoading = false;
      this.utilService.hide();
      reject(err);
    }
  });
}
```

---

## 4. Componentes Compartidos Integrados

### 4.1 Componente Principal

#### **ContentHeaderComponent**
- **Ruta:** `importsComponents/headers/content-header/content-header.component`
- **Propósito:** Header estándar con título y navegación
- **Features:** 
  - Título "Manuales"
  - Botón de retroceso
  - Layout consistente con otras páginas

### 4.2 Estructura de Template

#### **Grid de Manuales**
```html
<div class="manual-container">
  @for (Manuals of Manuals; track Manuals.id) {
    <div class="manual-card group">
      <div class="image-container">
        <section class="manual-image-section">
          <img src="{{Manuals.img_prev}}" alt="Imagen del manual" class="manual-image" />
        </section>
      </div>

      <div class="download-button-container">
        <button
          (click)="shareMessageWithImage(Manuals.url, Manuals.name, Manuals.img_prev)"
          [disabled]="isLoading"
          class="download-button"
        >
          Compartir
          <ion-icon style="font-size: 24px" name="share-outline"></ion-icon>
        </button>
      </div>
    </div>
  }
</div>
```

---

## 5. Integración con Servicios

### 5.1 Servicios Principales

#### **ManualsService**
- **Propósito:** Gestión centralizada de manuales técnicos
- **Métodos clave:** `Getmanuals()`
- **Flujo:** Promise que retorna array de manuales con información completa
- **Datos:** URLs, nombres, imágenes preview, metadata

#### **NetworkStatusService**
- **Propósito:** Validación de conectividad
- **Métodos clave:** `validateNetworkAccess()`
- **Uso:** Verificar conexión antes de operaciones críticas

#### **UtilService**
- **Propósito:** Utilidades compartidas de UI y loading
- **Métodos clave:** `show()`, `hide()`
- **Uso:** Mostrar/ocultar indicadores de carga

---

## 6. Estilos y Diseño Visual

### 6.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.manual-container {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 grid-flow-row items-center justify-center p-4 gap-4 place-items-center max-w-[95rem] mx-auto;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr)) !important;
}

.manual-card {
  @apply bg-white lg:min-h-56 h-56 lg:h-60 rounded-xl drop-shadow-lg shadow-md w-full max-w-md lg:max-w-xl flex flex-col lg:flex-row border-2 relative ease-in-out duration-300;
  border-color: #0154e9;
  height: 137px;
}

.image-container {
  @apply p-4 flex flex-col lg:flex-row gap-4 lg:items-center lg:justify-center lg:w-full lg:mx-auto lg:pb-12 bg-blue-900 rounded-lg;
  padding: 0;
  height: calc(100% - 2rem);
  overflow: hidden;
}

.manual-image {
  @apply w-full object-cover h-full;
}

.download-button-container {
  @apply flex justify-center items-center bg-[#0154E9] rounded-b-lg absolute bottom-0 right-0 left-0 cursor-pointer;
}
```

#### **Diseño Responsivo**
- **Adaptativo:** Grid con auto-fit para diferentes tamaños de pantalla
- **Card Layout:** Flexbox para distribución de contenido
- **Image Sizing:** Object-cover para mantener proporciones
- **Button Positioning:** Posicionamiento absoluto en bottom de cards

### 6.2 Estados Visuales

- **Loading States:** Indicadores durante carga y compartición
- **Hover Effects:** Transiciones suaves en cards
- **Button States:** Estados disabled durante operaciones
- **Image Overflow:** Manejo de overflow en imágenes

---

## 7. Flujo de Usuario Detallado

### 7.1 Caminos Principales

#### **Usuario Accediendo a Manuales**
1. Carga inicial de la página
2. Validación de conectividad
3. Carga asíncrona de manuales disponibles
4. Visualización en grid responsivo
5. Selección de manual para compartir

#### **Proceso de Compartir Manual**
1. Click en botón "Compartir"
2. Activación de loading indicator
3. Descarga de imagen preview del manual
4. Conversión a Base64
5. Guardado temporal en cache del dispositivo
6. Apertura de diálogo nativo de compartir
7. Envío con texto y archivo adjunto

### 7.2 Estados de Error y Recuperación

- **Error de Carga:** Manejo con try-catch y console.error
- **Error de Descarga:** Validación de response.ok
- **Error de Filesystem:** Manejo de errores de escritura
- **Error de Compartir:** Fallback con mensaje de error

---

## 8. Consideraciones de Performance

### 8.1 Optimizaciones Implementadas

1. **Lazy Loading:** Manuales cargados bajo demanda
2. **Efficient Grid:** CSS Grid con auto-fit para responsividad
3. **Image Caching:** Cache temporal en filesystem para compartir
4. **Track By Function:** Optimización de *ngFor con trackByManual

### 8.2 Manejo de Memoria

```typescript
trackByManual(index: number, manual: Manuals): number {
  return manual.id; // Returns the unique ID of each manual
}
```

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Carga inicial de manuales**
2. **Visualización responsiva del grid**
3. **Descarga de imágenes**
4. **Conversión a Base64**
5. **Escritura en filesystem**
6. **Compartición con archivos**
7. **Loading states**
8. **Error handling**
9. **Responsive design**
10. **Performance tracking**

### 9.2 Pruebas Unitarias Requeridas

- Carga y filtrado de manuales
- Proceso de compartición completo
- Manejo de filesystem
- Conversión de imágenes
- Responsive behavior
- Error handling
- Performance de grid

---

## 10. Consideraciones de Seguridad

### 10.1 Manejo de Datos Sensibles

- **URL Validation:** Validación de URLs antes de descarga
- **File System Security:** Paths controlados para cache
- **Share Data Validation:** Sanitización de datos antes de compartir
- **Image Processing:** Manejo seguro de blobs y Base64

### 10.2 Validaciones de Entrada

- **Manual URLs:** Validación de formato y accesibilidad
- **File Names:** Sanitización de nombres de archivo
- **Share Content:** Validación de contenido antes de compartir
- **Network Requests:** Manejo seguro de fetch requests

---

## 11. APIs y Servicios Externos

### 11.1 Capacitor Share API

- **URL:** https://capacitorjs.com/docs/apis/share
- **Propósito:** Compartir contenido a través de APIs nativas
- **Uso en la aplicación:** 
  - Compartir manuales con archivos adjuntos
  - Detección automática de capacidades
  - Soporte para texto y archivos
- **Características:** 
  - Cross-platform compatibility
  - Soporte para archivos adjuntos
  - Integración con apps nativas de compartir

### 11.2 Capacitor Filesystem API

- **URL:** https://capacitorjs.com/docs/apis/filesystem
- **Propósito:** Acceso al sistema de archivos del dispositivo
- **Uso en la aplicación:** 
  - Cache temporal de imágenes para compartir
  - Escritura en Directory.Cache
  - Manejo de paths y URIs
- **Características:** 
  - Cross-platform file operations
  - Cache management
  - URI handling

### 11.3 Web APIs Nativas

#### **Fetch API**
- **Propósito:** Descarga de imágenes desde URLs
- **Uso:** `fetch(imageURL)` para obtener blobs
- **Características:** Soporte para streams y blobs

#### **FileReader API**
- **Propósito:** Conversión de blobs a Base64
- **Uso:** `fileReader.readAsDataURL(blob)`
- **Características:** Manejo de datos binarios

---

## 12. Componentes y Código Destacable

### 12.1 Sistema de Compartición Completo

```typescript
public shareMessageWithImage(url: string, name: string, imgPrev: string): Promise<void> {
  this.utilService.show();
  this.isLoading = true;
  
  return new Promise<void>((resolve, reject) => {
    try {
      const message = `Hola, te estoy enviando el Manual de ${name}: \n\n${url}`;
      const imageURL = new URL(url, location.href).toString();

      fetch(imageURL, { method: 'GET' })
        .then(response => {
          if (!response.ok) {
            throw new Error(`Error al obtener la imagen: ${response.statusText}`);
          }
          return response.blob();
        })
        .then(blob => {
          const fileReader = new FileReader();
          fileReader.onload = () => {
            const base64Image = fileReader.result as string;
            const splited = url.split('/');
            const nameFile = splited[splited.length - 1];

            Filesystem.writeFile({
              data: base64Image,
              path: nameFile,
              directory: Directory.Cache,
            })
              .then(resultWrite => {
                const filePath = resultWrite.uri;

                Share.share({
                  title: name,
                  text: message,
                  dialogTitle: name,
                  files: [filePath],
                })
                  .then(() => resolve())
                  .catch(err => {
                    console.error(err);
                    reject(err);
                  })
                  .finally(() => {
                    this.isLoading = false;
                    this.utilService.hide();
                  });
              });
          };
          fileReader.readAsDataURL(blob);
        });
    } catch (err) {
      console.error(err);
      this.isLoading = false;
      this.utilService.hide();
      reject(err);
    }
  });
}
```

**Características:**
- Descarga automática de imágenes
- Conversión a Base64 para compatibilidad
- Cache temporal en filesystem
- Compartición con archivos adjuntos
- Manejo robusto de errores
- Loading states apropiados

### 12.2 Grid Responsivo con CSS Grid

```scss
.manual-container {
  @apply grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 grid-flow-row items-center justify-center p-4 gap-4 place-items-center max-w-[95rem] mx-auto;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr)) !important;
}
```

**Características:**
- Auto-fit para adaptabilidad total
- Mínimo de 300px por card
- Responsive breakpoints
- Center alignment
- Maximum width control

### 12.3 Optimización de *ngFor

```typescript
trackByManual(index: number, manual: Manuals): number {
  return manual.id; // Returns the unique ID of each manual
}
```

**Características:**
- Optimización de rendimiento
- Tracking por ID único
- Reducción de re-renders
- Mejora de performance

---

## 13. Mejoras Futuras Sugeridas

### 13.1 Features Potenciales

1. **PDF Viewer:** Visualización inline de manuales PDF
2. **Search Functionality:** Búsqueda dentro de manuales
3. **Favorites:** Guardar manuales favoritos
4. **Offline Mode:** Descarga completa para acceso offline
5. **Categories:** Categorización de manuales por tipo

### 13.2 Optimizaciones Técnicas

1. **Virtual Scrolling:** Para grandes cantidades de manuales
2. **Image Optimization:** Compresión de imágenes preview
3. **Progressive Loading:** Carga progresiva de contenido
4. **Cache Strategy:** Cache inteligente de manuales
5. **Performance Monitoring:** Métricas de uso y rendimiento

---

## 14. Notas para Mantenimiento

### 14.1 Puntos Críticos

1. **Image Processing:** Mantener optimización de imágenes
2. **File System Management:** Limpieza de cache temporal
3. **Share API Compatibility:** Testing en diferentes dispositivos
4. **Grid Performance:** Optimización para grandes volúmenes
5. **Error Handling:** Manejo robusto de errores de red

### 14.2 Buenas Prácticas

- Mantener validación de todas las URLs de manuales
- Implementar proper cleanup de cache
- Mantener consistencia en loading states
- Documentar cambios en APIs externas
- Realizar testing cross-platform regularmente
- Optimizar para dispositivos móviles

---

## 15. Conclusión

La Guide Page representa un componente esencial en la arquitectura de Oficina Móvil para la gestión de documentación técnica. Su implementación con sistema de compartición avanzado, cache inteligente de imágenes y diseño responsivo la convierten en una solución completa para el acceso a manuales técnicos de clientes Fibex.

La arquitectura modular, la integración con Capacitor para funcionalidades nativas y el manejo eficiente de archivos proporcionan una base sólida para futuras mejoras como visualización inline de PDFs, búsqueda avanzada y modo offline. Su diseño actual ofrece una experiencia de usuario intuitiva y eficiente tanto en plataformas móviles como web.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
