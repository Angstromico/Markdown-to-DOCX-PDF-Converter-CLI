# RFC: Payment Now Page - Sistema de Pagos Múltiples

## Introducción

La **Payment Now Page** es el componente central de procesamiento de pagos de la aplicación **Oficina Móvil V2** que facilita el pago de servicios Fibex a través de múltiples métodos de pago nacionales e internacionales. Esta página implementa un sistema multi-step basado en acordeón que guía al usuario a través de diferentes etapas: selección de monto, elección de método de pago, y procesamiento de transacciones con pasarelas de pago externas.

Este RFC documenta la arquitectura técnica, flujo de usuario, métodos de pago disponibles y consideraciones de implementación de la página de pagos, que sirve como gateway principal para todas las transacciones financieras del ecosistema Fibex.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/payment-now.png" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | PaymentNowPage (src/app/pages/payment-now/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/payment-now/
    payment-now.page.ts          # Componente principal con lógica de pagos
    payment-now.page.html        # Template con acordeón de 3 pasos
    payment-now.page.scss        # Estilos específicos del componente
    payment-now.page.spec.ts     # Pruebas unitarias
    payment-now-routing.module.ts # Configuración de rutas
    payment-now.module.ts        # Módulo Angular con dependencias
    
    # Subcomponentes de métodos de pago
    paypal/
        paypal.component.ts        # Integración con PayPal
        paypal.component.html      # Template PayPal
        paypal.component.scss      # Estilos PayPal
    stripe/
        stripe.component.ts        # Integración con Stripe
        stripe.component.html      # Template Stripe
        stripe.component.scss      # Estilos Stripe
    mercantil/
        mercantil.component.ts     # Pagos Mercantil (TDD, C2P, Pago Móvil)
        mercantil.component.html   # Template Mercantil
        mercantil.component.scss   # Estilos Mercantil
    bnc/
        bnc.component.ts          # Pagos Banco Nacional de Crédito
        bnc.component.html        # Template BNC
        bnc.component.scss        # Estilos BNC
    banco100/
        banco100.component.ts      # Pagos 100% Banco
        banco100.component.html    # Template 100% Banco
        banco100.component.scss    # Estilos 100% Banco
    banco-r4/
        banco-r4.component.ts     # Pagos Banco R4
        banco-r4.component.html   # Template R4
        banco-r4.component.scss   # Estilos R4
    zelle/
        zelle.component.ts        # Pagos Zelle
        zelle.component.html      # Template Zelle
        zelle.component.scss      # Estilos Zelle
