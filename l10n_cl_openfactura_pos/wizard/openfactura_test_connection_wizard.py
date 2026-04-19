from odoo import _, fields, models
from odoo.exceptions import UserError


class OpenfacturaTestConnectionWizard(models.TransientModel):
    _name = 'openfactura.test.connection.wizard'
    _description = 'Openfactura Test Connection'

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)

    def action_test(self):
        client = self.env['openfactura.document']._get_client(self.company_id)
        try:
            client.test_connection()
            self.company_id.write({
                'openfactura_last_connection_state': 'ok',
                'openfactura_last_connection_message': 'OK',
            })
        except Exception as err:
            self.company_id.write({
                'openfactura_last_connection_state': 'error',
                'openfactura_last_connection_message': str(err),
            })
            raise UserError(_('Conexión fallida: %s') % err)
        return {'type': 'ir.actions.act_window_close'}
