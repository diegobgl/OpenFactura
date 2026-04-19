import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from ..services.openfactura_attachment_service import OpenfacturaAttachmentService
from ..services.openfactura_dte_builder import build_idempotency_key, build_payload


class PosOrder(models.Model):
    _inherit = 'pos.order'

    openfactura_document_type = fields.Selection([
        ('receipt', 'Boleta'),
        ('invoice', 'Factura'),
    ], default='receipt')
    openfactura_document_id = fields.Many2one('openfactura.document', copy=False)
    openfactura_state = fields.Selection(related='openfactura_document_id.state', store=True)
    openfactura_error_message = fields.Text(copy=False)
    openfactura_payment_method = fields.Char(copy=False)

    @api.model
    def _load_pos_data_fields(self, config_id):
        result = super()._load_pos_data_fields(config_id)
        result += ['openfactura_document_type', 'openfactura_document_id', 'openfactura_state']
        return result

    def _ensure_document_type(self):
        self.ensure_one()
        return self.openfactura_document_type or self.config_id.openfactura_default_document_type

    def action_openfactura_emit(self):
        for order in self:
            if not order.config_id.openfactura_enabled:
                continue
            doc_type = order._ensure_document_type()
            idempotency_key = build_idempotency_key(order, doc_type)
            existing = self.env['openfactura.document'].search([
                ('company_id', '=', order.company_id.id),
                ('idempotency_key', '=', idempotency_key),
                ('state', 'in', ['sent', 'accepted'])
            ], limit=1)
            if existing:
                order.openfactura_document_id = existing
                continue

            payload = build_payload(order, doc_type)
            document = order.openfactura_document_id or self.env['openfactura.document'].create({
                'name': order.name,
                'company_id': order.company_id.id,
                'pos_config_id': order.config_id.id,
                'pos_order_id': order.id,
                'partner_id': order.partner_id.id,
                'document_type': doc_type,
                'idempotency_key': idempotency_key,
                'currency_id': order.currency_id.id,
                'amount_total': order.amount_total,
                'amount_tax': order.amount_tax,
                'amount_untaxed': order.amount_total - order.amount_tax,
                'state': 'sending',
                'request_payload': json.dumps(payload),
                'sent_at': fields.Datetime.now(),
            })
            order.openfactura_document_id = document
            client = document._get_client(order.company_id)
            try:
                response = client.call('emit_document', payload=payload, idempotency_key=idempotency_key)
                data = response.get('data', {})
                document.write({
                    'state': 'sent',
                    'external_id': data.get('id') or data.get('external_id'),
                    'folio': str(data.get('folio') or ''),
                    'number': str(data.get('numero') or ''),
                    'response_payload': response.get('raw'),
                    'response_code': response.get('status'),
                    'response_at': fields.Datetime.now(),
                    'correlation_id': response.get('correlation_id'),
                })
                OpenfacturaAttachmentService(self.env).attach_document_payloads(
                    document,
                    pdf=data.get('pdf'),
                    xml=data.get('xml'),
                    json_raw=response.get('raw'),
                )
                order.message_post(body=_('Openfactura document emitted successfully. Folio: %s') % (document.folio or '-'))
            except Exception as err:
                document.write({
                    'state': 'retry',
                    'error_message': str(err),
                    'response_at': fields.Datetime.now(),
                })
                order.openfactura_error_message = str(err)
                order.message_post(body=_('Openfactura emission failed: %s') % err)
                raise UserError(_('No se pudo emitir DTE. Intente nuevamente o contacte soporte.'))

    def action_openfactura_reprint(self):
        self.ensure_one()
        if not self.openfactura_document_id or not self.openfactura_document_id.pdf_attachment_id:
            raise UserError(_('No PDF tributario disponible para reimpresión.'))
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{self.openfactura_document_id.pdf_attachment_id.id}?download=true",
            'target': 'self',
        }

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super().create_from_ui(orders, draft=draft)
        created_orders = self.browse([o.get('id') for o in order_ids if o.get('id')])
        for order in created_orders:
            if order.config_id.openfactura_enabled:
                order.action_openfactura_emit()
        return order_ids
