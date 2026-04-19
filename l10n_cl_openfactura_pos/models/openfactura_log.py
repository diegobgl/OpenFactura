import json

from odoo import fields, models


class OpenfacturaLog(models.Model):
    _name = 'openfactura.log'
    _description = 'Openfactura Technical Log'
    _order = 'id desc'

    company_id = fields.Many2one('res.company', required=True)
    related_model = fields.Char()
    related_res_id = fields.Integer()
    operation = fields.Char(required=True)
    level = fields.Selection([('info', 'Info'), ('warning', 'Warning'), ('error', 'Error')], default='info')
    request_url = fields.Char()
    request_method = fields.Char()
    request_headers_sanitized = fields.Text()
    request_body = fields.Text()
    response_status = fields.Integer()
    response_body = fields.Text()
    error_message = fields.Text()
    duration_ms = fields.Integer()
    correlation_id = fields.Char(index=True)
    created_at = fields.Datetime(default=fields.Datetime.now)

    def create_log(self, company, operation, request_url, request_method, request_headers, request_body,
                   response_status, response_body, error_message, duration_ms, correlation_id):
        return self.create({
            'company_id': company.id,
            'operation': operation,
            'request_url': request_url,
            'request_method': request_method,
            'request_headers_sanitized': json.dumps(request_headers),
            'request_body': json.dumps(request_body) if isinstance(request_body, (dict, list)) else (request_body or ''),
            'response_status': response_status or 0,
            'response_body': response_body or '',
            'error_message': error_message or '',
            'duration_ms': duration_ms,
            'correlation_id': correlation_id,
            'level': 'error' if error_message else 'info',
        })
