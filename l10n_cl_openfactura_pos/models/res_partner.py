from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    openfactura_external_id = fields.Char(index=True)
    openfactura_last_sync = fields.Datetime()
