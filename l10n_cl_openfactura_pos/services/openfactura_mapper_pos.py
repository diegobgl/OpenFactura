from odoo import _
from odoo.exceptions import ValidationError

from .openfactura_mapper import map_lines_common, map_partner_common, validate_partner_tax_fields


class OpenfacturaPosMapper:
    @staticmethod
    def validate(order, document_type):
        if not order.lines:
            raise ValidationError(_('La orden POS no tiene líneas para emitir.'))
        if document_type == 'invoice':
            validate_partner_tax_fields(order.partner_id)

    @staticmethod
    def payload(order, document_type, document_code):
        return {
            'tipo': document_code,
            'referencia': order.pos_reference,
            'emisor': {
                'rut': order.company_id.vat,
                'sucursal': order.config_id.openfactura_branch_code,
                'giro': order.company_id.openfactura_business_activity or order.company_id.name,
            },
            'receptor': map_partner_common(order.partner_id),
            'detalles': map_lines_common(order.lines),
            'totales': {
                'afecto': order.amount_total - order.amount_tax,
                'iva': order.amount_tax,
                'total': order.amount_total,
            },
            'forma_pago': order.openfactura_payment_method or 'contado',
            'metadata': {'source_channel': 'pos'},
        }
