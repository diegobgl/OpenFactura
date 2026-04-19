from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestOpenfacturaClient(TransactionCase):
    def test_healthcheck_error(self):
        company = self.env.company
        company.openfactura_api_key = 'demo'
        doc = self.env['openfactura.document']
        client = doc._get_client(company)
        with patch('urllib.request.urlopen', side_effect=Exception('boom')):
            with self.assertRaises(Exception):
                client.test_connection()
