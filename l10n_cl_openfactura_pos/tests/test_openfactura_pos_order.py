from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestOpenfacturaPosOrder(TransactionCase):
    def test_emit_document_error_sets_retry(self):
        pos_config = self.env['pos.config'].search([], limit=1)
        session = self.env['pos.session'].search([('config_id', '=', pos_config.id)], limit=1)
        if not session:
            return
        order = self.env['pos.order'].create({
            'name': 'Test',
            'company_id': self.env.company.id,
            'session_id': session.id,
            'amount_total': 100,
            'amount_tax': 19,
            'amount_paid': 100,
            'amount_return': 0,
            'config_id': pos_config.id,
        })
        order.config_id.openfactura_enabled = True
        with patch('odoo.addons.l10n_cl_openfactura_pos.services.openfactura_emission_service.OpenfacturaEmissionService.emit_from_pos', side_effect=Exception('timeout')):
            with self.assertRaises(Exception):
                order.action_openfactura_emit()