```

### 1.2 Dependencias Externas

#### **@ngx-stripe/stripe-js**
- **Propósito:** Integración con pasarela de pago Stripe para tarjetas internacionales
- **Configuración:** Token de API en environment, elementos de tarjeta seguros
- **Integración:** Mediante `StripeCardComponent` con validación en tiempo real
- **Documentación:** [Stripe.js Documentation](https://stripe.com/docs/js)

#### **@ngx-paypal/core**
- **Propósito:** Integración con pasarela de pago PayPal
- **Configuración:** Client ID, moneda USD, comisión del 5.5%
- **Integración:** Mediante `NgxPayPalModule` con botón de pago personalizado
- **Documentación:** [PayPal SDK Documentation](https://developer.paypal.com/docs/business/javascript-sdk/)

#### **Angular Forms**
- **ReactiveFormsModule:** Para gestión de formularios reactivos de pago
- **FormsModule:** Para formularios template-driven
- **Validaciones:** Validators para montos, números de tarjeta, fechas
- **Documentación:** [Angular Forms Documentation](https://angular.dev/guide/forms)

#### **Ionic Framework**
- **ModalController:** Para modales de confirmación de pago
- **LoadingController:** Para indicadores de carga durante procesamiento
- **NavController:** Para navegación entre pasos del acordeón
- **Documentación:** [Ionic Framework Documentation](https://ionicframework.com/)

---

## 2. Flujo de Usuario y Estados de Navegación

### 2.1 Arquitectura Multi-Step

La página implementa 3 pasos principales mediante un sistema de acordeón:

#### **Paso 1: Información de Monto**
- **Componente:** Balance card con monto a pagar
- **Propósito:** Mostrar saldo pendiente o saldo a favor
- **Features:** 
  - Toggle entre USD/Bs con tasa de cambio en tiempo real
  - Botón de edición de monto
  - Visualización de suscripción mensual
  - Historial de últimos pagos

#### **Paso 2: Selección de Método de Pago**
- **Estado Dual:** Selección de pagos frecuentes o todos los métodos
- **Componentes:** 
  - Pagos frecuentes guardados del usuario
  - Grid de métodos de pago disponibles
  - Opción "Otros" para métodos no frecuentes

#### **Paso 3: Detalles del Pago**
- **Estado Dinámico:** Componente específico según método seleccionado
- **Componentes Posibles:** 
  - `app-paypal` (ID: 2)
  - `app-stripe` (ID: 3)
  - `app-mercantil` (ID: 4, 5, 6)
  - `app-bnc` (Débito)
  - `app-banco100` (C2P)
  - `app-banco-r4` (C2P)

---

## 3. Implementación Técnica

### 3.1 Gestión de Estados

#### **Propiedades Principales**
```typescript
// Estados del acordeón
public accordionActiveStep: number = 1;
public accordionMaxStep: number = 1;
public accordionExpanded: boolean = true;

// Datos de usuario y contrato
public user: ItmAbonadoTable | null = null;
public contrato: ItmContratoTable | null = null;

// Estados de pago
public selectedPaymentType: IPaymentType | undefined;
public debitPaymentType: IPaymentType | undefined;
public c2pPaymentType: IPaymentType | undefined;

// Estados financieros
public currentBalanceBs: number = 0;
public currentBalanceUSD: number = 0;
public favorMountBs: number = 0;
public favorMountUSD: number = 0;

