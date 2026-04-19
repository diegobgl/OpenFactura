from odoo import _
from odoo.exceptions import ValidationError


def validate_partner_tax_fields(partner, require_email=False):
    missing = []
    if not partner:
        raise ValidationError(_('Debe seleccionar un cliente para emitir el documento tributario.'))
    required = ['vat', 'name', 'street', 'city']
    if require_email:
        required.append('email')
    for field_name in required:
        if not partner[field_name]:
            missing.append(field_name)
    if missing:
        raise ValidationError(_('Faltan datos tributarios del cliente: %s') % ', '.join(missing))


def map_partner_common(partner):
    if not partner:
        return {
            'rut': '66666666-6',
            'razon_social': 'Consumidor Final',
            'direccion': 'N/A',
            'comuna': 'N/A',
        }
    return {
        'rut': partner.vat,
        'razon_social': partner.name,
        'giro': partner.function or partner.name,
        'direccion': partner.street,
        'comuna': partner.city,
        'correo': partner.email,
    }


def map_lines_common(lines):
    details = []
    for line in lines:
        product = getattr(line, 'product_id', False)
        qty = getattr(line, 'qty', False) if hasattr(line, 'qty') else getattr(line, 'quantity', 0)
        price_unit = getattr(line, 'price_unit', 0)
        discount = getattr(line, 'discount', 0)
        tax_ids = getattr(line, 'tax_ids', False)
        details.append({
            'nombre': (product.display_name if product else (line.name or 'Item'))[:80],
            'codigo': product.default_code if product and product.default_code else str(product.id if product else line.id),
            'cantidad': qty,
            'precio': price_unit,
            'descuento': discount or 0,
            'impuestos': [tax.amount for tax in tax_ids] if tax_ids else [],
        })
    return details
