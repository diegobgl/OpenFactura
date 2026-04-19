from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..services.openfactura_mapper import validate_partner_tax_fields


class TestOpenfacturaMapper(TransactionCase):
    def test_invoice_partner_validation(self):
        partner = self.env['res.partner'].create({'name': 'X'})
        with self.assertRaises(ValidationError):
            validate_partner_tax_fields(partner)
