from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
        from ..services.openfactura_emission_service import OpenfacturaEmissionService
        for order in self:
            if not order.config_id.openfactura_enabled:
                continue
            document_type = order._ensure_document_type()
            service = OpenfacturaEmissionService(self.env, order.company_id)
            try:
                document = service.emit_from_pos(order, document_type)
                order.openfactura_document_id = document
            except Exception as err:
                order.openfactura_error_message = str(err)
                raise UserError(_('No se pudo emitir DTE POS: %s') % err)

    def action_openfactura_reprint(self):
        self.ensure_one()
        doc = self.openfactura_document_id
        if not doc or not doc.pdf_attachment_id:
            raise UserError(_('No PDF tributario disponible para reimpresión.'))
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{doc.pdf_attachment_id.id}?download=true",
            'target': 'self',
        }

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super().create_from_ui(orders, draft=draft)
        created_orders = self.browse([o.get('id') for o in order_ids if o.get('id')])
        for order in created_orders.filtered(lambda o: o.config_id.openfactura_enabled):
            order.action_openfactura_emit()
        return order_ids
