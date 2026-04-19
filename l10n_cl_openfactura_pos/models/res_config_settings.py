from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openfactura_api_key = fields.Char(related='company_id.openfactura_api_key', readonly=False)
    openfactura_base_url = fields.Char(related='company_id.openfactura_base_url', readonly=False)
    openfactura_environment = fields.Selection(related='company_id.openfactura_environment', readonly=False)
    openfactura_business_activity = fields.Char(related='company_id.openfactura_business_activity', readonly=False)
    openfactura_default_branch_code = fields.Char(related='company_id.openfactura_default_branch_code', readonly=False)
    openfactura_timeout_seconds = fields.Integer(related='company_id.openfactura_timeout_seconds', readonly=False)
    openfactura_retry_count = fields.Integer(related='company_id.openfactura_retry_count', readonly=False)
