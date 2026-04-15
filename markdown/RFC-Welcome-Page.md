# RFC: Welcome Page - Onboarding Experience

## Introducción

La **Welcome Page** es el punto de entrada principal de la aplicación **Oficina Móvil V2** que sirve como experiencia de onboarding para nuevos usuarios. Esta página implementa un slider interactivo con Swiper.js que presenta los beneficios clave del servicio, guiando al usuario hacia las acciones principales de autenticación o registro de nuevos servicios.

Este RFC documenta la implementación actual de la página de bienvenida, su arquitectura técnica, flujo de usuario y consideraciones de diseño para mantener una experiencia de usuario consistente y optimizada en todas las plataformas móviles.

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo — Versión 3.3.1                  |
| **Componente**  | WelcomePage (src/app/pages/welcome/)    |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-12                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/welcome/
├── welcome.page.ts          # Componente principal con lógica
├── welcome.page.html        # Template HTML con estructura UI
├── welcome.page.scss        # Estilos específicos del componente
├── welcome.page.spec.ts     # Pruebas unitarias
├── welcome-routing.module.ts # Configuración de rutas
└── welcome.module.ts        # Módulo Angular
```

### 1.2 Dependencias Externas

#### **Swiper.js v9.4.1**
- **Propósito:** Carrousel interactivo para slides de bienvenida
- **Configuración:** `slides-per-view="1"`, `autoplay="true"`
- **Integración:** Mediante `<swiper-container>` y `<swiper-slide>`
- **Documentación:** [Swiper.js Documentation](https://swiperjs.com/)

#### **Datos Mock**
- **Origen:** `src/app/mock/welcome-page-data.ts`
- **Variable:** `welcomeSliderSections`
- **Contenido:** 2 secciones HTML con información del servicio

---

## 2. Flujo de Usuario y Experiencia

### 2.1 Estados de Navegación

La página maneja tres estados principales:

1. **Estado Inicial:** Primer slide con información del servicio
2. **Estado Intermedio:** Navegación entre slides
3. **Estado Final:** Último slide con botones de acción

### 2.2 Componentes de UI

#### **Header Dinámico**
```typescript
// Estructura condicional basada en estado
@if (isLast) {
  <button (click)="onPrev()"> // Botón para volver al inicio
} else {
  <button (click)="onSkip()"> // Botón para saltar al final
}
```

#### **Slider de Contenido**
- **Contenedor:** `<swiper-container #swiper>`
- **Slides:** Generados dinámicamente desde `slideSections`
- **Renderizado:** `[innerHTML]="slideItem"` para contenido HTML

#### **Indicadores de Progreso**
```html
<div class="pagers">
  <div *ngFor="let item of items" 
       [class]="item == index ?'active':'deactive'">
  </div>
</div>
```

#### **Botones de Acción Final**
- **"Soy cliente"**: Navegación a `/signin`
- **"Contratar servicio"**: Navegación a `/chat`

---

## 3. Implementación Técnica

### 3.1 Ciclo de Vida del Componente

#### **ionViewWillEnter()**
```typescript
ionViewWillEnter() {
  this.isInViewActive = true;
  this.resetSlider();
}
```
- Activa la vista del slider
- Reinicia estados para nueva entrada

#### **ionViewDidEnter()**
```typescript
ionViewDidEnter() {
  this.resetSlider();
  setTimeout(() => {
    // Timeout para dispositivos lentos
    this.length = this.swiper?.nativeElement.swiper.slides.length;
    this.index = this.swiper?.nativeElement.swiper.activeIndex;
    // Generación de indicadores de página
  }, 700);
}
```
- Configura el slider con delay para dispositivos lentos
- Inicializa contadores y generadores de UI

#### **ionViewWillLeave()**
```typescript
ionViewWillLeave() {
  this.isInViewActive = false;
  this.resetSlider();
}
```
- Limpia estados al salir de la vista

### 3.2 Gestión de Estados

#### **Propiedades Principales**
```typescript
@ViewChild('swiper') swiper?: ElementRef<{ swiper: Swiper }>;
isLast: boolean = false;           // Estado del último slide
length: number | undefined = 0;    // Total de slides
index: number | undefined = 0;     // Slide actual
items: number[] = [];              // Array para indicadores
slideSections: string[] = welcomeSliderSections; // Contenido
isInViewActive: boolean = false;   // Estado de visibilidad
```

#### **Métodos de Control**
```typescript
onSkip() {
  this.swiper?.nativeElement.swiper.slideTo(3); // Salta al final
}

onPrev() {
  this.swiper?.nativeElement.swiper.slideTo(0); // Vuelve al inicio
}

slideChanged(event: any) {
  this.index = this.swiper?.nativeElement.swiper.activeIndex;
  this.isLast = this.swiper?.nativeElement.swiper.isEnd ?? false;
}
```

---

## 4. Contenido y Datos

### 4.1 Estructura de welcomeSliderSections

El archivo `welcome-page-data.ts` define el contenido del slider:

