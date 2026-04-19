from odoo import fields, models


class OpenfacturaResyncWizard(models.TransientModel):
    _name = 'openfactura.resync.wizard'
    _description = 'Openfactura Re-sync'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    sync_catalogs = fields.Boolean(default=True)
    sync_partners = fields.Boolean(default=False)

    def action_resync(self):
        from ..services.openfactura_sync_service import OpenfacturaSyncService
        service = OpenfacturaSyncService(self.env, self.company_id)
        if self.sync_catalogs:
            service.sync_catalogs()
        if self.sync_partners:
            service.sync_partners()
        return {'type': 'ir.actions.act_window_close'}
