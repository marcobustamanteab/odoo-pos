=======================
SAP - Integration
=======================

Install all modules required for integration beetween Odoo and SAP.

**Tabla de contenidos**

.. contents::
   :local:

Uso
===

Configuración
=============

INVENTARIO

Parametrizar los siguientes modelo/campos que permiten la sincronización de datos entre Odoo y SAP
* backend.acp (en módulo Conectores): Crear o modificar un registro con las credenciales de connexion al bus
* backed.acp.user: Es el nombre de usuario que se envía a SAP (ej. Odoo)
* En Ajustes > Usuarios y Compañias > Compañías:
 * company_id.ccu_business_unit (Unidad de Negocio CCU): Código de Empresa CCU para SAP ej. A050
 * company_id.backend_esb_id  (Proveedor de ESB): Seleccionar Servidor WSO2 que contiene APIs
* En Inventario > configuración > Ubicaciones
 * location.ccu_code (Código CCU)> indicar código SAP del Almacen (ubicación Odoo). Ej. PT08
 * location.location_id.ccu_code (Código CCU) > en padre de Almacen indica el código de Centro SAP. Ej. 5033
* En Inventario > configuración > Tipos de Operaciones
 * stock.picking.type.ccu_code_usage (ERP Code USage)> Código SAP del tipo de Operación. Ej. T06 para movimientos de Venta y T05 para ingreso
 * stock.picking.type.ccu_sync (Sync with CCU) > Indicar que tipo de Operación se debe sincronizar con CCU

CONTABILIDAD

* IMPORTANTE: Todas las cuentas que se muevan al hacer una venta o devolución, deben enviarse a SAP
* IMPORTANTE: Todos los usuarios de CAJA deben pertenecer a un Equipo de Ventas. Aquí se especifica el código de SUCURSAL o CENTRO a la que pertenecen

Parametrizar los siguientes modelo/campos que permiten la sincronización de datos entre Odoo y SAP

* En Ajustes > Usuarios y Compañías > Compañias
 * res.company.cost_center_code (Cost Center Code): Indicar Centro de Costo SAP para la empresa
 * res.company.cost_center_code (Profit Center Code): Indicar Centro de Beneficio SAP para la empresa
* En Contabilidad > Configuración > Plan de Cuentas
 * account.account.send_cost_center (Send Cost Center to ESB): Indicar si movimiento en cuenta envía Centro de Costo a SAP
 * account.account.send_profit_center (Send Cost Center to ESB): Indicar si movimiento en cuenta envía Centro de Beneficio a SAP
* En Inventario > Configuración > Diarios Contables
 * account_move.journal_id.ccu_sync (Sincroniza con ESB), indicar que diario contable se envíe a SAP
 * account_move.journal_id.ccu_code (Código de Diario en SAP), indicar con qué código de Diario SAP se hace el movimiento. Ej. "IE"
* En Empleados > Configuración > Equipos de Ventas
 * team.branch_ccu_code: Indica el código de Centro SAP al cual pertenece el equipo de Ventas. Ej. 5033

Creditos
========
  * CCU S.A.

Contribuidores
--------------

* `CCU <https://www.ccu.cl>`_:

  * Daniel Clavería <dclaver@ccu.cl>

Mantenedores
------------

Ese modulo esta mantenido por Área de Desarrollo CCU S.A.

.. image:: https://www.ccu.cl/wp-content/themes/ccu/img/logo-color.png
   :target: https://www.ccu.cl
   :alt: CCU S.A.
