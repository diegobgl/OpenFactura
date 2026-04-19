from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

from ..services.openfactura_mapper import validate_partner_for_invoice


class TestOpenfacturaMapper(TransactionCase):
    def test_invoice_partner_validation(self):
        partner = self.env['res.partner'].create({'name': 'X'})
        with self.assertRaises(ValidationError):
            validate_partner_for_invoice(partner)
