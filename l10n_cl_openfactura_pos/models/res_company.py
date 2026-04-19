from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    openfactura_api_key = fields.Char(groups='l10n_cl_openfactura_pos.group_openfactura_manager')
    openfactura_base_url = fields.Char(default='https://dev-api.haulmer.com')
    openfactura_environment = fields.Selection([
        ('sandbox', 'Sandbox'),
        ('production', 'Production'),
    ], default='sandbox')
    openfactura_business_activity = fields.Char()
    openfactura_timeout_seconds = fields.Integer(default=30)
    openfactura_retry_count = fields.Integer(default=2)
    openfactura_last_connection_state = fields.Selection([
        ('never', 'Never'), ('ok', 'OK'), ('error', 'Error')
    ], default='never', readonly=True)
    openfactura_last_connection_message = fields.Char(readonly=True)
