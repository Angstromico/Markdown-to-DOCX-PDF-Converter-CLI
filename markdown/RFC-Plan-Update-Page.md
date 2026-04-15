# RFC: Plan Update Page - Sistema de Mejora de Planes

## Introducción

La **Plan Update Page** es el componente especializado de la aplicación **Oficina Móvil V2** que gestiona el flujo completo de mejora y cambio de planes de internet para clientes de **Fibex Telecom**. Esta página implementa un sistema completo de selección de planes, validación mediante PIN, confirmación de upgrade y gestión de estados de usuario deudor vs usuario activo. Ofrece una experiencia guiada para la transición entre diferentes niveles de servicio con validaciones de seguridad y animaciones interactivas.

Este RFC documenta la arquitectura técnica, flujo de usuario, gestión de estados, integración con APIs de upgrade y consideraciones de implementación del sistema de mejora de planes, que representa una funcionalidad crítica para la retención y upselling de clientes.

<p align="center">
  <img src="/home/memz/Repos/Oficina-Movil-Fibex/docs/images/plan-update.jpeg" alt="Plan Update Page Interface" width="300"/>
</p>

---

## Especificación Técnica

| Campo           | Valor                                   |
| --------------- | --------------------------------------- |
| **Estado**      | Activo - Versión 3.3.1                  |
| **Componente**  | PlanUpdatePage (src/app/pages/plan-update/) |
| **Autor**       | Manuel Morales                          |
| **Fecha**       | 2026-04-13                              |
| **App**         | Oficina Móvil (Oficina_Movil_V2) v3.3.1 |
| **Plataformas** | Android, iOS, Web (PWA)                 |

---

## 1. Arquitectura del Componente

### 1.1 Estructura de Archivos

```
src/app/pages/plan-update/
    plan-update.page.ts          # Componente principal con lógica de upgrade
    plan-update.page.html        # Template con flujo de selección de planes
    plan-update.page.scss        # Estilos específicos del componente
    plan-update.page.spec.ts     # Pruebas unitarias
    plan-update-routing.module.ts # Configuración de rutas
    plan-update.module.ts        # Módulo Angular con dependencias
```

### 1.2 Dependencias Externas

