from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    openfactura_document_id = fields.Many2one('openfactura.document', copy=False)
    openfactura_document_type = fields.Selection([
        ('invoice', 'Factura'),
        ('receipt', 'Boleta'),
        ('credit_note', 'Nota de Crédito'),
        ('debit_note', 'Nota de Débito'),
    ], default='invoice')
    openfactura_state = fields.Selection(related='openfactura_document_id.state', store=True)
    openfactura_external_folio = fields.Char(related='openfactura_document_id.folio', store=False)
    openfactura_error_message = fields.Text(related='openfactura_document_id.error_message', store=False)

    def action_openfactura_emit(self):
        from ..services.openfactura_emission_service import OpenfacturaEmissionService
        for move in self:
            service = OpenfacturaEmissionService(self.env, move.company_id)
            doc = service.emit_from_account_move(move, move.openfactura_document_type)
            move.openfactura_document_id = doc
        return True

    def action_openfactura_check_status(self):
        for move in self.filtered('openfactura_document_id'):
            move.openfactura_document_id.action_refresh_status()
        return True

    def action_openfactura_retry(self):
        for move in self:
            doc_type = move.openfactura_document_type
            if move.openfactura_document_id and move.openfactura_document_id.state in ('retry', 'error', 'rejected'):
                move.openfactura_document_id.write({'state': 'pending_send'})
            move.action_openfactura_emit()
            move.openfactura_document_type = doc_type
        return True

    def action_openfactura_open_document(self):
        self.ensure_one()
        if not self.openfactura_document_id:
            raise UserError(_('La factura no tiene documento Openfactura asociado.'))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'openfactura.document',
            'view_mode': 'form',
            'res_id': self.openfactura_document_id.id,
            'target': 'current',
        }

    def action_openfactura_download_pdf(self):
        self.ensure_one()
        doc = self.openfactura_document_id
        if not doc or not doc.pdf_attachment_id:
            raise UserError(_('No existe PDF disponible para este documento.'))
        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/{doc.pdf_attachment_id.id}?download=true",
            'target': 'self',
        }
