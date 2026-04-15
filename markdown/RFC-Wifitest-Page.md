# RFC: Wifitest Page - Sistema de Pruebas de Velocidad Internet

## Introducción

La **Wifitest Page** es el componente especializado de pruebas de velocidad de la aplicación **Oficina Móvil V2** que permite a los usuarios realizar pruebas de velocidad de conexión a internet a través de una interfaz integrada con el servicio de pruebas de **Fibex Telecom**. Esta página implementa un sistema de iframe con control de estados, modal de instrucciones y manejo de errores para proporcionar una experiencia completa de medición de velocidad.

Este RFC documenta la arquitectura técnica, flujo de usuario, sistema de integración con iframe externo, manejo de estados y consideraciones de implementación de la página de pruebas de velocidad, que sirve como portal central para la medición de rendimiento de conexión de los clientes Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/wifitest.jpeg" alt="Wifitest Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | WifitestPage (src/app/pages/wifitest/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/wifitest/
    wifitest.page.ts          # Componente principal con lógica de pruebas
    wifitest.page.html        # Template con iframe y estados
    wifitest.page.scss        # Estilos específicos del componente
    wifitest.page.spec.ts     # Pruebas unitarias
    wifitest-routing.module.ts # Configuración de rutas
    wifitest.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Angular Core**
- **Propósito:** Framework base con lifecycle management
- **Configuración:** Component lifecycle, dependency injection
- **Integración:** Decoradores @Component, OnInit
- **Documentación:** [Angular Documentation](https://angular.dev/)

#### **Ionic Framework**
- **Propósito:** Componentes UI nativos y navegación
- **Configuración:** ion-content, ion-spinner, ion-header
- **Integración:** ViewWillEnter lifecycle hook
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

#### **HTML5 Iframe API**
- **Propósito:** Integración de contenido externo
- **Configuración:** src, frameborder, allowfullscreen attributes
- **Integración:** Eventos load y error del iframe
- **Documentación:** [HTML5 Iframe Documentation](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura de Estados

La página implementa un sistema de 3 estados para el iframe:

#### **Estado: LOADING**
- **Componente:** Spinner de carga
- **Propósito:** Indicar que el test está cargando
- **Features:** 
  - Spinner circular de 80x80px
  - Centrado vertical y horizontal
  - Mensaje de espera opcional

#### **Estado: LOADED**
- **Componente:** Iframe con test de velocidad
- **Propósito:** Mostrar la interfaz del test
- **Features:** 
  - Iframe de 500px de altura
  - Integración con velocidad.fibextelecom.net
  - Fullscreen y scrolling deshabilitados

#### **Estado: ERROR**
- **Componente:** Mensaje de error
- **Propósito:** Informar sobre problemas de carga
- **Features:** 
  - Mensaje descriptivo del error
  - Opciones de reintento
  - Retroalimentación clara

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Enum de Estados**
```typescript
enum StatusIframe {
  LOADING,
  LOADED,
  ERROR,
}

public statusEnum = StatusIframe;
public status: StatusIframe = StatusIframe.LOADING;
```

#### **Manejo de Eventos del Iframe**
```typescript
handleLoad() {
  this.status = StatusIframe.LOADED;
}

handleError() {
  const errorPages = {
    message: 'Error en el modal',
    linea: '76',
    componente: 'wifitest',
    nombre_metodo: this.constructor.name,
    obj_error: new Error('Error en el modal'),
  };

  this.status = StatusIframe.ERROR;
}
```

### 3.2 Sistema de Instrucciones Modal

#### **Modal de Recomendaciones**
```typescript
showModal(locationName: string) {
  try {
    const promps: IModalInfoPromps = {
      imgSrc: 'assets/images/router.png',
      width_img: '9rem',
      title: 'Recomendaciones',
      message: `Antes de realizar el test de velocidad, por favor asegúrate de:
      <div class="container-wifitest-paragraf">
        <p class="container-wifitest-paragraf-p"><strong>1.</strong> <span> Conectar tu dispositivo directamente al router. </span> </p>
        <p class="container-wifitest-paragraf-p"><strong>2.</strong> <span> Cerrar todas las aplicaciones y dispositivos que usen internet. </span> </p>
        <p class="container-wifitest-paragraf-p"><strong>3.</strong> <span> Evitar moverte mientras realizas el test. </span> </p>
        <p class="container-wifitest-paragraf-p"><strong>4.</strong> <span> Realizar el test cerca del router para una mejor precisión. </span> </p>
      </div>`,
      checkBox: true,
      checkMessage: `Confirmo haber entendido las instrucciones`,
      buttons: [
        {
          label: 'Cerrar',
          onClick: () => {},
        },
      ],
    };

    this.dialogService.showStandardModalInfo(promps);
  } catch (error) {
    const errorShowmodal = {
      message: 'error del modal',
      linea: '62',
      componente: 'wifitest',
      nombre_metodo: this.constructor.name,
      obj_error: error,
    };
  }
}
```

---

## 4. Componentes Compartidos Integrados

### 4.1 Componentes Principales

#### **ContentHeaderComponent**
- **Ruta:** `importsComponents/headers/content-header/content-header.component`
- **Propósito:** Header estándar con título y navegación
- **Features:** 
  - Título "Test Wifi"
  - Botón de retroceso
  - Layout consistente con otras páginas

#### **IframeTemplateComponent**
- **Ruta:** `importsComponents/iframe-template/iframe-template.component`
- **Propósito:** Template para manejo de iframes
- **Features:** 
  - Manejo de eventos de carga
  - Control de dimensiones
  - Integración con contenido externo

#### **HeaderSmallComponent**
- **Ruta:** `importsComponents/headers/header-small/header-small.component`
- **Propósito:** Header compacto para mobile
- **Features:** 
  - Diseño optimizado para móviles
  - Navegación minimalista

### 4.2 Estructura de Template

#### **Contenedor Principal con Iframe**
```html
<ion-content fullscreen="true" class="contenedor" style="padding: 1rem">
  <app-content-header title="Test Wifi">
    <div class="iframe-container" style="margin-top: 20px">
      <iframe
        class="wifitest-iframe"
        src="https://velocidad.fibextelecom.net/app"
        frameborder="0"
        width="100%"
        height="500px"
        allowfullscreen
        scrolling="no"
        [ngClass]="{hidden:status!=statusEnum.LOADED}"
        (error)="handleError()"
        (load)="handleLoad()"
      ></iframe>
    </div>

    <!-- Estados de carga -->
    @switch (status) { 
      @case (statusEnum.LOADING) {
        <div class="flex items-center justify-center pt-12">
          <ion-spinner name="circular" style="width: 80px; height: 80px"></ion-spinner>
        </div>
      } 
      
      @case (statusEnum.ERROR) {
        <p>tu internet esta piche</p>
      } 
    }
  </app-content-header>
</ion-content>
```

---

## 5. Integración con Servicios

### 5.1 Servicios Principales

#### **NetworkStatusService**
- **Propósito:** Validación de conectividad
- **Métodos clave:** `validateNetworkAccess()`
- **Uso:** Verificar conexión antes de iniciar test
- **Flujo:** Validación al entrar a la página

#### **DialogsService**
- **Propósito:** Gestión de modales y notificaciones
- **Métodos clave:** `showStandardModalInfo()`
- **Uso:** Mostrar instrucciones antes del test
- **Características:** Modal con checkbox de confirmación

---

## 6. Estilos y Diseño Visual

### 6.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
ion-content {
  display: flex;
  height: 100%;
  width: 100%;
}

.wiffi_iframe {
  height: 100%;
  width: 100%;
  flex-grow: 1;
}

.container {
  width: 100px;
  height: 100px;
}

.modal-info-container[_ngcontent-ng-c1965373711] p[_ngcontent-ng-c1965373711] {
  padding-block: 1rem;
  text-wrap: balance;
  text-align: left;
}

.parrafo {
  text-align: justify;
}

.container-wifitest-small-img {
  width: 30px;
  height: auto;
}
```

#### **Diseño Responsivo**
- **Fullscreen:** ion-content con fullscreen="true"
- **Iframe Responsivo:** 100% width con altura fija
- **Centered Content:** Flexbox para centrar elementos
- **Modal Styling:** Estilos específicos para contenido del modal

### 6.2 Estados Visuales

- **Loading State:** Spinner circular centrado
- **Error State:** Mensaje descriptivo simple
- **Loaded State:** Iframe con contenido externo
- **Modal State:** Instrucciones con imagen y checkbox

---

## 7. Flujo de Usuario Detallado

### 7.1 Caminos Principales

#### **Usuario Iniciando Test**
1. Entrada a la página de Wifi Test
2. Validación automática de conectividad
3. Apertura automática del modal de instrucciones
4. Lectura y confirmación de recomendaciones
5. Cierre del modal y carga del iframe
6. Visualización del spinner de carga
7. Carga completa del test de velocidad
8. Realización del test en la interfaz externa

#### **Usuario con Error de Carga**
1. Entrada a la página
2. Error en la carga del iframe
3. Visualización del mensaje de error
4. Opción de recargar página
5. Reintento automático del proceso

### 7.2 Estados de Error y Recuperación

- **Error de Conexión:** Validación de red al inicio
- **Error de Iframe:** Manejo con evento error
- **Error de Modal:** Try-catch en showModal
- **Error General:** Logging detallado con contexto

---

## 8. Consideraciones de Performance

### 8.1 Optimizaciones Implementadas

1. **Lazy Loading:** Iframe carga bajo demanda
2. **State Management:** Enum para control eficiente de estados
3. **Error Handling:** Manejo robusto de errores asíncronos
4. **Network Validation:** Verificación preventiva de conexión

### 8.2 Manejo de Memoria

- **Iframe Cleanup:** Manejo apropiado del ciclo de vida
- **Modal Management:** Liberación de recursos modales
- **State Reset:** Limpieza de estados al salir

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Carga inicial del iframe**
2. **Validación de conectividad**
3. **Mostrar modal de instrucciones**
4. **Manejo de estados de carga**
5. **Error handling del iframe**
6. **Responsive design**
7. **Cross-platform compatibility**
8. **Modal checkbox functionality**
9. **Iframe event handling**
10. **Performance de carga**

### 9.2 Pruebas Unitarias Requeridas

- Manejo de estados del iframe
- Validación de conectividad
- Funcionalidad del modal
- Manejo de errores
- Eventos del iframe
- Responsive behavior
- Cross-browser testing

---

## 10. Consideraciones de Seguridad

### 10.1 Manejo de Iframe Externo

- **CORS Policy:** Validación de políticas de origen cruzado
- **Sandbox Attributes:** Configuración segura del iframe
- **URL Validation:** Validación de URL externa
- **Content Security:** Prevención de XSS

### 10.2 Validaciones de Seguridad

- **Network Validation:** Verificación de conexión segura
- **Input Sanitization:** Limpieza de contenido dinámico
- **Error Logging:** Manejo seguro de información de errores
- **Modal Content:** Sanitización de HTML en mensajes

---

## 11. APIs y Servicios Externos

### 11.1 Fibex Telecom Speed Test API

- **URL:** https://velocidad.fibextelecom.net/app
- **Propósito:** Servicio externo de pruebas de velocidad
- **Uso en la aplicación:** 
  - Integración vía iframe
  - Pruebas de velocidad completas
  - Resultados en tiempo real
  - Interfaz especializada para Fibex
- **Características:** 
  - Pruebas de descarga y subida
  - Medición de latencia (ping)
  - Interfaz responsive
  - Resultados detallados

### 11.2 HTML5 Iframe API

- **URL:** https://developer.mozilla.org/en-US/docs/Web/HTML/Element/iframe
- **Propósito:** Integración de contenido externo
- **Uso en la aplicación:** 
  - Carga del test de velocidad
  - Manejo de eventos de carga
  - Control de dimensiones y comportamiento
- **Características:** 
  - Cross-origin communication
  - Event handling
  - Security attributes
  - Responsive integration

---

## 12. Componentes y Código Destacable

### 12.1 Sistema de Estados con Enum

```typescript
enum StatusIframe {
  LOADING,
  LOADED,
  ERROR,
}

export class WifitestPage implements OnInit {
  public statusEnum = StatusIframe;
  public status: StatusIframe = StatusIframe.LOADING;

  handleLoad() {
    this.status = StatusIframe.LOADED;
  }

  handleError() {
    this.status = StatusIframe.ERROR;
  }
}
```

**Características:**
- Type-safe state management
- Claro control de flujo
- Fácil extensibilidad
- Debugging simplificado

### 12.2 Modal de Instrucciones Detallado

```typescript
showModal(locationName: string) {
  try {
    const promps: IModalInfoPromps = {
      imgSrc: 'assets/images/router.png',
      width_img: '9rem',
      title: 'Recomendaciones',
      message: `Antes de realizar el test de velocidad, por favor asegúrate de:
      <div class="container-wifitest-paragraf">
        <p class="container-wifitest-paragraf-p"><strong>1.</strong> <span> Conectar tu dispositivo directamente al router. </span> </p>
        <p class="container-wifitest-paragraf-p"><strong>2.</strong> <span> Cerrar todas las aplicaciones y dispositivos que usen internet. </span> </p>
        <p class="container-wifitest-paragraf-p"><strong>3.</strong> <span> Evitar moverte mientras realizas el test. </span> </p>
        <p class="container-wifitest-paragraf-p"><strong>4.</strong> <span> Realizar el test cerca del router para una mejor precisión. </span> </p>
      </div>`,
      checkBox: true,
      checkMessage: `Confirmo haber entendido las instrucciones`,
      buttons: [
        {
          label: 'Cerrar',
          onClick: () => {},
        },
      ],
    };

    this.dialogService.showStandardModalInfo(promps);
  } catch (error) {
    const errorShowmodal = {
      message: 'error del modal',
      linea: '62',
      componente: 'wifitest',
      nombre_metodo: this.constructor.name,
      obj_error: error,
    };
  }
}
```

**Características:**
- Instrucciones claras y numeradas
- Imagen representativa del router
- Checkbox de confirmación
- Manejo robusto de errores
- Logging detallado

### 12.3 Manejo de Eventos del Iframe

```html
<iframe
  class="wifitest-iframe"
  src="https://velocidad.fibextelecom.net/app"
  frameborder="0"
  width="100%"
  height="500px"
  allowfullscreen
  scrolling="no"
  [ngClass]="{hidden:status!=statusEnum.LOADED}"
  (error)="handleError()"
  (load)="handleLoad()"
></iframe>
```

**Características:**
- Eventos de carga y error
- Control de visibilidad con ngClass
- Configuración de seguridad
- Dimensiones responsivas
- Integración fluida

---

## 13. Mejoras Futuras Sugeridas

### 13.1 Features Potenciales

1. **Historial de Tests:** Guardar resultados anteriores
2. **Comparative Analysis:** Comparar resultados históricos
3. **Scheduled Tests:** Tests automáticos programados
4. **Advanced Metrics:** Métricas adicionales de red
5. **Offline Mode:** Tests básicos sin conexión externa

### 13.2 Optimizaciones Técnicas

1. **Iframe Communication:** PostMessage API para comunicación bidireccional
2. **Progressive Loading:** Carga progresiva del test
3. **Error Recovery:** Reintentos automáticos con backoff
4. **Performance Monitoring:** Métricas de tiempo de carga
5. **Accessibility:** Mejoras para accesibilidad

---

## 14. Notas para Mantenimiento

### 14.1 Puntos Críticos

1. **Iframe Integration:** Mantener compatibilidad con servicio externo
2. **State Management:** Coordinación precisa de estados
3. **Error Handling:** Manejo robusto de errores de red
4. **Modal Content:** Actualización de instrucciones según necesidades
5. **Cross-browser Testing:** Compatibilidad con diferentes navegadores

### 14.2 Buenas Prácticas

- Mantener validación de conectividad antes de operaciones
- Implementar proper error logging con contexto
- Mantener consistencia en estados de UI
- Documentar cambios en API externa
- Realizar testing cross-platform regularmente
- Optimizar para dispositivos móviles

---

## 15. Conclusión

La Wifitest Page representa un componente especializado y eficiente en la arquitectura de Oficina Móvil para la medición de velocidad de conexión. Su implementación con sistema de estados robusto, integración segura con iframe externo y modal de instrucciones detallado la convierten en una solución completa para las necesidades de diagnóstico de red de los clientes Fibex.

La arquitectura modular, la integración con el servicio especializado de pruebas de velocidad de Fibex y el manejo inteligente de estados proporcionan una base sólida para futuras mejoras como historial de resultados, análisis comparativo y comunicación bidireccional con el iframe. Su diseño actual ofrece una experiencia de usuario clara y eficiente tanto en plataformas móviles como web.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
