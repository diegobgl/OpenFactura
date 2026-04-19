import hashlib

from .openfactura_mapper import map_order_lines, map_partner_to_openfactura, validate_partner_for_invoice


def build_idempotency_key(order, document_type):
    base = f"{order.company_id.id}:{order.config_id.id}:{order.pos_reference}:{document_type}"
    return hashlib.sha256(base.encode('utf-8')).hexdigest()


def build_payload(order, document_type):
    if document_type == 'invoice':
        validate_partner_for_invoice(order.partner_id)

    return {
        'tipo': 33 if document_type == 'invoice' else 39,
        'referencia': order.pos_reference,
        'emisor': {
            'rut': order.company_id.vat,
            'sucursal': order.config_id.openfactura_branch_code,
            'giro': order.company_id.openfactura_business_activity or order.company_id.name,
        },
        'receptor': map_partner_to_openfactura(order.partner_id),
        'detalles': map_order_lines(order),
        'totales': {
            'afecto': order.amount_total - order.amount_tax,
            'iva': order.amount_tax,
            'total': order.amount_total,
        },
        'forma_pago': order.openfactura_payment_method or 'contado',
    }
