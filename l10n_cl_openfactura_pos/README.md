# l10n_cl_openfactura_pos

Integración Odoo 19 (Community + Enterprise) para emisión tributaria Openfactura desde **POS** y **Facturación/Contabilidad**.

## Objetivo
- Canal único de integración Openfactura reutilizable.
- Trazabilidad completa de request/response, estado, idempotencia y adjuntos.
- Arquitectura mantenible, multi-company, operable en producción.

## Arquitectura
- **Cliente HTTP único**: `services/openfactura_client.py`
- **Modelo documental unificado**: `openfactura.document` con `source_channel`, `source_model`, `source_res_id`.
- **Servicio de emisión común**: `services/openfactura_emission_service.py`.
- **Mappers por canal**:
  - `openfactura_mapper_pos.py`
  - `openfactura_mapper_account_move.py`
- **Builder de idempotencia/document type común**: `openfactura_dte_builder.py`.

## Flujos de emisión
### 1) POS
`pos.order.create_from_ui()` → `pos.order.action_openfactura_emit()` → `OpenfacturaEmissionService.emit_from_pos()`.

### 2) Facturación / Contabilidad
Botones en `account.move`:
- Emitir Openfactura
- Consultar Estado
- Reintentar
- Descargar PDF
- Ver Documento Openfactura

Flujo: `account.move.action_openfactura_emit()` → `OpenfacturaEmissionService.emit_from_account_move()`.

## Validaciones
- Partner tributario (RUT, razón social, dirección, ciudad).
- Líneas con contenido.
- `account.move` cliente y estado `posted` para emisión conservadora.
- Tipo documental según `move_type`.

## Idempotencia
Key determinística por:
`company + source_channel + source_model + source_res_id + document_type`.

## Trazabilidad
- `openfactura.document`: payloads, response, folio, external_id, estado, adjuntos.
- `openfactura.log`: logging técnico saneado (apikey oculto).
- Chatter en `pos.order` y `account.move`.

## Nota de documentación Openfactura
En este entorno no fue posible consultar `https://docsapi-openfactura.haulmer.com/` por bloqueo de red (`403 CONNECT tunnel failed`).
Se dejó `openfactura_endpoints.py` como capa de adaptación para alinear rápidamente rutas/payloads con la documentación oficial vigente en entorno con acceso.
