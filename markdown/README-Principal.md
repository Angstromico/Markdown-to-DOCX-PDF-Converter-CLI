# Documentación Principal: Oficina Móvil V2

## Introducción

**Oficina Móvil V2** es una aplicación **híbrida multiplataforma** desarrollada con **Angular 17**, **Ionic 8** y **Capacitor 7** que sirve como el centro digital de gestión para clientes de **Fibex Telecom**. La aplicación permite a los usuarios gestionar **pagos**, **facturación**, **servicios contratados**, **soporte técnico** y **notificaciones** desde dispositivos móviles (Android e iOS).

La aplicación se integra con múltiples APIs especializadas para proporcionar una experiencia completa de autogestión, conectándose con sistemas de **pagos bancarios**, **facturación TLS**, y **configuración dinámica**.

---

## Información del Proyecto

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo — Versión 3.3.1                  |
| **Rama**        | desarrollo-principal                    |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-10                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura y Stack Tecnológico

### 1.1 Frameworks Principales

#### **Angular 17**

- **Versión:** 17.3.12
- **Propósito:** Framework base para la aplicación
- **Documentación:** [Angular Documentation](https://angular.io/docs)
- **Características clave:**
  - **Standalone Components** para mejor modularidad
  - **Signals** para gestión reactiva de estado
  - **Server-Side Rendering** listo para producción

#### **Ionic 8**

- **Versión:** 8.3.3
- **Propósito:** Framework UI para componentes móviles
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/docs)
- **Características clave:**
  - Componentes nativos optimizados para móviles
  - **Ion Select**, **Ion Modal**, **Ion Toast** para UX nativa
  - Sistema de **theming** con variables CSS

#### **Capacitor 7**

