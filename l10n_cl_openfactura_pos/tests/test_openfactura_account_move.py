from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestOpenfacturaAccountMove(TransactionCase):
    def _create_invoice(self, company=None):
        company = company or self.env.company
        partner = self.env['res.partner'].create({
            'name': 'Cliente Prueba',
            'vat': '76086428-5',
            'street': 'Av. Siempre Viva 123',
            'city': 'Santiago',
            'company_id': False,
        })
        product = self.env['product.product'].create({'name': 'Servicio', 'list_price': 100})
        account = self.env['account.account'].search([('company_id', '=', company.id), ('account_type', '=', 'income')], limit=1)
        move = self.env['account.move'].with_company(company).create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_line_ids': [(0, 0, {'product_id': product.id, 'quantity': 1, 'price_unit': 100, 'account_id': account.id})],
        })
        move.action_post()
        return move

    def test_emit_success_from_account_move(self):
        move = self._create_invoice()
        with patch('odoo.addons.l10n_cl_openfactura_pos.services.openfactura_client.OpenfacturaClient.call', return_value={'data': {'id': 'ext-1', 'folio': 123}, 'raw': '{}', 'status': 200, 'correlation_id': 'c1'}):
            move.action_openfactura_emit()
        self.assertTrue(move.openfactura_document_id)
        self.assertEqual(move.openfactura_document_id.source_channel, 'account_move')

    def test_partner_validation_error(self):
        move = self._create_invoice()
        move.partner_id.vat = False
        with self.assertRaises(ValidationError):
            move.action_openfactura_emit()

    def test_idempotency_duplicate_avoided(self):
        move = self._create_invoice()
        with patch('odoo.addons.l10n_cl_openfactura_pos.services.openfactura_client.OpenfacturaClient.call', return_value={'data': {'id': 'ext-1', 'folio': 123}, 'raw': '{}', 'status': 200, 'correlation_id': 'c1'}) as mocked:
            move.action_openfactura_emit()
            move.action_openfactura_emit()
        self.assertEqual(mocked.call_count, 1)

    def test_retry_flow(self):
        move = self._create_invoice()
        with patch('odoo.addons.l10n_cl_openfactura_pos.services.openfactura_client.OpenfacturaClient.call', side_effect=Exception('timeout')):
            with self.assertRaises(Exception):
                move.action_openfactura_emit()
        self.assertEqual(move.openfactura_document_id.state, 'retry')

    def test_multi_company(self):
        company2 = self.env['res.company'].create({'name': 'Comp2'})
        move = self._create_invoice(company=company2)
        with patch('odoo.addons.l10n_cl_openfactura_pos.services.openfactura_client.OpenfacturaClient.call', return_value={'data': {'id': 'ext-2', 'folio': 321}, 'raw': '{}', 'status': 200, 'correlation_id': 'c2'}):
            move.action_openfactura_emit()
        self.assertEqual(move.openfactura_document_id.company_id, company2)
