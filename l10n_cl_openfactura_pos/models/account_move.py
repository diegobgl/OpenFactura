from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    openfactura_document_id = fields.Many2one('openfactura.document', copy=False)
