"""Central endpoint registry for Openfactura API resources.

The API docs host may evolve; this layer isolates endpoint path changes from business logic.
"""

OPENFACTURA_ENDPOINTS = {
    'emit_document': {'method': 'POST', 'path': '/v2/dte/document'},
    'get_document': {'method': 'GET', 'path': '/v2/dte/document/{external_id}'},
    'get_document_status': {'method': 'GET', 'path': '/v2/dte/document/{external_id}/status'},
    'document_pdf': {'method': 'GET', 'path': '/v2/dte/document/{external_id}/pdf'},
    'document_xml': {'method': 'GET', 'path': '/v2/dte/document/{external_id}/xml'},
    'document_json': {'method': 'GET', 'path': '/v2/dte/document/{external_id}/json'},
    'document_types': {'method': 'GET', 'path': '/v2/dte/document-types'},
    'branches': {'method': 'GET', 'path': '/v2/dte/branches'},
    'economic_activities': {'method': 'GET', 'path': '/v2/dte/activities'},
    'payment_methods': {'method': 'GET', 'path': '/v2/dte/payment-methods'},
    'taxes': {'method': 'GET', 'path': '/v2/dte/taxes'},
    'customers': {'method': 'GET', 'path': '/v2/dte/customers'},
    'products': {'method': 'GET', 'path': '/v2/dte/products'},
    'healthcheck': {'method': 'GET', 'path': '/v2/dte/organization'},
}

CATALOG_ENDPOINTS = [
    'document_types',
    'branches',
    'economic_activities',
    'payment_methods',
    'taxes',
]