// Pagos frecuentes
public pagosFrecuentes: any[] = [];
public frequentPaymentsList: ICardItem[] = [];
```

#### **Control de Acordeón**
```typescript
onAccordionHeaderClick(step: number) {
  if (this.canOpenAccordionStep(step)) {
    if (this.accordionActiveStep === step) {
      this.accordionExpanded = !this.accordionExpanded;
    } else {
      this.accordionActiveStep = step;
      this.accordionExpanded = true;
      
      // Lógica específica por paso
      if (step === 2) {
        if (this.pagosFrecuentes && this.pagosFrecuentes.length > 0) {
          this.activeStep = 1.9; // Paso especial para pagos frecuentes
        } else {
          this.activeStep = 2;
        }
      }
    }
  }
}
```

### 3.2 Manejo de Métodos de Pago

#### **Selección de Método**
```typescript
public selectPaymentType(paymentType: ICardItem) {
  this.selectedPaymentType = paymentType;
  
  // Configurar datos del usuario para el pago
  this.datauserpayment = {
    name: this.user?.nombres_abonado + ' ' + this.user?.apellidos_abonado,
    cedula: this.user?.cedula_abonado,
    contrato: this.contrato?.nro_abonado,
    idcontrato: this.contrato?.id_contrato_adm,
    monto: this.currentBalanceBs.toString(),
  };
  
  // Avanzar al paso 3 (formulario de pago)
  this.activeStep = 3;
}
```

#### **Pagos Frecuentes**
```typescript
public async checkFrequentPayments() {
  if (!this.user || !this.user.id_abonado) return;
  
  try {
    this.pagosFrecuentes = await this.transferenciaService.getFrequentPayments(
      String(this.user.id_abonado),
    );
    
    this.frequentPaymentsList = this.pagosFrecuentes.map(p => ({
      id: p.id!,
      title: p.metodo_pago,
      image: this.getIconForPayment(p),
      value: JSON.stringify(p),
    }));
  } catch (error) {
    console.error('Error cargando pagos frecuentes', error);
    this.pagosFrecuentes = [];
  }
}
```

---

## 4. Componentes de Pago Integrados

### 4.1 Componentes Internacionales

#### **PayPalComponent**
- **Ruta:** `src/app/pages/payment-now/paypal/paypal.component`
- **Propósito:** Procesamiento de pagos vía PayPal
- **Features:** 
  - Integración con SDK de PayPal
  - Cálculo automático de comisión (5.5% + $0.30)
  - Validación de monto mínimo
  - Confirmación de pago con referencia

#### **StripeComponent**
- **Ruta:** `src/app/pages/payment-now/stripe/stripe.component`
- **Propósito:** Procesamiento de tarjetas de crédito internacionales
- **Features:** 
  - Elementos de tarjeta seguros (PCI compliance)
  - Validación en tiempo real
  - Soporte para Visa, MasterCard, Amex, Discover
  - Tokenización de datos de tarjeta

### 4.2 Componentes Nacionales

#### **MercantilComponent**
- **Ruta:** `src/app/pages/payment-now/mercantil/mercantil.component`
- **Propósito:** Pagos vía Banco Mercantil (múltiples modalidades)
- **Modalidades:** 
  - TDD (Transferencia Débito Directo)
  - C2P (Click to Pay)
  - Pago Móvil Mercantil
- **Features:** Validación OCR, generación de referencias

#### **BNCComponent**
- **Ruta:** `src/app/pages/payment-now/bnc/bnc.component`
- **Propósito:** Pagos vía Banco Nacional de Crédito
- **Features:** Formulario de débito, validación de cuenta

#### **Banco100Component**
- **Ruta:** `src/app/pages/payment-now/banco100/banco100.component`
- **Propósito:** Pagos vía 100% Banco
- **Features:** C2P, validación de datos bancarios

#### **BancoR4Component**
- **Ruta:** `src/app/pages/payment-now/banco-r4/banco-r4.component`
- **Propósito:** Pagos vía Banco R4
- **Features:** C2P, formulario de pago móvil

---

## 5. Integración con Servicios

### 5.1 Servicios Principales

#### **TransferenciaService**
- **Propósito:** Gestión de transferencias y pagos frecuentes
- **Métodos clave:** `getFrequentPayments()`, `savePayment()`
- **APIs:** Endpoints para guardar y recuperar métodos de pago

#### **UserService**
- **Propósito:** Gestión de datos de usuario y contratos
- **Métodos clave:** `GetUserPromise()`, `GetServicios()`
- **Estados:** `user`, `contrato`, `servicios`

#### **ApiJsonService**
- **Propósito:** Obtener métodos de pago disponibles
- **Métodos clave:** `GetMetodosPagos()`, `requestPaymentMethods()`
- **Datos:** Tipos de pago, listas de bancos, configuración regional

#### **TasaMonedaService**
- **Propósito:** Conversión entre USD/Bs en tiempo real
- **Métodos clave:** `updateTasa()`, `tasaDollar`
- **Actualización:** Cada vez que se carga la página

#### **MonitorService**
- **Propósito:** Monitoreo de eventos de pago
- **Métodos clave:** `UseMonitoreo()`
- **Tracking:** Eventos de usuario, conversiones, errores

### 5.2 Integración con APIs Externas

#### **PayPal API**
```typescript
// Configuración del SDK
this.payPalConfig = {
  style: {
    layout: 'vertical',
    color: 'blue',
    shape: 'rect',
    label: 'paypal'
  },
  onApprove: (data) => {
    this.processPayPalPayment(data);
  },
  onError: (err) => {
    this.handlePaymentError(err);
  }
};
```

#### **Stripe API**
```typescript
// Configuración de elementos
const elementsOptions: StripeElementsOptions = {
  mode: 'payment',
  amount: this.saldo * 100, // Convertir a centavos
  currency: 'usd',
  appearance: {
    theme: 'stripe'
  }
};