#### **Canvas-Confetti v1.9.3**
- **Propósito:** Animaciones de celebración para upgrades exitosos
- **Uso:** Efectos visuales cuando el usuario completa un upgrade
- **Integración:** `import confetti from 'canvas-confetti'`
- **Documentación:** [Canvas-Confetti Documentation](https://github.com/catdad/canvas-confetti)

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

#### **Estado Usuario Deudor**
- **Condición:** `contrato?.estatus_contrato !== 'ACTIVO' && (contrato?.saldo ?? 0) > 0`
- **UI:** Mensaje informativo y botón para pagar ahora
- **Acción:** Redirección a `tabs/payment-now`

#### **Estado Usuario Activo**
- **Condición:** `contrato?.estatus_contrato === 'ACTIVO'`
- **UI:** Selección de planes disponibles para upgrade
- **Acción:** Proceso de selección y confirmación de upgrade

#### **Estado Upgrade Exitoso**
- **Condición:** `isPlanChanged = true`
- **UI:** Celebración con confetti y mensaje de felicitación
- **Acción:** Actualización de servicios locales y notificación

### 2.2 Flujo de Upgrade

1. **Detección de Cambio:** Monitoreo de cambios en contrato
2. **Carga de Planes:** Obtener servicios disponibles desde API
3. **Selección:** Usuario elige plan superior
4. **Verificación:** Modal con PIN de seguridad
5. **Confirmación:** Aplicación del upgrade con efectos visuales
6. **Actualización:** Sincronización local y con backend

---

## 3. Implementación Técnica

### 3.1 Propiedades Principales

```typescript
// Datos del usuario y contrato
public contrato: ItmContratoTable | null = null;
public userData: ItmAbonadoTable | null = null;
public currentUserPlan?: IServicio;
public selectedPlanToUpgrade: IServicio | undefined;

// Estado del flujo
public availableServices: IServicio[] = [];
public isPlanChanged: boolean = false;
public isDebtorUser: boolean = false;
public isLoading: boolean = true;
public errorMsg: string = '';

// Configuración de banner
public bannerUrlImg: string = 'https://cms.fibextelecom.net/uploads/Oficina_Movil_V2_upgrade_jpg_cb171fe0f9.jpeg';
```

### 3.2 Gestión de Ciclo de Vida

```typescript
ionViewWillEnter() {
  try {
    this.networkService.validateNetworkAccess();
    this.startInitSub();
  } catch (error) {
    // Logging estructurado de errores
  }
}

ionViewDidLeave() {
  this.subscriptionContrato?.unsubscribe();
  this.isFirstLoaded = false;
}
```

### 3.3 Sistema de Subscripciones Reactivas

```typescript
private startInitSub = () => {
  this.subscriptionContrato = this.userService.GetContratoSelected()
    .subscribe(
      async contrato => {
        const contratoWasChanged = 
          !this.contrato || 
          (this.contrato && contrato && this.contrato?.nro_abonado !== contrato?.nro_abonado);
        
        this.contrato = contrato;
        this.userData = await this.userService.GetUserPromise();
        
        if (contratoWasChanged) {
          // Limpiar cache de upgrades anteriores
          const upgradeTable = await this.dbService.getUpgradeTable();
          await upgradeTable.delete();
          this.resetUpgradeDatas();
          
          // Evaluar estado del usuario
          this.isDebtorUser = 
            this.contrato?.estatus_contrato !== 'ACTIVO' && (this.contrato?.saldo ?? 0) > 0;
          
          this.loadInitPlanData();
        }
      },
      error => {
        this.setErrorMsg('Error al cambiar de cuenta. intente de nuevo más tarde');
      }
    );
};
```

---

## 4. Integración con Servicios

### 4.1 Servicios Principales

#### **UpgradePlanService**
- **Propósito:** Gestión de operaciones de upgrade de planes
- **Métodos clave:** 
  - `GetServiciosToUpgrade()` - Obtener planes disponibles
  - `GeneratePinVerification()` - Generar PIN de verificación
  - `RequestUpgrade()` - Ejecutar upgrade seleccionado
- **API:** Endpoint especializado para operaciones de upgrade

#### **UserService**
- **Propósito:** Gestión de datos de usuario y contrato actual
- **Métodos:** `GetContratoSelected()`, `GetUserPromise()`, `getInternetService()`
- **Integración:** Subscripción reactiva a cambios de contrato

#### **DbService**
- **Propósito:** Gestión local de cache de upgrades y servicios
- **Métodos:** `getUpgradeTable()`, `getServiciosTable()`
- **Uso:** Cache temporal de planes disponibles y estado de upgrade

#### **DialogsService**
- **Propósito:** Gestión de modales y alertas
- **Métodos:** `showAlert()`, `showPinDialog()`, `showLoader()`
- **Uso:** Confirmación de upgrade, verificación PIN, loading states

#### **TriesService**
- **Propósito:** Control de intentos de PIN fallidos
- **Métodos:** `getTries()`, `setTries()`
- **Lógica:** Bloqueo después de 3 intentos fallidos

### 4.2 Servicios de Utilidad

#### **NetworkStatusService**
- **Propósito:** Validación de conectividad a internet
- **Métodos:** `validateNetworkAccess()`
- **Importancia:** Prevención de errores por falta de conexión

#### **MenuService**
- **Propósito:** Control de animaciones de espacio y navegación
- **Métodos:** `stopSpaceAnimation()`
- **Uso:** Detener animaciones durante carga de planes

---

## 5. Componentes Compartidos Integrados

### 5.1 ContentHeaderComponent
- **Ruta:** `src/app/shared/components/headers/content-header/content-header.component`
- **Propósito:** Header estandarizado con título "Mejora tu plan de internet"
- **Props:** `title` para personalización del header

### 5.2 FormStepperComponent
- **Ruta:** `src/app/shared/components/inputs/form-stepper/form-stepper.component`
- **Propósito:** Formulario multi-step para solicitudes personalizadas
- **Props:** `formStepper` con configuración de pasos
- **Uso:** Cuando no hay planes predefinidos disponibles

---

## 6. Flujo de Validación y Seguridad

### 6.1 Sistema de Verificación PIN

```typescript
public showVerifyCodeModal = async (): Promise<void> => {
  this._dialogService.showLoader();
  
  try {
    await this.upgradeService.GeneratePinVerification();
  } catch (error) {
    console.error(error);
  }
  
  this._dialogService.closeLoader();
  
  const tries = this.triesService.getTries();
  const message = this.userService.messagePinFormat(
    this.userData?.telefono_abonado,
    this.userData?.email_abonado,
  );
  
  this._dialogService.showPinDialog(
    (pin: string) => {
      return new Promise<void>((resolve, reject) => {
        if (this.selectedPlanToUpgrade && this.selectedPlanToUpgrade.id_servicio_adm) {
          this._dialogService.showLoader();
          
          // Query para realizar upgrade
          this.upgradeService
            .RequestUpgrade<{ data: { resultado: string } }>(
              String(this.selectedPlanToUpgrade?.id_servicio_adm),
              pin,
            )
            .then((verifyPinData: { data: { resultado: string } }) => {
              this._dialogService.closeLoader();
              if (verifyPinData?.data?.resultado === 'ok') {
                this.applyUpgrade();
                resolve();
              } else {
                reject();
              }
            })
            .catch(error => {
              this._dialogService.closeLoader();
              this.handleUpgradeError(error, tries);
              reject();
            });
        }
      });
    },
    4, // Máximo 4 intentos
    true, // Modal cancelable
    message,
  );
};
```

### 6.2 Manejo de Errores de PIN

```typescript
private handleUpgradeError = (error: any, tries: number) => {
  const errorStatus = 
    error instanceof Error &&
    error.message.includes('La solicitud ha fallado por un status: ')
      ? Number(error.message.slice(-3))
      : 0;

  if (error instanceof Error && errorStatus) {
    let invalidPinMessage = '';
    if (tries > 0) {
      this.triesService.setTries(tries - 1);
      this.showVerifyCodeModal();
      invalidPinMessage = 'Pin de verificación invalido. Intente nuevamente más tarde.';
    } else {
      invalidPinMessage = 'Pin de verificación invalido. Intentos superados debe esperar para realizar otra solicitud.';
      this.triesService.setTries(2);
    }
    
    this._dialogService.showToast({
      message: errorStatus === 400 ? invalidPinMessage : 
        errorStatus === 403 ? 'El pin de verificación ha expirado. Intente nuevamente más tarde.' :
        'Error validando Pin. Intente nuevamente más tarde.',
      icon: 'information',
      cssClass: 'toast-danger-color',
    });
  }
};
```

---

## 7. Gestión de Planes y Lógica de Negocio

### 7.1 Clasificación de Planes

```typescript
private getPlanName = (totalMB: number): IPlanNames | undefined => {
  return totalMB <= 200
    ? 'Plan Básico'
    : totalMB <= 400
      ? 'Plan Intermedio'
      : totalMB <= 900
        ? 'Plan Avanzado'
        : undefined;
};
```

### 7.2 Extracción de Megabytes

```typescript
public getTotalMB(serviceName: string): number {
  let totalMB = 0;
  const indexToSearch = serviceName.indexOf('_');
  
  totalMB = parseInt(serviceName.substring(indexToSearch + 1) || '0');
  if (Number.isNaN(totalMB)) {
    const match = serviceName.match(/\d+/);
    if (match) totalMB = parseInt(match[0], 10);
  }
  
  return totalMB;
}
```

### 7.3 Lógica de Disponibilidad

```typescript
private loadInitPlanData = async () => {
  try {
    this.isLoading = true;
    
    const upgradeTable = await this.dbService.getUpgradeTable();
    const upgradeTableDatas = await upgradeTable.findAll();
    const currentServiceDatas = await this.userService.getInternetService(true);
    
    if (currentServiceDatas.length) this.currentUserPlan = currentServiceDatas[0];
    
    // Filtrar servicios activos y no expirados
    const activeUpgradeServices: IServicio[] = upgradeTableDatas.filter(async serviceItem => {
      if (serviceItem.expire > Date.now()) {
        return serviceItem.contrato === this.contrato?.nro_abonado;
      } else {
        // Limpiar servicios expirados
        await upgradeTable.delete({ where: { id_upgrade: serviceItem.id_upgrade } });
        return false;
      }
    });
    
    if (upgradeTableDatas?.length && activeUpgradeServices.length) {
      this.availableServices = activeUpgradeServices;
      this.isLoading = false;
    } else {
      // Cargar desde API si no hay cache
      await this.loadFromAPI();
    }
  } catch (error) {
    this.setErrorMsg('Error al cargar los planes. intente de nuevo más tarde');
  }
};
```

---

## 8. Animaciones y Experiencia de Usuario

### 8.1 Celebración de Upgrade

```typescript
public applyUpgrade = async () => {
  if (this.selectedPlanToUpgrade && this.currentUserPlan) {
    this.isPlanChanged = true;
    
    // Actualizar servicios disponibles
    this.availableServices = this.availableServices.filter(
      serv =>
        this.currentUserPlan &&
        serv.nombre_servicio !== this.currentUserPlan.nombre_servicio &&
        this.getTotalMB(serv.nombre_servicio) > this.getTotalMB(this.currentUserPlan.nombre_servicio),
    );
    
    this.currentUserPlan = this.selectedPlanToUpgrade;
    confetti(); // Animación de celebración
    
    this.updateServices();
  }
};
```

### 8.2 Estados de Carga

```typescript
// Skeleton loading para planes
@if (isLoading) {
  <div class="plan-container">
    @for (item of [1,2,3]; track $index) {
      <ion-skeleton-text class="card-btn-2-skeleton" [animated]="true"></ion-skeleton-text>
    }
  </div>
}
```

---

## 9. Estilos y Diseño Visual

### 9.1 Arquitectura de Estilos

#### **Clases Principales**
```scss
.plan-upgrade-services-container {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 1rem;
}

.plan-card {
  background-color: white;
  border-radius: 1rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  box-shadow: rgba(17, 12, 46, 0.15) 0px 48px 100px 0px;
  
  &:not(:disabled) {
    &:active, &:hover {
      background-color: #f5f5f5;
    }
  }
}

.plan-card.selected {
  border: 2px solid #007bff;
  background-color: #e3f2fd;
}
```

#### **Animaciones Personalizadas**
```scss
@keyframes shakes {
  10% { transform: translate(#{random(5)}px, #{random(5)}px); }
  20% { transform: translate(#{random(5)}px, #{random(5)}px); }
  // ... hasta 100%
}
```

### 9.2 Diseño Responsivo

- **Layout Flexbox:** Para alineación de tarjetas de planes
- **Grid System:** Adaptación a diferentes tamaños de pantalla
- **Mobile First:** Optimizado para dispositivos móviles
- **Touch Interactions:** Estados hover y active para táctil

---

## 10. Integración con APIs Externas

### 10.1 API de Upgrade de Planes

- **Propósito:** Obtener planes disponibles y ejecutar upgrades
- **Métodos:** 
  - `GET /api/servicios/upgrade` - Listado de planes
  - `POST /api/upgrade/request` - Solicitar upgrade
  - `POST /api/upgrade/pin/generate` - Generar PIN
  - `POST /api/upgrade/verify` - Verificar PIN

### 10.2 API de Servicios

- **Propósito:** Obtener servicios actuales del usuario
- **Endpoint:** `GET /api/servicios/usuario`
- **Uso:** Comparación y validación de upgrade disponibles

---

## 11. Consideraciones de Performance

### 11.1 Optimizaciones Implementadas

1. **Cache Local:** Almacenamiento temporal en IndexedDB
2. **Lazy Loading:** Carga bajo demanda de planes
3. **Subscription Management:** Cleanup apropiado de observables
4. **Error Boundaries:** Manejo robusto de errores

### 11.2 Estrategias de Carga

```typescript
// Priorizar cache vs API
if (upgradeTableDatas?.length && activeUpgradeServices.length) {
  this.availableServices = activeUpgradeServices;
  this.isLoading = false;
} else {
  // Cargar desde API como fallback
  let availablePlanToUpgrade: IServiceResponse[] = 
    await this.upgradeService.GetServiciosToUpgrade();
}
```

---

## 12. Testing y Calidad

### 12.1 Casos de Uso Críticos

1. **Flujo completo de upgrade exitoso**
2. **Manejo de usuario deudor**
3. **Validación de PIN incorrecto**
4. **Límite de intentos alcanzado**
5. **Expiración de PIN**
6. **Cambios de contrato durante el flujo**
7. **Conectividad a internet perdida**
8. **Carga de planes desde API vs cache**

### 12.2 Pruebas Unitarias Requeridas

- Gestión de estados de usuario
- Lógica de selección de planes
- Manejo de errores de API
- Validación de formularios
- Integración con servicios
- Animaciones y efectos visuales

---

## 13. Mejoras Futuras Sugeridas

### 13.1 Features Potenciales

1. **Real-time Updates:** WebSocket para actualizaciones instantáneas
2. **Advanced Analytics:** Métricas de conversión de upgrade
3. **AI Recommendations:** Sistema inteligente de sugerencias de planes
4. **Offline Support:** Modo offline para selección básica
5. **Progressive Web App:** Mejoras para PWA

### 13.2 Optimizaciones Técnicas

1. **State Management:** Implementación con NgRx o Signals
2. **Virtual Scrolling:** Para listas largas de planes
3. **Image Optimization:** Lazy loading de banners
4. **Bundle Splitting:** Mejora de tiempo de carga

---

## 14. Notas para Mantenimiento

### 14.1 Puntos Críticos

1. **PIN Security:** Mantener seguridad en generación y validación
2. **Cache Consistency:** Coordinación con backend para actualizaciones
3. **Error Handling:** Logging estructurado para debugging
4. **Performance Monitoring:** Métricas de carga y conversión

### 14.2 Buenas Prácticas

- Mantener estados desacoplados y predecibles
- Implementar proper error handling y logging
- Validar todos los datos del usuario
- Mantener consistencia en el diseño y UX
- Documentar cambios en la API y estructura de datos

---

## 15. Conclusión

La Plan Update Page representa un componente crítico y complejo en la estrategia de retención y upselling de Oficina Móvil. Su implementación combina validación de seguridad, gestión de estados reactivos, animaciones interactivas y una robusta integración con APIs especializadas.

La arquitectura modular basada en servicios especializados permite una mantenibilidad escalable mientras proporciona una experiencia de usuario fluida y segura para el proceso de upgrade de planes. El sistema de validación mediante PIN, el cache inteligente y el manejo robusto de errores la convierten en un componente fundamental para el crecimiento del negocio y satisfacción del cliente.

---

*Documentación actualizada: 2026-04-13*
*Autor: Manuel Morales*
*Equipo: Desarrollo Fibex Telecom*
