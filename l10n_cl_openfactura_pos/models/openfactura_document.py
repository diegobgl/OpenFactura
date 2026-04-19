from odoo import fields, models


class OpenfacturaDocument(models.Model):
    _name = 'openfactura.document'
    _description = 'Openfactura Emitted Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(required=True, default='New')
    company_id = fields.Many2one('res.company', required=True, index=True)
    pos_config_id = fields.Many2one('pos.config', index=True)
    pos_order_id = fields.Many2one('pos.order', index=True)
    account_move_id = fields.Many2one('account.move', index=True)
    partner_id = fields.Many2one('res.partner')
    document_type = fields.Selection([('receipt', 'Boleta'), ('invoice', 'Factura')], required=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('pending_send', 'Pending Send'), ('sending', 'Sending'), ('sent', 'Sent'),
        ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('pending_status', 'Pending Status'),
        ('retry', 'Retry'), ('error', 'Error'),
    ], default='draft', tracking=True)
    external_id = fields.Char(index=True)
    folio = fields.Char(index=True)
    number = fields.Char(index=True)
    idempotency_key = fields.Char(required=True, index=True)
    request_payload = fields.Text()
    response_payload = fields.Text()
    response_code = fields.Integer()
    error_message = fields.Text()
    sent_at = fields.Datetime()
    response_at = fields.Datetime()
    pdf_attachment_id = fields.Many2one('ir.attachment')
    xml_attachment_id = fields.Many2one('ir.attachment')
    json_attachment_id = fields.Many2one('ir.attachment')
    currency_id = fields.Many2one('res.currency', required=True)
    amount_total = fields.Monetary(currency_field='currency_id')
    amount_tax = fields.Monetary(currency_field='currency_id')
    amount_untaxed = fields.Monetary(currency_field='currency_id')
    correlation_id = fields.Char(index=True)

    _sql_constraints = [
        ('openfactura_document_idempotency_unique', 'unique(company_id, idempotency_key)',
         'Idempotency key must be unique per company.'),
    ]

    def _get_client(self, company):
        from ..services.openfactura_client import OpenfacturaClient
        return OpenfacturaClient(company=company, env=self.env)

    def action_retry(self):
        for rec in self:
            if rec.pos_order_id:
                rec.pos_order_id.action_openfactura_emit()

    def action_refresh_status(self):
        for rec in self.filtered(lambda d: d.external_id):
            response = self._get_client(rec.company_id).call(
                'get_document_status', path_params={'external_id': rec.external_id}
            )
            status = (response['data'].get('status') if isinstance(response['data'], dict) else '') or 'pending'
            from ..services.openfactura_status_service import OpenfacturaStatusService
            rec.state = OpenfacturaStatusService.normalize(status)