```typescript
export const welcomeSliderSections: string[] = [
  // Slide 1: Presentación del servicio
  `
    <div class="slide-content">
        <img src="assets/images/logos/globo-company-450.png" 
             alt="Fibex Globo" class="back_img">
        <p class="head-title">Oficina Móvil</p>
        <p class="sub-title">
            Un servicio exclusivo para clientes. Autogestiona de forma 
            rápida, sencilla y segura tus operaciones de servicios de Internet
        </p>
    </div>
  `,
  // Slide 2: Beneficios y marcas aliadas
  `
    <div class="slide-content pt-16">
        <img src="assets/images/company-pet/sofia-size-lg.png" 
             class="back_img back_img_contain_type">
        <p class="sub-title">
          Descubre el poder de los beneficios exclusivos con nuestras 
          marcas aliadas desde la App Oficina Móvil Fibex.
        </p>
    </div>
  `
];
```

### 4.2 Assets Utilizados

- **Logo Principal:** `assets/images/logos/globo-company-450.png`
- **Mascota Sofia:** `assets/images/company-pet/sofia-size-lg.png`
- **Logo Fibex:** `assets/images/logos/fibextelecom.png`

---

## 5. Estilos y Diseño Visual

### 5.1 Arquitectura de Estilos

#### **Variables CSS**
- Uso de variables CSS para theming consistente
- Integración con sistema de colores de Ionic

#### **Clases Principales**
```scss
.welcomepage-header {
  height: 6.5rem;
  padding-top: 1.5rem;
  // Layout flexible con logo y botones
}

.slide-content-bottom-section {
  display: flex;
  flex-direction: column;
  padding-top: 3rem;
  gap: 0.8rem;
  padding-inline: 1rem;
}

.btn-style-icon-1.btns {
  border: 0.6px solid rgba(255, 255, 255, 0.478);
  border-radius: 13px;
  color: white;
  padding: 0.8rem;
}
```

### 5.2 Responsive Design

- **Adaptación móvil:** Layout optimizado para pantallas táctiles
- **Contenedor flexible:** Uso de Flexbox para alineación
- **Imágenes responsivas:** `object-fit: contain` para assets

---

## 6. Integración con Navegación

### 6.1 Rutas de Salida

```typescript
onLogin() {
  this.util.navigateRoot('/signin');  // Clientes existentes
}

onRegister() {
  this.util.navigateToPage('/chat');  // Nuevos servicios
}
```

### 6.2 UtilService Integration

El componente depende de `UtilService` para:
- Navegación programática
- Utilidades de UI compartidas
- Gestión de rutas

---

## 7. Consideraciones de Performance

### 7.1 Optimizaciones Implementadas

1. **Lazy Loading:** La página se carga bajo demanda
2. **ViewChild:** Acceso directo al DOM para manipulación eficiente
3. **Timeout Strategy:** Delay para dispositivos de baja performance
4. **Estado Reactivo:** Gestión eficiente de cambios de UI

### 7.2 Manejo de Memoria

```typescript
ionViewWillLeave() {
  this.resetSlider(); // Limpieza de estados
}
```

---

## 8. Testing y Calidad

### 8.1 Pruebas Unitarias

El archivo `welcome.page.spec.ts` debe cubrir:
- Inicialización del componente
- Navegación entre slides
- Estados de botones
- Integración con Swiper
- Manejo de ciclos de vida

### 8.2 Casos de Uso Críticos

1. **Flujo completo:** Navegación desde inicio hasta acción final
2. **Skip functionality:** Salto directo al último slide
3. **Back navigation:** Regreso desde el último slide
4. **Responsive behavior:** Comportamiento en diferentes tamaños

---

## 9. Mejoras Futuras Sugeridas

### 9.1 Features Potenciales

1. **Animaciones avanzadas:** Transiciones más fluidas entre slides
2. **Personalización dinámica:** Contenido basado en perfil de usuario
3. **Analytics:** Tracking de interacciones del usuario
4. **A/B Testing:** Diferentes versiones de onboarding

### 9.2 Optimizaciones Técnicas

1. **Preloading de assets:** Carga anticipada de imágenes
2. **Service Worker:** Caching para mejor performance offline
3. **Accesibilidad:** Mejoras para usuarios con discapacidades
4. **Internacionalización:** Soporte multiidioma

---

## 10. Notas para Mantenimiento

### 10.1 Puntos Clave a Considerar

1. **Timeout de 700ms:** Ajustar según dispositivos objetivo
2. **Contenido HTML:** Validar seguridad del innerHTML
3. **Assets:** Mantener consistencia en tamaños y formatos
4. **Versionado:** Coordinar cambios con actualizaciones de Swiper.js

### 10.2 Buenas Prácticas

- Mantener separación clara entre lógica y presentación
- Validar cambios en múltiples dispositivos
- Documentar cualquier modificación al flujo de usuario
- Realizar pruebas de regresión ante actualizaciones de dependencias

---

## 11. Conclusión

La Welcome Page representa un componente crítico en la experiencia de usuario de Oficina Móvil. Su implementación actual balancea funcionalidad, performance y mantenibilidad, proporcionando un onboarding efectivo que guía a los usuarios hacia las acciones principales de la aplicación.

La arquitectura modular y el uso de estándares establecidos como Swiper.js aseguran que el componente sea escalable y fácil de mantener, mientras que el diseño responsivo garantiza una experiencia consistente across todas las plataformas soportadas.

---

*Documentación actualizada: 2026-04-12*
*Autor: Equipo de Desarrollo Fibex Telecom*
