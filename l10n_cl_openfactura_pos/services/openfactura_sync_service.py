from odoo import fields

from .openfactura_endpoints import CATALOG_ENDPOINTS


class OpenfacturaSyncService:
    def __init__(self, env, company):
        self.env = env
        self.company = company
        self.client = env['openfactura.document']._get_client(company)

    def sync_catalogs(self):
        for endpoint in CATALOG_ENDPOINTS:
            self.env['openfactura.sync.job'].sudo().create({
                'company_id': self.company.id,
                'job_type': endpoint,
                'state': 'running',
            })
            self.client.call(endpoint)

    def sync_partners(self):
        data = self.client.call('customers').get('data', [])
        Partner = self.env['res.partner'].sudo().with_company(self.company)
        for entry in data if isinstance(data, list) else data.get('data', []):
            vat = entry.get('rut')
            if not vat:
                continue
            partner = Partner.search([('vat', '=', vat), ('company_id', 'in', [False, self.company.id])], limit=1)
            values = {
                'name': entry.get('razon_social') or vat,
                'vat': vat,
                'email': entry.get('correo'),
                'openfactura_external_id': entry.get('id'),
                'openfactura_last_sync': fields.Datetime.now(),
            }
            if partner:
                partner.write(values)
            else:
                Partner.create(values)
