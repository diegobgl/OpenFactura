from odoo import _
from odoo.exceptions import ValidationError


def normalize_vat(vat):
    return (vat or '').replace('.', '').replace('-', '').upper().strip()


def validate_partner_for_invoice(partner):
    missing = []
    if not partner:
        raise ValidationError(_('Partner is mandatory for invoice DTE emission.'))
    if not partner.vat:
        missing.append('vat')
    if not partner.name:
        missing.append('name')
    if not partner.street:
        missing.append('street')
    if not partner.city:
        missing.append('city')
    if missing:
        raise ValidationError(_('Missing fiscal fields: %s') % ', '.join(missing))


def map_partner_to_openfactura(partner):
    if not partner:
        return {'rut': '66666666-6', 'razon_social': 'Consumidor Final'}
    return {
        'rut': partner.vat,
        'razon_social': partner.name,
        'giro': partner.function or partner.name,
        'direccion': partner.street,
        'comuna': partner.city,
        'correo': partner.email,
    }


def map_order_lines(order):
    result = []
    for line in order.lines:
        result.append({
            'nombre': line.product_id.display_name[:80],
            'cantidad': line.qty,
            'precio': line.price_unit,
            'descuento': line.discount or 0,
            'impuestos': [tax.amount for tax in line.tax_ids],
            'codigo': line.product_id.default_code or str(line.product_id.id),
        })
    return result
