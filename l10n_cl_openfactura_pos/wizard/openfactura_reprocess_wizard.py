from odoo import fields, models


class OpenfacturaReprocessWizard(models.TransientModel):
    _name = 'openfactura.reprocess.wizard'
    _description = 'Openfactura Reprocess'

    document_id = fields.Many2one('openfactura.document', required=True)

    def action_reprocess(self):
        self.document_id.action_retry()
        return {'type': 'ir.actions.act_window_close'}
