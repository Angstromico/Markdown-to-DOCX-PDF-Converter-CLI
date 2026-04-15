# RFC: Payment Report Page - Sistema de Reporte de Pagos

## Introducción

La **Payment Report Page** es el componente especializado de la aplicación **Oficina Móvil V2** que gestiona el flujo completo de reporte de pagos para clientes de **Fibex Telecom**. Esta página implementa un sistema multi-método para reportar pagos realizados a través de diferentes canales bancarios, incluyendo transferencias, pago móvil, Zelle y otros métodos de pago. Ofrece una experiencia guiada con validación de datos, procesamiento OCR para comprobantes, y seguimiento del estado de conciliación de pagos.

Este RFC documenta la arquitectura técnica, flujo de usuario, integración con APIs bancarias, procesamiento de comprobantes, y consideraciones de implementación del sistema de reporte de pagos, que representa una funcionalidad crítica para la gestión financiera y conciliación de pagos.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/payment-report.jpeg" alt="Payment Report Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | PaymentReportV2Page (src/app/pages/payment-report-v2/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-14                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/payment-report-v2/
    payment-report-v2.page.ts          # Componente principal con lógica de reporte
    payment-report-v2.page.html        # Template con flujo multi-step
    payment-report-v2.page.scss        # Estilos específicos del componente
    payment-report-v2.page.spec.ts     # Pruebas unitarias
    payment-report-v2-routing.module.ts # Configuración de rutas
    payment-report-v2.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Axios v1.7.7**
- **Propósito:** Cliente HTTP para peticiones a APIs externas
- **Uso:** Comunicación con APIs bancarias y servicios de reporte
- **Integración:** `import { AxiosError } from 'axios'`
- **Documentación:** [Axios Documentation](https://axios-http.com/)

#### **RxJS v7.8.0**
- **Propósito:** Gestión reactiva de suscripciones a cambios de contrato
- **Uso:** Subscriptions a UserService y actualizaciones de estado
- **Documentación:** [RxJS Documentation](https://rxjs.dev/)

#### **Angular Forms**
- **ReactiveFormsModule:** Para gestión de formularios reactivos
- **FormsModule:** Para formularios template-driven
- **Validaciones:** Manejo de estados de formulario
- **Documentación:** [Angular Forms Documentation](https://angular.dev/guide/forms)

---

## 2. Flujo de Usuario y Estados

### 2.1 Estados Principales del Sistema

#### **Estado Cuenta Exonerada**
- **Condición:** `contrato?.nombre_g_a === 'EXONERADO'`
- **UI:** Mensaje informativo y botón para mejorar plan
- **Acción:** Redirección a `tabs/plan-upgrade`

#### **Estado Pago Reportado Exitosamente**
- **Condición:** `billListRecipe` existe
- **UI:** Confirmación de pago reportado
- **Acción:** Mostrar detalles del pago y opciones de navegación

#### **Estado Pagos en Proceso**
- **Condición:** `DataPay && DataPay.length && !forceReport`
- **UI:** Lista de pagos pendientes de conciliación
- **Acción:** Opción para reportar nuevo pago

#### **Estado Formulario de Reporte**
- **Condición:** Ninguna de las anteriores
- **UI:** Acordeón multi-step para reportar pago
- **Acción:** Proceso completo de reporte

### 2.2 Flujo de Reporte

1. **Selección de Método:** Elección del tipo de pago (Transferencia, Pago Móvil, Zelle)
2. **Captura de Datos:** Formularios específicos por método
3. **Validación:** Verificación de datos y comprobantes
4. **Procesamiento:** Envío a APIs correspondientes
5. **Confirmación:** Estado de conciliación y seguimiento

---

## 3. Implementación Técnica

### 3.1 Propiedades Principales

```typescript
// Datos del usuario y contrato
public user: ItmAbonadoTable | null = null;
public contrato: ItmContratoTable | null = null;

// Datos de pagos
public DataPay: IPaymentExistent[] | null = null;
public billList: IGenericBill[] = [];
public billListRecipe: IGenericBill | null = null;

// Estado del flujo
public canPay: boolean = true;
public canReport: boolean = false;
public forceReport: boolean = false;
public isNational: boolean = true;
public isPaymentConciliated: boolean = false;

// Estructura del formulario
public structure: IFormStep[] = [];
public selectedReportType: ISlidingItem | undefined;

// Lista de bancos
public ListBank: BankReport[] = [];
public ListBankEmisor: IBankEmisor[] = [];
public ListBankDefault: BankReport[] = [];
```

### 3.2 Diccionario de Bancos

```typescript
readonly BANCOS_VENEZUELA = {
  '0102': 'Banco de Venezuela',
  '0104': 'Banco Venezolano de Crédito',
  '0105': 'Banco Mercantil',
  '0108': 'BBVA Banco Provincial',
  '0114': 'Bancaribe',
  '0115': 'Banco Exterior',
  '0128': 'Banco Caroní',
  '0134': 'Banesco',
  '0137': 'Banco Sofitasa',
  '0138': 'Banco Plaza',
  '0151': 'Banco Fondo Común (BFC)',
  '0156': '100% Banco',
  '0157': 'Del Sur',
  '0163': 'Banco del Tesoro',
  '0168': 'BanCrecer, Banco de Desarrolo',
  '0169': 'Mi banco, Banco Microfinanciero, C.A.',
  '0171': 'Banco Activo',
  '0172': 'Bancamiga Banco Universal, C.A.',
  '0174': 'BanPlus, Banco Comercial',
  '0175': 'Banco Bicentenario Banco Universal, C.A.',
  '0177': 'Banco de las Fuerzas Armadas',
  '0191': 'Banco Nacional de Crédito, C.A. Banco Universal',
} as const;
```

### 3.3 Gestión de Ciclo de Vida

```typescript
ionViewWillEnter() {
  this.networkService.validateNetworkAccess();
  this.billListRecipe = null;
  this.ViewEntered = true;
  this.resetAccordionState();
  this.canPay = true;
  
  this.subscriptionContrato = this.userService.GetContratoSelected()
    .subscribe(contrato => {
      Promise.all([
        this.userService.GetServicios(),
        this.userService.GetUserPromise(),
        this.tasaService.updateTasa(),
      ])
        .then(async ([servicios, user]) => {
          const resetForm = Boolean(
            this.contrato && contrato && this.contrato.id_contrato !== contrato.id_contrato,
          );
          
          this.contrato = contrato;
          this.user = user;
          this.initFormLoad(resetForm);
          
          // Validar estado exonerado
          this.canPay = contrato?.nombre_g_a === 'EXONERADO' ? false : true;
          
          // Validar estado suspendido/cortado
          if (contrato?.estatus_contrato == 'SUSPENDIDO' || contrato?.estatus_contrato == 'CORTADO') {
            this.showSuspendedServiceModal();
          }
        });
    });
}
```

---

## 4. Integración con Servicios

### 4.1 Servicios Principales

#### **ApiJsonService**
- **Propósito:** Gestión de APIs JSON para métodos de pago
- **Métodos clave:** 
  - `GetMetodosPagos()` - Obtener métodos de pago disponibles
  - `requestPaymentMethods()` - Solicitar métodos por franquicia
- **API:** Endpoints para configuración de pagos

#### **TransferenciaService**
- **Propósito:** Gestión de transferencias bancarias
- **Métodos:** `ListBank()` - Listado de bancos disponibles
- **Integración:** Diccionario de bancos venezolanos

#### **UserService**
- **Propósito:** Gestión de datos de usuario y contrato
- **Métodos:** `GetContratoSelected()`, `GetUserPromise()`, `getInternetService()`
- **Integración:** Subscripción reactiva a cambios de contrato

#### **SaeReportService**
- **Propósito:** Gestión de reportes SAE (Sistema Administrativo)
- **Métodos:** Procesamiento de reportes financieros
- **API:** Integración con sistema contable

#### **TasaMonedaService**
- **Propósito:** Conversión de divisas y tasa de cambio
- **Métodos:** `updateTasa()` para actualizar tasa dólar/bolívar
- **Uso:** Cálculo de montos en diferentes monedas

#### **DialogsService**
- **Propósito:** Gestión de modales y alertas
- **Métodos:** `showAlert()`, `showPinDialog()`, `showLoader()`
- **Uso:** Confirmación de reporte, estados de carga

### 4.2 Servicios de Utilidad

#### **NetworkStatusService**
- **Propósito:** Validación de conectividad a internet
- **Métodos:** `validateNetworkAccess()`
- **Importancia:** Prevención de errores por falta de conexión

#### **MonitorService**
- **Propósito:** Monitoreo y analítica de uso
- **Métodos:** `UseMonitoreo()` para tracking
- **Uso:** Métricas de uso del sistema de reporte

#### **AnalyticsService**
- **Propósito:** Análisis de comportamiento de usuario
- **Uso:** Tracking de eventos de reporte de pagos

#### **DriverServicesBanksService**
- **Propósito:** Servicios específicos para bancos
- **Integración:** APIs bancarias personalizadas

---

## 5. Componentes Compartidos Integrados

### 5.1 ContentHeaderComponent
- **Ruta:** `src/app/shared/components/headers/content-header/content-header.component`
- **Propósito:** Header dinámico con navegación personalizada
- **Props:** `title`, `goBackFunction` personalizada
- **Uso:** Navegación condicional según estado

### 5.2 FormStepperComponent
- **Ruta:** `src/app/shared/components/inputs/form-stepper/form-stepper.component`
- **Propósito:** Formulario multi-step con validación
- **Props:** `formStepper`, `onSubmit`, `isReport`, `OCRFormFieldIds`
- **Eventos:** `onInputChange`, `onStepChanged`, `uploadOCRFormEvent`

### 5.3 GenericBillComponent
- **Ruta:** `src/app/shared/components/cards/generic-bill/generic-bill.component`
- **Propósito:** Visualización de recibos y comprobantes
- **Props:** `billItem`, `isListView`
- **Uso:** Mostrar detalles de pagos reportados

---

## 6. Flujo de Procesamiento de Pagos

### 6.1 Inicialización del Formulario

```typescript
public initFormLoad = (forceReset?: boolean) => {
  try {
    this.route.queryParams.subscribe(params => {
      const typeReportParams = params['type_report'];
      const directBDV = params['direct_bdv'] === 'true';
      const directR4 = params['direct_r4'] === 'true';
      
      // Configuración automática según parámetros
      if (directBDV && typeReportParams === '3') {
        this.selectedPaymentType = 'bdv';
      }
      if (directR4 && typeReportParams === '3') {
        this.selectedPaymentType = 'r4';
      }
    });
    
    this.structure = [
      {
        step: 1,
        formInputs: [],
        hiddenNavBtns: true,
        onNext: data => {
          if (data['sliding-report-type'] == 'Pago Móvil') {
            return {
              type: 'modal',
              modal: 'info',
              title: 'Pago Móvil',
              text: '¿Ya realizaste el pago móvil o deseas pagar aquí?',
              buttons: [
                {
                  type: 'navigate',
                  label: 'Pagar aquí',
                  href: '/tabs/payment-now',
                  variant: 'outline',
                },
                {
                  type: 'next',
                  label: 'Reportar pago',
                },
              ],
            };
          }
        },
        getFormLoad: async () => {
          const [allReportCopyData, BanksAll, paymentExistent] = await Promise.all([
            this.apiJson.GetMetodosPagos(forceReset),
            this._transferenciaservice.ListBank(forceReset),
            this.PayPending(),
          ]);
          
          this.DataPay = paymentExistent.payments;
          this.canReport = paymentExistent.avariable;
          this.currentCopyBanksData = allReportCopyData.copyreportpaymentsdata;
          
          // Procesar pagos existentes
          this.billList = this.processPaymentList(this.DataPay, BanksAll);
          
          return this.structure;
        },
      },
    ];
  } catch (error) {
    console.error('Error en initFormLoad:', error);
  }
};
```

### 6.2 Procesamiento de Contenido Dinámico

```typescript
// Procesamiento de copyContent para pago móvil
processedCopyContent = processedCopyContent.map(copyItem => {
  if (typeof copyItem === 'string') {
    // Procesar número de teléfono
    if (copyItem.includes(':PHONE_NUMBER')) {
      const phoneNumberFormatted = this.user?.telefono_abonado
        ? `(${this.user.telefono_abonado.slice(0, 2)}*****${this.user.telefono_abonado.slice(-4)})`
        : '';
      return copyItem.replace(':PHONE_NUMBER', phoneNumberFormatted);
    }
    
    // Procesar cédula/DNI
    if (copyItem.includes('V-') && this.user?.cedula_abonado) {
      return copyItem.replace(/V-[A-Z0-9\-]+/gi, `V-${this.user.cedula_abonado}`);
    }
    
    // Procesar monto
    const saldoAPagar = this.balanceBs > 0 ? Math.abs(this.balanceBs).toFixed(2) : '0.00';
    if (copyItem.trim().toLowerCase().startsWith('monto:')) {
      return `Monto: ${saldoAPagar}`;
    }
  }
  return copyItem;
});
```

### 6.3 Formateo de Montos

```typescript
formatAmount(payment: IPaymentExistent) {
  return this.isNational === false
    ? payment.simbolo_moneda == 'USD' || payment.cambio_moneda == '1'
      ? `USD ${payment.monto_dep}`
      : `${payment.monto_dep} ${payment.simbolo_moneda || 'BS'}`
    : `${payment.monto_dep} ${payment.simbolo_moneda || 'BS'}`;
}

public get balanceBs(): number {
  return this.user && this.contrato
    ? parseFloat(Math.abs(this.tasaService.tasaDollar * this.contrato.saldo).toFixed(2))
    : 0;
}

public get balanceUSD(): number {
  return this.contrato ? Math.abs(this.contrato.saldo) : 0;
}
```

---

## 7. Sistema de Acordión Multi-Step

### 7.1 Gestión de Estados del Acordión

```typescript
public accordionActiveStep: number = 1;
public accordionMaxStep: number = 1;
public accordionExpanded: boolean = true;

public isAccordionActive(step: number): boolean {
  return this.accordionActiveStep === step && this.accordionExpanded;
}

public isAccordionCompleted(step: number): boolean {
  return step < this.accordionActiveStep;
}

public canOpenAccordionStep(step: number): boolean {
  return step <= this.accordionActiveStep + 1;
}

public onAccordionHeaderClick(step: number): void {
  if (this.isAccordionActive(step)) {
    this.accordionExpanded = !this.accordionExpanded;
  } else if (this.canOpenAccordionStep(step)) {
    this.accordionActiveStep = step;
    this.accordionExpanded = true;
  }
}
```

### 7.2 Progreso Visual

```typescript
public getAccordionProgressPercent(): string {
  const completedSteps = this.accordionActiveStep - 1;
  const totalSteps = this.structure.length;
  const progress = (completedSteps / totalSteps) * 100;
  return `${progress}%`;
}
```

---

## 8. Manejo de Estados Especiales

### 8.1 Estado de Servicio Suspendido

```typescript
if (contrato?.estatus_contrato == 'SUSPENDIDO' || contrato?.estatus_contrato == 'CORTADO') {
  if (this.show_payment_contrato !== contrato.id_contrato_adm) {
    this.show_payment_contrato = contrato.id_contrato_adm;
    this.formStepper.handleEventStep({
      type: 'modal',
      modal: 'info',
      title: '¡Información importante!',
      text: "Sus servicios están suspendidos actualmente. Para restaurarlos rápidamente, seleccione 'Pagar Ahora'.\n\nSi ya realizó un pago y desea reportarlo, presione 'Reportar pago existente'.",
      buttons: [
        {
          type: 'navigate',
          label: 'Pagar Ahora',
          href: '/tabs/payment-now',
        },
        {
          type: 'event',
          label: 'Reportar pago existente',
          onClick: 'void',
          variant: 'outline',
        },
      ],
    });
  }
}
```

### 8.2 Navegación Condicional

```typescript
public goToBack = () => {
  const directBDV = this.isDirectBDV || this.route.snapshot.queryParams['direct_bdv'] === 'true';
  const directR4 = this.isDirectR4 || this.route.snapshot.queryParams['direct_r4'] === 'true';
  
  if (directBDV || directR4) {
    this.router.navigate(['/tabs/payment-now'], {
      replaceUrl: true,
      state: { returnToC2P: true },
    });
    return;
  }
  
  if ((this.formStepper?.activeFormStep || 0) > 1) {
    this.isNational = true;
    this.formStepper.handleFormStep('prev');
  } else {
    this.utilService.onBack();
  }
};
```

---

## 9. Integración con APIs Externas

### 9.1 API de Métodos de Pago

- **Propósito:** Obtener configuración de métodos de pago
- **Endpoint:** `GET /api/metodos-pago`
- **Response:** Estructura con `copyreportpaymentsdata`, `paymenttypereport`, `c2pReport`

### 9.2 API de Bancos

- **Propósito:** Listado de bancos disponibles
- **Endpoint:** `GET /api/bancos`
- **Response:** `BankReport[]` con información bancaria

### 9.3 API de Pagos Pendientes

- **Propósito:** Obtener pagos pendientes de conciliación
- **Endpoint:** `GET /api/pagos-pendientes`
- **Response:** `IPaymentExistent[]` con detalles de pagos

### 9.4 API de Reporte SAE

- **Propósito:** Enviar reportes al sistema contable
- **Endpoint:** `POST /api/sae-reporte`
- **Payload:** Datos del pago y comprobante

---

## 10. Estilos y Diseño Visual

### 10.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.pending-pay-container {
  @apply flex justify-center text-justify flex-col border font-medium text-black;
  gap: 0.4rem !important;
  padding: 1rem !important;
  
  .payment-rev-title {
    @apply font-bold text-blue-500;
    font-size: 1.1rem !important;
  }
  
  .text-container {
    font-size: 0.9rem;
    text-wrap: pretty;
    text-align: center;
  }
}

.payment-report-accordion {
  .accordion-list {
    position: relative;
    
    .accordion-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      border-radius: 0.5rem;
      background: white;
      margin-bottom: 0.5rem;
      transition: all 0.3s ease;
      
      &.active {
        background: #f0f8ff;
        border: 1px solid #007bff;
      }
      
      &.completed {
        background: #f8fff8;
        border: 1px solid #28a745;
      }
    }
  }
}
```

#### **Animaciones y Transiciones**
```scss
.animated {
  &.fadeInRight {
    animation: fadeInRight 0.5s ease-in-out;
  }
  
  &.faster {
    animation-duration: 0.3s;
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
```

### 10.2 Diseño Responsivo

- **Mobile First:** Optimizado para dispositivos móviles
- **Touch Interactions:** Estados hover y active para táctil
- **Flexible Layout:** Flexbox para alineación de elementos
- **Progress Enhancement:** Mejoras progresivas para diferentes dispositivos

---

## 11. Consideraciones de Performance

### 11.1 Optimizaciones Implementadas

1. **Lazy Loading:** Carga bajo demanda de datos de bancos
2. **Subscription Management:** Cleanup apropiado de observables
3. **Error Boundaries:** Manejo robusto de errores
4. **Data Caching:** Cache local de métodos de pago
5. **Debouncing:** Prevención de múltiples solicitudes

### 11.2 Estrategias de Carga

```typescript
// Carga paralela de datos
const [allReportCopyData, BanksAll, paymentExistent] = await Promise.all([
  this.apiJson.GetMetodosPagos(forceReset),
  this._transferenciaservice.ListBank(forceReset),
  this.PayPending(),
]);
```

---

## 12. Testing y Calidad

### 12.1 Casos de Uso Críticos

1. **Flujo completo de reporte exitoso**
2. **Manejo de cuenta exonerada**
3. **Reporte de pago móvil con datos dinámicos**
4. **Procesamiento de OCR de comprobantes**
5. **Validación de datos bancarios**
6. **Conciliación de pagos múltiples**
7. **Navegación condicional según estado**
8. **Manejo de errores de API**

### 12.2 Pruebas Unitarias Requeridas

- Gestión de estados de usuario
- Procesamiento de contenido dinámico
- Validación de formularios
- Integración con APIs bancarias
- Manejo de errores de red
- Formateo de montos y fechas

---

## 13. Mejoras Futuras Sugeridas

### 13.1 Features Potenciales

1. **Real-time Updates:** WebSocket para actualizaciones de conciliación
2. **Advanced OCR:** Mejor reconocimiento de comprobantes
3. **AI Validation:** Sistema inteligente de validación de pagos
4. **Offline Support:** Modo offline para reporte básico
5. **Multi-language:** Soporte para múltiples idiomas

### 13.2 Optimizaciones Técnicas

1. **State Management:** Implementación con NgRx o Signals
2. **Virtual Scrolling:** Para listas largas de pagos
3. **Image Optimization:** Procesamiento eficiente de comprobantes
4. **Bundle Splitting:** Mejora de tiempo de carga

---

## 14. Notas para Mantenimiento

### 14.1 Puntos Críticos

1. **API Integration:** Mantener compatibilidad con APIs bancarias
2. **Data Validation:** Validación rigurosa de datos financieros
3. **Error Handling:** Logging estructurado para debugging
4. **Performance Monitoring:** Métricas de carga y procesamiento

### 14.2 Buenas Prácticas

- Mantener estados desacoplados y predecibles
- Implementar proper error handling y logging
- Validar todos los datos financieros
- Mantener consistencia en el diseño y UX
- Documentar cambios en la API y estructura de datos
- Actualizar diccionario de bancos regularmente

---

## 15. Conclusión

La Payment Report Page representa un componente crítico y complejo en la gestión financiera de Oficina Móvil. Su implementación combina validación de datos bancarios, procesamiento de comprobantes, integración con múltiples APIs, y una robusta gestión de estados para proporcionar una experiencia completa de reporte de pagos.

La arquitectura modular basada en servicios especializados permite una mantenibilidad escalable mientras proporciona una experiencia de usuario fluida y segura para el proceso de reporte financiero. El sistema de acordión multi-step, el procesamiento dinámico de contenido, y la integración con APIs bancarias la convierten en un componente fundamental para la operación financiera y satisfacción del cliente.

---

*Documentación actualizada: 2026-04-14*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
