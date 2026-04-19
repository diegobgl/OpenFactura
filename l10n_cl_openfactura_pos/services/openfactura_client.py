import json
import logging
import time
import uuid
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from odoo import _
from odoo.exceptions import UserError

from .openfactura_endpoints import OPENFACTURA_ENDPOINTS

_logger = logging.getLogger(__name__)


class OpenfacturaClient:
    def __init__(self, company, env):
        self.company = company
        self.env = env

    def _base_url(self):
        return (self.company.openfactura_base_url or '').rstrip('/')

    def _headers(self, idempotency_key=None, correlation_id=None):
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.company.openfactura_api_key or '',
            'X-Correlation-ID': correlation_id or str(uuid.uuid4()),
        }
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        return headers

    def _sanitize_headers(self, headers):
        sanitized = dict(headers)
        if sanitized.get('apikey'):
            sanitized['apikey'] = '***'
        return sanitized

    def call(self, endpoint_key, payload=None, params=None, path_params=None, idempotency_key=None, correlation_id=None):
        if endpoint_key not in OPENFACTURA_ENDPOINTS:
            raise UserError(_('Openfactura endpoint not configured: %s') % endpoint_key)
        endpoint = OPENFACTURA_ENDPOINTS[endpoint_key]
        method = endpoint['method']
        path = endpoint['path'].format(**(path_params or {}))
        url = f"{self._base_url()}{path}"
        if params:
            query = '&'.join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url = f"{url}?{query}"

        body = None
        if payload is not None:
            body = json.dumps(payload).encode('utf-8')

        headers = self._headers(idempotency_key=idempotency_key, correlation_id=correlation_id)
        req = urlrequest.Request(url=url, data=body, headers=headers, method=method)
        timeout = self.company.openfactura_timeout_seconds
        started = time.time()
        error_message = False
        status_code = False
        response_text = False

        for attempt in range(1, self.company.openfactura_retry_count + 2):
            try:
                with urlrequest.urlopen(req, timeout=timeout) as response:
                    status_code = response.getcode()
                    response_text = response.read().decode('utf-8')
                    break
            except HTTPError as err:
                status_code = err.code
                response_text = err.read().decode('utf-8') if err.fp else '{}'
                if status_code >= 500 and attempt <= self.company.openfactura_retry_count:
                    continue
                error_message = f"HTTP {status_code}"
                break
            except URLError as err:
                error_message = str(err)
                if attempt <= self.company.openfactura_retry_count:
                    continue
                break

        duration_ms = int((time.time() - started) * 1000)
        self.env['openfactura.log'].sudo().create_log(
            company=self.company,
            operation=endpoint_key,
            request_url=url,
            request_method=method,
            request_headers=headers,
            request_body=payload,
            response_status=status_code,
            response_body=response_text,
            error_message=error_message,
            duration_ms=duration_ms,
            correlation_id=headers.get('X-Correlation-ID'),
        )

        parsed = {}
        if response_text:
            try:
                parsed = json.loads(response_text)
            except json.JSONDecodeError:
                parsed = {'raw': response_text}

        if error_message or (status_code and status_code >= 400):
            raise UserError(_('Openfactura request failed: %s') % (parsed.get('message') or error_message or status_code))

        return {
            'status': status_code,
            'headers': self._sanitize_headers(headers),
            'raw': response_text,
            'data': parsed,
            'correlation_id': headers.get('X-Correlation-ID'),
        }

    def test_connection(self):
        return self.call('healthcheck')