- **Versión:** 7.1.0
- **Propósito:** Puente entre web y nativo
- **Documentación:** [Capacitor Documentation](https://capacitorjs.com/docs)
- **Plugins utilizados:**
  - `@capacitor/push-notifications` - Notificaciones push
  - `@capacitor/clipboard` - Portapapeles nativo
  - `@capacitor/filesystem` - Gestión de archivos
  - `@capacitor/share` - Compartir contenido nativo

### 1.2 Dependencias Clave

#### **Gestión de Estado y Datos**

- **Apollo Client** (`@apollo/client` v3.11.8) - Cliente GraphQL
  - [Documentación](https://www.apollographql.com/docs/react/)
  - Para consultas GraphQL y caché inteligente

- **RxJS** (v7.8.0) - Programación reactiva
  - [Documentación](https://rxjs.dev/)
  - Para manejo de streams asíncronos

#### **Procesamiento de Pagos**

- **Stripe** (`@stripe/stripe-js` v3.5.0, `ngx-stripe` v17.2.0)
  - [Documentación](https://stripe.com/docs/js)
  - Para procesamiento de pagos con tarjetas

- **PayPal** (`ngx-paypal` v11.0.0)
  - [Documentación](https://www.npmjs.com/package/ngx-paypal)
  - Integración con PayPal Checkout

#### **UI y Visualización**

- **ApexCharts** (v3.54.1) - Gráficos interactivos
  - [Documentación](https://apexcharts.com/docs/)
  - Para dashboards y visualización de datos

- **Swiper** (v9.4.1) - Carouseles y sliders
  - [Documentación](https://swiperjs.com/)
  - Para componentes de navegación táctil

#### **Utilidades**

- **Axios** (v1.7.7) - Cliente HTTP
  - [Documentación](https://axios-http.com/docs/intro)
  - Para llamadas API REST

- **SweetAlert2** (v11.15.10) - Alertas personalizadas
  - [Documentación](https://sweetalert2.github.io/)
  - Para modales de confirmación y notificaciones

- **Yup** (v1.4.0) - Validación de formularios
  - [Documentación](https://github.com/jquense/yup)
  - Para validación de datos de entrada

---

## 2. Estructura del Proyecto

### 2.1 Arquitectura de Carpetas

```
src/
├── app/
│   ├── graphql/            # Configuración GraphQL
│   ├── guards/              # Guards de rutas de Angular
│   ├── handlers/           # Manejadores de eventos
│   ├── interceptors/         # HTTP interceptors
│   ├── interfaces/          # Definiciones TypeScript
│   ├── layouts/             # Layouts reutilizables
│   ├── mock/               # Datos mock para desarrollo
│   ├── pages/               # Páginas principales de la app
│   ├── services/            # Servicios de API y lógica de negocio
│   ├── shared/              # Componentes reutilizables
│   ├── utils/              # Utilidades generales
│   └── validators/          # Validadores personalizados
├── assets/                  # Recursos estáticos
├── environments/            # Configuración de entornos
├── theme/                   # Variables CSS y temas
└── utils/                   # Utilidades globales
```

### 2.2 Páginas Principales

- **Login/Authentication** (signin.page.ts) - Gestión de identidad del usuario
- **Dashboard** (home.page.ts) - Vista principal con resumen de servicios y contratos
- **Billing** (payment-bill.page.ts) - Facturación y estado de cuenta
- **Payments** (make-payments.page.ts) - Procesamiento de pagos múltiples métodos
- **Services** (client-services.page.ts) - Gestión de servicios contratados
- **Support** (chat-sofia.page.ts) - Tickets y soporte técnico
- **Profile** (profile.page.ts) - Configuración de usuario y preferencias

---

## 3. Integración con APIs

### 3.1 API JSON (Configuración)

- **Base URL:** `https://apijsonnode.fibextelecom.lat`
- **Propósito:** Datos estáticos y configuración
- **Endpoints principales:**
  ```typescript
  GET / api / metodos - pago; // Métodos de pago disponibles
  GET / api / banners; // Banners promocionales
  GET / api / franquicias; // Franquicias bancarias
  GET / api / menu - app; // Navegación de la app
  ```

### 3.2 API TLS (Autenticación y Facturación)

- **Base URL:** `https://apijsonnode.fibextelecom.lat`
- **Propósito:** Operaciones seguras del usuario
- **Endpoints clave:**
  ```typescript
  POST / api / login; // Autenticación
  POST / api / factura; // Consulta de facturas
  POST / api / estado - cuenta; // Estado de cuenta
  POST / api / servicios; // Servicios contratados
  POST / api / tickets; // Gestión de soporte
  ```

### 3.3 API Gateway (Pagos)

- **Base URL:** `https://tlsnode.fibextelecom.lat`
- **Propósito:** Procesamiento de transacciones
- **Endpoints principales:**
  ```typescript
  POST / api / gateway / pg; // Procesamiento de pagos
  POST / api / gateway / auth; // Autenticación bancaria
  ```

---

## 4. Configuración y Desarrollo

### 4.1 Prerrequisitos

```bash
# Node.js 18+ requerido
node --version  # >= 18.0.0

# npm o yarn
npm --version  # >= 8.0.0

```

### 4.2 Instalación y Arranque

```bash
# 1. Clonar el repositorio
# bash
git clone --branch desarrollo-principal git@github.com:GrupoConex/Oficina_Movil_V2.git && cd Oficina_Movil_V2
# Ejecutar en dos pasos en CMD de Windows:
git clone --branch desarrollo-principal git@github.com:GrupoConex/Oficina_Movil_V2.git
cd Oficina_Movil_V2

# 2. Instalar dependencias
npm install

# 3. Variables de entorno
# Las variables de configuración ya están definidas en:
# - src/environments/environment.ts (desarrollo)
# - src/environments/environment.prod.ts (producción)
# Editar estos archivos según sea necesario para el entorno específico

# 4. Iniciar servidor de desarrollo
npm start
# o
ng serve

# 5. Para desarrollo móvil
npm run build
npx cap sync
npx cap open android    # o ios
```

### 4.3 Scripts Disponibles

```json
{
  "ng": "ng", // CLI de Angular
  "start": "ng serve", // Servidor de desarrollo
  "build": "ionic build --prod", // Build de producción
  "dev": "ionic s", // Modo desarrollo Ionic
  "test": "ng test", // Ejecutar pruebas unitarias
  "lint": "ng lint", // Análisis de código
  "format": "prettier --write", // Formatear código
  "cap": "npx ionic build && npx cap sync && npx cap open android"
}
```

---

## 5. Guía de Modificación

### 5.1 Añadir Nueva Página

```bash
# Generar página con Ionic CLI
ionic generate page pages/nueva-pagina

# O con Angular CLI
ng generate component pages/nueva-pagina
```

### 5.2 Crear Nuevo Servicio

```bash
# Generar servicio
ng generate service services/nuevo-servicio

# Estructura recomendada:
@Injectable({
  providedIn: 'root'
})
export class NuevoServicioService {
  constructor(private http: HttpClient) {}

  async MetodoNuevo(): Promise<TipoRespuesta> {
    // Lógica del servicio
  }
}
```

### 5.3 Añadir Nuevo Componente Compartido

```bash
# Generar componente standalone
ng generate component shared/components/nuevo-componente --standalone

# En el componente:
@Component({
  selector: 'app-nuevo-componente',
  standalone: true,
  imports: [CommonModule, IonicModule],
  templateUrl: './nuevo-componente.component.html',
  styleUrls: ['./nuevo-componente.component.scss']
})
```

### 5.4 Gestión de Estados

```typescript
// Usar Signals para estado reactivo
private estadoSignal = signal<TipoEstado>(valorInicial);

// En plantilla:
{{ estadoSignal() }}

// Actualizar estado:
this.estadoSignal.set(nuevoValor);
```

---

## 6. Buenas Prácticas

### 6.1 Código

- **TypeScript estricto** para tipado robusto
- **Standalone Components** para mejor modularidad
- **Signals** sobre BehaviorSubjects para estado reactivo
- **Lazy loading** de páginas para mejor rendimiento
- **Unit testing** para componentes

### 6.2 Estilos

- **Variables CSS** para theming consistente
- **Tailwind CSS** para utilidades rápidas
- **Component-scoped styles** para encapsulación

### 6.3 Testing

```bash
# Ejecutar pruebas unitarias
npm test

# Con cobertura
ng test --code-coverage

```

---

## 7. Despliegue

### 7.1 Build de Producción

```bash
# Build optimizado
npm run build

# Generar assets para móviles
npm run generate-assets

# Sincronizar con Capacitor
npx cap sync
```

### 7.2 Plataformas

#### **Android**

```bash
npx cap open android
# En Android Studio: Build > Generate Signed Bundle/APK
```

#### **iOS**

```bash
npx cap open ios
# En Xcode: Product > Archive
```

#### **Web (PWA)**

```bash
# El build en www/ es una PWA lista para desplegar
# Subir a cualquier servidor web estático
```

---

## 8. Monitoreo y Debug

### 8.1 Herramientas de Desarrollo

- **Chrome DevTools** para debugging web
- **Safari Web Inspector** para debugging iOS
- **Android Studio Debugger** para debugging Android
- **Capacitor DevApp** para testing rápido

### 8.2 Logs y Errores

```typescript
// Logging básico utilizado en la aplicación
console.error(error); // Para errores
console.log('Mensaje informativo'); // Para desarrollo

// Nota: En producción los console.log son deshabilitados
// Ver main.ts líneas 68-70
```

---

## 9. Seguridad

### 9.2 Variables de Entorno

```typescript
// environments/environment.ts (desarrollo)
export const environment = {
  production: false,
  isDev: true,
  version: '3.3.42',
  url_backend: 'https://tlsnode.fibextelecom.lat/',
  urlApiJson: 'https://apijsonnode.fibextelecom.lat',
  gatewaypay: 'https://gateway.fibextelecom.info/',
  // ... muchas más configuraciones
};

// environments/environment.prod.ts (producción)
export const environment = {
  production: true,
  isDev: true,
  version: '3.3.42',
  url_backend: 'https://tlsnode.fibextelecom.lat/',
  urlApiJson: 'https://apijsonnode.fibextelecom.info/',
  gatewaypay: 'https://gateway.fibextelecom.info/',
  // ... configuraciones de producción
};
```

**Nota:** Los archivos contienen numerosas configuraciones adicionales (tokens, URLs de servicios, claves de API bancarias, configuraciones de OneSignal, etc.). Ver los archivos completos para todas las variables disponibles.

---

## 10. Sugerencias Próximos Pasos y Roadmap

### 10.1 Features en Desarrollo

- **Biometric Authentication** con Face ID/Touch ID
- **Offline Mode** para funcionalidades críticas
- **Push Notifications** avanzadas con segmentación
- **Analytics Dashboard** para métricas de uso

### 10.2 Mejoras Técnicas

- **Micro-frontends** para mejor escalabilidad
- **Service Workers** para caching inteligente
- **GraphQL Subscriptions** para tiempo real
- **Automated Testing** con Cypress

---

## 11. Contribución

### 11.1 Flujo de Trabajo

1. **Crear rama feature** desde `desarrollo-principal`
2. **Desarrollar** siguiendo las buenas prácticas
3. **Testing** unitario y de integración
4. **Pull Request** con descripción detallada
5. **Code Review** por al menos otro desarrollador
6. **Merge** a `desarrollo-principal` tras aprobación

### 11.2 Estándares de Código

- **ESLint** para calidad de código
- **Prettier** para formato consistente
- **Conventional Commits** para mensajes claros
- **TypeScript strict mode** para robustez
- **Unit Testing** robusto con Jasmine y Karma

## 13. Licencia

Este proyecto es propiedad intelectual de **Fibex Telecom C.A.** Todos los derechos reservados.

© 2026 Fibex Telecom. Documentación actualizada: 2026-04-10
