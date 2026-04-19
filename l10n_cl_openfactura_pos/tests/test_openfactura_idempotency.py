from odoo.tests.common import TransactionCase

from ..services.openfactura_dte_builder import build_idempotency_key


class TestOpenfacturaIdempotency(TransactionCase):
    def test_idempotency_is_stable_and_channel_aware(self):
        key1 = build_idempotency_key(self.env.company.id, 'pos', 'pos.order', 10, 'receipt')
        key2 = build_idempotency_key(self.env.company.id, 'pos', 'pos.order', 10, 'receipt')
        key3 = build_idempotency_key(self.env.company.id, 'account_move', 'account.move', 10, 'receipt')
        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)
