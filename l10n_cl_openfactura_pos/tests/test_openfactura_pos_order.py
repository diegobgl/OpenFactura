from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestOpenfacturaPosOrder(TransactionCase):
    def test_emit_document_error_sets_retry(self):
        order = self.env['pos.order'].create({
            'name': 'Test',
            'company_id': self.env.company.id,
            'session_id': self.env['pos.session'].search([], limit=1).id,
            'amount_total': 100,
            'amount_tax': 19,
            'amount_paid': 100,
            'amount_return': 0,
            'config_id': self.env['pos.config'].search([], limit=1).id,
        })
        order.config_id.openfactura_enabled = True
        with patch('odoo.addons.l10n_cl_openfactura_pos.services.openfactura_client.OpenfacturaClient.call', side_effect=Exception('timeout')):
            with self.assertRaises(Exception):
                order.action_openfactura_emit()
            self.assertEqual(order.openfactura_document_id.state, 'retry')