// Creación de payment intent
const paymentIntent = await this.stripe.createPaymentIntent({
  amount: this.saldo * 100,
  currency: 'usd',
  metadata: {
    user_id: this.user?.id_abonado,
    contract_id: this.contrato?.id_contrato
  }
});
```

---

## 6. Estilos y Diseño Visual

### 6.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.payment-now-container-all {
  padding: 1rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.balance-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.payment-types-slider {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.accordion-item {
  background: white;
  border: none;
  border-radius: 12px;
  margin-bottom: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}
```

#### **Diseño Responsivo**
- **Grid Adaptativo:** Métodos de pago se ajustan al tamaño de pantalla
- **Acordeón Collapsible:** Optimizado para dispositivos móviles
- **Animaciones Suaves:** Transiciones entre pasos con fade effects

### 6.2 Optimizaciones de UI

- **Loading States:** Indicadores durante procesamiento de pagos
- **Error Handling:** Retroalimentación visual clara para errores
- **Success States:** Confirmación visual de pagos completados
- **Progress Indicators:** Barra de progreso en acordeón

---

## 7. Flujo de Pago Detallado

### 7.1 Caminos Principales

#### **Usuario con Saldo Pendiente**
1. Paso 1: Visualizar monto a pagar
2. Paso 2: Seleccionar método de pago (frecuentes o todos)
3. Paso 3: Completar formulario de pago específico
4. Confirmación y procesamiento
5. Redirección a página de éxito

#### **Usuario con Saldo a Favor**
1. Paso 1: Visualizar monto a favor
2. Opción de edición de monto
3. Continuar con flujo normal de pago

#### **Usuario con Pagos Frecuentes**
1. Paso 1: Visualizar monto
2. Paso 2: Selección rápida de pago frecuente
3. Paso 3: Formulario pre-completado
4. Confirmación rápida

### 7.2 Estados de Error y Recuperación

- **Pago Fallido:** Manejo de errores con opciones de reintentar
- **Método No Disponible:** Retroalimentación y sugerencia de alternativas
- **Validación Fallida:** Mensajes específicos por tipo de error
- **Timeout:** Manejo de timeouts de conexión

---

## 8. Consideraciones de Seguridad

### 8.1 Validaciones de Entrada

- **Monto:** Validación de rango y formato numérico
- **Tarjeta:** Validación de número, fecha, CVV
- **Cuenta Bancaria:** Validación de formato y longitud
- **Datos Personales:** Sanitización contra XSS

### 8.2 Manejo de Datos Sensibles

- **Tokenización:** Datos de tarjeta nunca almacenados en servidor
- **HTTPS:** Todas las comunicaciones cifradas
- **PCI Compliance:** Integración con pasarelas certificadas
- **Audit Trail:** Registro de todos los eventos de pago

---

## 9. Testing y Calidad

### 9.1 Casos de Uso Críticos

1. **Flujo completo PayPal**
2. **Flujo completo Stripe**
3. **Flujo completo Mercantil TDD**
4. **Flujo completo Mercantil C2P**
5. **Pagos frecuentes**
6. **Conversión de moneda**
7. **Manejo de errores de red**
8. **Validación de formularios**

### 9.2 Pruebas Unitarias Requeridas

- Validación de montos y conversiones
- Selección de métodos de pago
- Integración con APIs externas
- Manejo de estados del acordeón
- Procesamiento de errores
- Guardado de pagos frecuentes

---

## 10. Consideraciones de Performance

### 10.1 Optimizaciones Implementadas

1. **Lazy Loading:** Componentes de pago cargados bajo demanda
2. **Caching:** Métodos de pago frecuentes cacheados localmente
3. **Debouncing:** Validaciones de formularios con debounce
4. **Image Optimization:** Iconos de bancos optimizados

