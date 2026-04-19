from odoo import _
from odoo.exceptions import ValidationError

from .openfactura_mapper import map_lines_common, map_partner_common, validate_partner_tax_fields


class OpenfacturaAccountMoveMapper:
    TYPE_MAP = {
        'out_invoice': {'invoice': 33, 'receipt': 39},
        'out_refund': {'credit_note': 61},
    }

    @classmethod
    def resolve_document_code(cls, move, requested_type):
        mapping = cls.TYPE_MAP.get(move.move_type, {})
        if requested_type not in mapping:
            raise ValidationError(_('Tipo documental no soportado para el tipo de asiento: %s') % move.move_type)
        return mapping[requested_type]

    @staticmethod
    def validate(move, document_type):
        if move.state != 'posted':
            raise ValidationError(_('Debe publicar la factura antes de emitir en Openfactura.'))
        if move.move_type not in ('out_invoice', 'out_refund'):
            raise ValidationError(_('Solo se admiten facturas/notas de cliente.'))
        if not move.invoice_line_ids:
            raise ValidationError(_('La factura no tiene líneas para emitir.'))
        if document_type in ('invoice', 'credit_note', 'debit_note'):
            validate_partner_tax_fields(move.partner_id, require_email=False)

    @staticmethod
    def payload(move, document_type, document_code):
        details_lines = move.invoice_line_ids.filtered(lambda l: not l.display_type)
        return {
            'tipo': document_code,
            'referencia': move.name,
            'emisor': {
                'rut': move.company_id.vat,
                'sucursal': move.company_id.openfactura_default_branch_code,
                'giro': move.company_id.openfactura_business_activity or move.company_id.name,
            },
            'receptor': map_partner_common(move.partner_id),
            'detalles': map_lines_common(details_lines),
            'totales': {
                'afecto': move.amount_untaxed,
                'iva': move.amount_tax,
                'total': move.amount_total,
            },
            'metadata': {'source_channel': 'account_move', 'move_type': move.move_type, 'document_type': document_type},
        }
