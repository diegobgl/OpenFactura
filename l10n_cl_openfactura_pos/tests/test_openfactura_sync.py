from unittest.mock import patch

from odoo.tests.common import TransactionCase

from ..services.openfactura_sync_service import OpenfacturaSyncService


class TestOpenfacturaSync(TransactionCase):
    def test_sync_catalogs_creates_jobs(self):
        service = OpenfacturaSyncService(self.env, self.env.company)
        with patch('odoo.addons.l10n_cl_openfactura_pos.services.openfactura_client.OpenfacturaClient.call', return_value={'data': []}):
            service.sync_catalogs()
        self.assertTrue(self.env['openfactura.sync.job'].search_count([]) > 0)
