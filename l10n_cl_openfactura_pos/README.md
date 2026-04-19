# l10n_cl_openfactura_pos

Integración Odoo 19 POS ↔ Openfactura (Haulmer) para emisión de DTE en Chile, con trazabilidad, idempotencia y soporte operativo.

## Instalación
1. Copiar el módulo en addons path.
2. Actualizar apps list e instalar `l10n_cl_openfactura_pos`.
3. Verificar dependencias: `point_of_sale`, `account`, `mail`, `contacts`, `product`, `stock`.

## Configuración
### Por compañía
- API Key Openfactura.
- Base URL API.
- Ambiente (sandbox/producción).
- Giro por defecto.
- Timeout y reintentos.

### Por POS
- Habilitar emisión Openfactura.
- Tipo de documento por defecto (boleta/factura).
- Sucursal.
- Restricciones de factura sin cliente.

## Flujo de emisión POS
1. Cajero elige Boleta/Factura.
2. POS envía orden a backend Odoo.
3. `pos.order.create_from_ui()` gatilla `action_openfactura_emit()`.
4. Backend construye payload, calcula idempotency key determinística y llama API mediante `OpenfacturaClient`.
5. Se persiste `openfactura.document`, `openfactura.log`, chatter, adjuntos PDF/XML/JSON si existen.

## Troubleshooting
- **Error de conexión**: ejecutar wizard de prueba de conexión y revisar `Openfactura Logs`.
- **Orden en retry**: usar acción manual Retry en documento.
- **Factura bloqueada**: completar datos tributarios del partner (RUT, razón social, dirección, comuna).

## Decisiones de arquitectura
- Cliente HTTP centralizado con manejo uniforme de errores.
- Endpoint registry desacoplado de modelos de negocio.
- Servicios separados: builder, mapper, sync, status, attachment.
- Estado de documento explícito y cron para refresh de estado.
- Multi-company por diseño (config y datos con `company_id`).

## Extensión futura
- Añadir catálogo maestro persistente por recurso (document types, branches, payment methods, taxes, activities).
- Sincronización bidireccional de productos y clientes.
- Webhooks/callbacks solo si Openfactura los documenta oficialmente.
- Dashboard KPI de aceptación/rechazo y latencia de API.

## Nota sobre documentación API
Se intentó consultar `https://docsapi-openfactura.haulmer.com/`, pero en este entorno devolvió bloqueo de red (403 CONNECT tunnel). El módulo mantiene `openfactura_endpoints.py` como capa de adaptación para ajustar rutas/payloads de forma segura según la documentación oficial vigente al desplegar en entorno con acceso.
