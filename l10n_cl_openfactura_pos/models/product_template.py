from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    openfactura_external_id = fields.Char(index=True)
    openfactura_last_sync = fields.Datetime()
