from odoo.tests.common import TransactionCase

from ..services.openfactura_dte_builder import build_idempotency_key


class TestOpenfacturaIdempotency(TransactionCase):
    def test_idempotency_is_stable(self):
        order = self.env['pos.order'].new({'company_id': self.env.company.id, 'config_id': self.env['pos.config'].search([], limit=1).id, 'pos_reference': 'ABC'})
        key1 = build_idempotency_key(order, 'receipt')
        key2 = build_idempotency_key(order, 'receipt')
        self.assertEqual(key1, key2)
