from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    openfactura_enabled = fields.Boolean(default=False)
    openfactura_default_document_type = fields.Selection([
        ('receipt', 'Boleta'),
        ('invoice', 'Factura'),
    ], default='receipt')
    openfactura_allow_receipt = fields.Boolean(default=True)
    openfactura_allow_invoice = fields.Boolean(default=True)
    openfactura_branch_code = fields.Char()
    openfactura_force_partner_for_invoice = fields.Boolean(default=True)
