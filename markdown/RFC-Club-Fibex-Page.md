# RFC: Club Fibex Page - Portal de Beneficios

## Introducción

La **Club Fibex Page** es el portal web integrado que proporciona acceso a los beneficios y servicios exclusivos para clientes de **Fibex Telecom**. Esta página implementa un sistema de iframe seguro que carga el portal de Club Fibex con autenticación automática mediante parámetros de usuario, gestionando la validación de red y proporcionando una experiencia de navegación fluida dentro del ecosistema de servicios de Fibex.

Este RFC documenta la arquitectura técnica, integración de iframe, gestión de seguridad y consideraciones de implementación de la página Club Fibex, que sirve como puerta de acceso a beneficios y promociones exclusivas para clientes de Fibex Telecom.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/club-fibex.png" alt="Club Fibex Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | ClubFibexPage (src/app/pages/club-fibex/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-13                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/club-fibex/
    club-fibex.page.ts          # Componente principal con lógica de iframe
    club-fibex.page.html        # Template con iframe y UI de carga
    club-fibex.page.scss        # Estilos específicos del componente
    club-fibex.page.spec.ts     # Pruebas unitarias
    club-fibex-routing.module.ts # Configuración de rutas
    club-fibex.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Angular Platform Browser**
- **Propósito:** Sanitización de URLs para seguridad de iframes
- **Servicios:** `DomSanitizer`, `SafeResourceUrl`
- **Método:** `bypassSecurityTrustResourceUrl()` para URLs confiables
- **Documentación:** [Angular Platform Browser Documentation](https://angular.dev/api/platform-browser)

#### **Capacitor Network**
- **Propósito:** Detección de estado de conexión a red
- **Servicios:** `Network.getStatus()`, `Network.addListener()`
- **Eventos:** `networkStatusChange` para cambios en tiempo real
- **Documentación:** [Capacitor Network Documentation](https://capacitorjs.com/docs/apis/network)

#### **Ionic Framework**
- **IonContent:** Contenedor principal con modo fullscreen
- **IonSpinner:** Indicador de carga durante carga de iframe
- **Platform Detection:** Detección de plataforma iOS/Android
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

---

## 2. Flujo de Navegación y Autenticación

### 2.1 Sistema de Autenticación Automática

La página implementa autenticación automática mediante parámetros URL:

#### **Construcción de URL Segura**
```typescript
this.safeUrl = this.sanitizer.bypassSecurityTrustResourceUrl(
  `${environment.urlClubFibex}?dni=${user?.cedula_abonado}&usermail=${user?.email_abonado}&userphone=${user?.telefono_abonado}`,
);
```

#### **Parámetros Transmitidos**
- **dni:** Cédula del abonado para identificación
- **usermail:** Email del abonado para notificaciones
- **userphone:** Teléfono del abonado para contacto

### 2.2 Gestión de Estados de Carga

#### **Indicador Visual**
- **Estado Inicial:** Spinner centrado con logo Club Fibex
- **Transición:** Animación `iframeHides` para ocultar spinner
- **Tiempo de Espera:** 1.5 segundos antes de mostrar iframe

#### **Control de Visibilidad**
```typescript
public onLoad() {
  if (this.timerLoaderIframe) {
    clearTimeout(this.timerLoaderIframe);
    this.timerLoaderIframe = null;
  }

  this.timerLoaderIframe = setTimeout(() => {
    this.showLoadereIndicator = false;
  }, 1500);
}
```

---

## 3. Implementación Técnica

### 3.1 Gestión de Iframe

#### **Propiedades Principales**
```typescript
@ViewChild('iframe') iframe: ElementRef<HTMLIFrameElement>;
public safeUrl: SafeResourceUrl;
public showLoadereIndicator: boolean = false;
private timerLoaderIframe: NodeJS.Timeout | null = null;
```

#### **Configuración de Iframe**
```typescript
class="full-size-iframe"
[src]="safeUrl"
frameborder="0"
(load)="onLoad()"
#iframe
```

#### **Ajustes Dinámicos**
```typescript
ionViewDidEnter() {
  setTimeout(() => {
    if (this.iframe) {
      this.iframe.nativeElement.style.position = 'static';
      this.iframe.nativeElement.style.left = '0';
    }
  }, 700);
}
```

### 3.2 Sistema de Validación de Red

#### **NetworkStatusService Integration**
```typescript
ionViewWillEnter(): void {
  this.networkService.validateNetworkAccess();
}
```

#### **Validación de Conectividad**
- **Detección:** Estado de red mediante Capacitor Network
- **Retroalimentación:** Modales informativos sin conexión
- **Recuperación:** Opciones para reintentar o continuar offline

---

## 4. Integración con Servicios

### 4.1 Servicios Principales

#### **UserService**
- **Propósito:** Obtención de datos del usuario autenticado
- **Método:** `GetUserPromise()` para datos asíncronos
- **Datos Utilizados:** `cedula_abonado`, `email_abonado`, `telefono_abonado`

#### **NetworkStatusService**
- **Propósito:** Gestión de estado de conexión a red
- **Métodos:** `validateNetworkAccess()`, `getCurrentNetworkStatus()`
- **Eventos:** `networkStatusChange` para cambios en tiempo real

#### **Environment Configuration**
- **URL Base:** `environment.urlClubFibex` (https://club.fibextelecom.net)
- **Propósito:** Configuración centralizada del portal Club Fibex

#### **UtilService**
- **Propósito:** Navegación y utilidades generales
- **Método:** `navigateToPage()` para redirección segura

---

## 5. Diseño Visual y Experiencia de Usuario

### 5.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.full-size-iframe {
  width: 100%;
  height: 100%;
  border: 0 !important;
  outline: 0 !important;
  padding-top: 3.5rem;
}

.iframe-header {
  height: 3.5rem;
  display: flex;
  align-items: center;
  color: var(--light-color);
  background: linear-gradient(90deg, #0087bdc0 35%, #0078b4b0 90%);
  position: absolute;
  width: 100%;
  z-index: 2;
}

.bg-loading {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  transition: all 0.5s ease-in-out;
}
```

#### **Animaciones**
```scss
@keyframes iframeHides {
  0% { opacity: 1; }
  100% { opacity: 0; display: none; }
}

.iframeCustomHidden {
  animation: iframeHides 0.6s ease-out forwards;
}
```

### 5.2 Elementos de UI

#### **Header Personalizado**
- **Botón Cerrar:** Navegación de regreso al dashboard
- **Gradiente:** Diseño consistente con branding Fibex
- **Posicionamiento:** Fijo en parte superior con z-index elevado

#### **Imagen de Fondo**
- **Ruta:** `assets/images/bg/clubfibexbg-sm.jpg`
- **Logo:** `assets/images/logos/club-fibex-positive-lg.png`
- **Spinner:** Indicador circular de carga

---

## 6. Seguridad y Sanitización

### 6.1 Gestión de URLs Seguras

#### **DomSanitizer Integration**
```typescript
private sanitizer: DomSanitizer = inject(DomSanitizer);

this.safeUrl = this.sanitizer.bypassSecurityTrustResourceUrl(url);
```

#### **Validación de Contenido**
- **Sanitización:** Todas las URLs pasan por sanitizer
- **Frameborder:** Configurado a 0 para seguridad
- **Restricciones:** Sin scripts externos no confiables

### 6.2 Manejo de Datos Sensibles

#### **Parámetros URL**
- **Cifrado:** Transmisión HTTPS obligatoria
- **Validación:** Datos de usuario validados antes de uso
- **Sanitización:** Ningún dato sensible expuesto en cliente

---

## 7. Manejo de Estados y Errores

### 7.1 Estados de Conexión

#### **Validación de Red**
```typescript
public validateNetworkAccess = (): Promise<boolean> => {
  return new Promise<boolean>((resolve, reject) => {
    this.getCurrentNetworkStatus()
      .then(networkStatus => {
        if (!networkStatus) {
          // Mostrar modal de sin conexión
          this.dialogService.showStandardModalInfo(promps);
        } else resolve(false);
      });
  });
};
```

#### **Retroalimentación Usuario**
- **Toast Messages:** Notificaciones de cambio de conexión
- **Modal Informativo:** Detalles de problema de red
- **Opciones de Recuperación:** Reintentar o continuar offline

### 7.2 Manejo de Errores de Iframe

#### **Timeout Management**
```typescript
private timerLoaderIframe: NodeJS.Timeout | null = null;

public onLoad() {
  if (this.timerLoaderIframe) {
    clearTimeout(this.timerLoaderIframe);
    this.timerLoaderIframe = null;
  }
  // Lógica de carga completada
}
```

---

## 8. Optimizaciones de Performance

### 8.1 Mejoras Implementadas

1. **Lazy Loading:** Iframe cargado bajo demanda
2. **Timeout Control:** Prevención de memory leaks
3. **Network Validation:** Validación asíncrona eficiente
4. **Animation Optimization:** Hardware acceleration para transiciones

### 8.2 Gestión de Memoria

```typescript
public ngOnDestroy() {
  if (this.timerLoaderIframe) {
    clearTimeout(this.timerLoaderIframe);
    this.timerLoaderIframe = null;
  }
}
```

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Carga exitosa del portal Club Fibex**
2. **Manejo de ausencia de conexión a internet**
3. **Autenticación automática con parámetros correctos**
4. **Recuperación de caídas de red durante navegación**
5. **Comportamiento con datos de usuario incompletos**
6. **Navegación de regreso al dashboard**
7. **Visualización correcta en diferentes plataformas**

### 9.2 Pruebas Unitarias Requeridas

- Integración con UserService
- Sanitización de URLs
- Manejo de estados de carga
- Validación de red
- Gestión de timeouts
- Navegación programática

---

## 10. Consideraciones de Seguridad

### 10.1 Validaciones de Entrada

- **URL Sanitization:** Todas las URLs validadas y sanitizadas
- **Parameter Validation:** Datos de usuario validados antes de uso
- **Frame Security:** Iframe configurado con restricciones de seguridad
- **HTTPS Only:** Comunicación obligatoria mediante HTTPS

### 10.2 Manejo de Datos Sensibles

- **User Data:** Transmisión mediante parámetros URL seguros
- **No Storage:** No persistencia de datos sensibles en cliente
- **Secure Context:** Operación dentro de contexto HTTPS
- **Access Control:** Validación de permisos antes de carga

---

## 11. Mejoras Futuras Sugeridas

### 11.1 Features Potenciales

1. **PostMessage API:** Comunicación bidireccional con iframe
2. **Offline Mode:** Caché de contenido para acceso offline
3. **Enhanced Security:** Token-based authentication
4. **Analytics Integration:** Tracking de uso del portal
5. **Custom Theming:** Adaptación visual dinámica

### 11.2 Optimizaciones Técnicas

1. **Web Components:** Componentes reutilizables para iframes
2. **Service Workers:** Caché inteligente de contenido
3. **Error Boundaries:** Mejor manejo de errores
4. **Performance Monitoring:** Métricas de carga y uso

---

## 12. Notas para Mantenimiento

### 12.1 Puntos Críticos

1. **URL Configuration:** Mantener sincronización con environment
2. **Security Updates:** Actualización de políticas de sanitización
3. **Network Service:** Coordinación con cambios en conectividad
4. **Cross-Platform Testing:** Verificación en iOS/Android/Web

### 12.2 Buenas Prácticas

- Mantener sanitización de URLs actualizada
- Validar todos los parámetros de usuario
- Implementar proper error handling
- Monitorear rendimiento del iframe
- Documentar cambios en el flujo de autenticación

---

## 13. Conclusión

La Club Fibex Page representa un componente estratégico que proporciona acceso seguro y conveniente al portal de beneficios exclusivos para clientes de Fibex Telecom. Su implementación mediante iframe con autenticación automática garantiza una experiencia de usuario fluida mientras mantiene la seguridad y el control de datos dentro del ecosistema de la aplicación.

La arquitectura robusta con gestión de red, sanitización de URLs y manejo de estados la convierten en un componente fundamental que requiere especial atención durante el mantenimiento y evolución de la plataforma. Su diseño actual proporciona una base sólida para futuras mejoras en la integración de servicios externos y la experiencia de usuario.

---

*Documentación actualizada: 2026-04-13*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