### 10.2 Manejo de Memoria

```typescript
ngOnDestroy(): void {
  this.activeStep = 1;
  this.subscriptionContrato?.unsubscribe();
  // Limpieza de timeouts
  if (this.clickStepTimeout) {
    clearTimeout(this.clickStepTimeout);
  }
}
```

---

## 11. APIs Externas Documentadas

### 11.1 PayPal JavaScript SDK

- **URL:** https://developer.paypal.com/docs/business/javascript-sdk/
- **Propósito:** Procesamiento de pagos internacionales vía PayPal
- **Uso en la aplicación:** 
  - Botones de pago personalizados
  - Procesamiento de pagos con comisión
  - Manejo de aprobaciones y errores
- **Características:** 
  - Soporte para tarjetas de crédito y débito
  - Cuentas PayPal balance
  - Compra en cuotas (disponible en algunos países)

### 11.2 Stripe.js API

- **URL:** https://stripe.com/docs/js
- **Propósito:** Procesamiento de pagos con tarjetas internacionales
- **Uso en la aplicación:** 
  - Elementos de tarjeta seguros
  - Creación de payment intents
  - Confirmación de pagos
- **Características:** 
  - Validación en tiempo real
  - Soporte multi-método (Visa, MC, Amex, Discover)
  - 3D Secure authentication
  - Tokenización PCI compliant

### 11.3 APIs Bancarias Nacionales

- **Mercantil Gateway:** Integración para pagos TDD, C2P, Pago Móvil
- **BNC Gateway:** Pagos vía débito bancario
- **100% Banco:** Transferencias bancarias online
- **Banco R4:** Pagos móviles y C2P

---

## 12. Mejoras Futuras Sugeridas

### 12.1 Features Potenciales

1. **Apple Pay / Google Pay:** Pagos con billeteras digitales
2. **Criptomonedas:** Soporte para pagos con Bitcoin, Ethereum
3. **Split Payments:** Dividir pagos entre múltiples métodos
4. **Payment Plans:** Planes de pago a plazos
5. **International Expansion:** Soporte para más países y monedas

### 12.2 Optimizaciones Técnicas

1. **Service Workers:** Soporte offline para pagos frecuentes
2. **Biometric Authentication:** Huella dactilar para autorización rápida
3. **Machine Learning:** Detección de fraudes en tiempo real
4. **Progressive Web App:** Mejoras de rendimiento
5. **Real-time Notifications:** Estado de pagos en tiempo real

---

## 13. Notas para Mantenimiento

### 13.1 Puntos Críticos

1. **API Keys:** Rotación regular de tokens de APIs externas
2. **Tasas de Cambio:** Actualización diaria de tasa USD/Bs
3. **Compliance:** Mantener cumplimiento PCI y regulaciones
4. **Error Monitoring:** Monitoreo constante de tasas de error
5. **Performance:** Optimización de tiempos de carga

### 13.2 Buenas Prácticas

- Mantener versiones actualizadas de SDKs externos
- Implementar proper error handling para cada método de pago
- Documentar cambios en APIs externas
- Realizar testing de regresión para cada nuevo método
- Mantener auditoría de seguridad regular

---

## 14. Conclusión

La Payment Now Page representa un componente crítico y complejo en la arquitectura de Oficina Móvil. Su implementación multi-step mediante acordeón permite manejar múltiples métodos de pago de manera eficiente y segura, desde pagos internacionales (PayPal, Stripe) hasta métodos bancarios nacionales (Mercantil, BNC, 100% Banco, R4).

La arquitectura modular, la integración con múltiples pasarelas de pago y el manejo robusto de estados la convierten en un componente central que requiere especial atención durante el mantenimiento y evolución de la aplicación. Su diseño actual proporciona una base sólida para futuras mejoras y expansiones en el ecosistema de pagos Fibex.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
