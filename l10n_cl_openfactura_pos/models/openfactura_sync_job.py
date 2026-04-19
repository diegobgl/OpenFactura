from odoo import api, fields, models


class OpenfacturaSyncJob(models.Model):
    _name = 'openfactura.sync.job'
    _description = 'Openfactura Synchronization Job'
    _order = 'id desc'

    company_id = fields.Many2one('res.company', required=True)
    job_type = fields.Char(required=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('running', 'Running'), ('done', 'Done'), ('error', 'Error')
    ], default='draft')
    started_at = fields.Datetime(default=fields.Datetime.now)
    ended_at = fields.Datetime()
    message = fields.Text()

    def run_now(self):
        for job in self:
            job.state = 'running'
            job.ended_at = fields.Datetime.now()
            job.state = 'done'

    @api.model
    def cron_refresh_document_status(self):
        docs = self.env['openfactura.document'].search([('state', 'in', ['sent', 'pending_status'])], limit=200)
        docs.action_refresh_status()
