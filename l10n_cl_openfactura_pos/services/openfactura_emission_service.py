import json

from odoo import _, fields
from odoo.exceptions import UserError

from .openfactura_attachment_service import OpenfacturaAttachmentService
from .openfactura_dte_builder import build_idempotency_key, get_document_code
from .openfactura_mapper_account_move import OpenfacturaAccountMoveMapper
from .openfactura_mapper_pos import OpenfacturaPosMapper


class OpenfacturaEmissionService:
    def __init__(self, env, company):
        self.env = env
        self.company = company
        self.client = env['openfactura.document']._get_client(company)

    def _source_meta(self, source_record, source_channel):
        return {
            'source_model': source_record._name,
            'source_res_id': source_record.id,
            'source_channel': source_channel,
            'company_id': source_record.company_id.id,
        }

    def _create_or_get_document(self, source_record, source_channel, document_type, payload):
        source_meta = self._source_meta(source_record, source_channel)
        idem_key = build_idempotency_key(
            source_record.company_id.id,
            source_channel,
            source_record._name,
            source_record.id,
            document_type,
        )
        existing = self.env['openfactura.document'].search([
            ('company_id', '=', source_record.company_id.id),
            ('idempotency_key', '=', idem_key),
        ], limit=1)
        if existing and existing.state in ('sent', 'accepted'):
            return existing, idem_key, True
        if existing:
            existing.write({'state': 'sending', 'request_payload': json.dumps(payload), 'sent_at': fields.Datetime.now(), 'error_message': False})
            return existing, idem_key, False

        values = {
            'name': source_record.display_name,
            'document_type': document_type,
            'idempotency_key': idem_key,
            'currency_id': source_record.currency_id.id,
            'amount_total': source_record.amount_total,
            'amount_tax': source_record.amount_tax,
            'amount_untaxed': source_record.amount_total - source_record.amount_tax,
            'state': 'sending',
            'request_payload': json.dumps(payload),
            'sent_at': fields.Datetime.now(),
            **source_meta,
        }
        if source_channel == 'pos':
            values.update({'pos_order_id': source_record.id, 'pos_config_id': source_record.config_id.id, 'partner_id': source_record.partner_id.id})
        else:
            values.update({'account_move_id': source_record.id, 'partner_id': source_record.partner_id.id})
        document = self.env['openfactura.document'].create(values)
        return document, idem_key, False

    def emit_from_pos(self, order, document_type):
        OpenfacturaPosMapper.validate(order, document_type)
        payload = OpenfacturaPosMapper.payload(order, document_type, get_document_code(document_type))
        return self._emit(source_record=order, source_channel='pos', document_type=document_type, payload=payload)

    def emit_from_account_move(self, move, document_type='invoice'):
        OpenfacturaAccountMoveMapper.validate(move, document_type)
        code = OpenfacturaAccountMoveMapper.resolve_document_code(move, document_type)
        payload = OpenfacturaAccountMoveMapper.payload(move, document_type, code)
        return self._emit(source_record=move, source_channel='account_move', document_type=document_type, payload=payload)

    def _emit(self, source_record, source_channel, document_type, payload):
        document, idem_key, already_sent = self._create_or_get_document(source_record, source_channel, document_type, payload)
        if already_sent:
            return document
        try:
            response = self.client.call('emit_document', payload=payload, idempotency_key=idem_key)
            data = response.get('data', {})
            document.write({
                'state': 'sent',
                'external_id': data.get('id') or data.get('external_id'),
                'folio': str(data.get('folio') or ''),
                'number': str(data.get('numero') or ''),
                'response_payload': response.get('raw'),
                'response_code': response.get('status'),
                'response_at': fields.Datetime.now(),
                'correlation_id': response.get('correlation_id'),
            })
            OpenfacturaAttachmentService(self.env).attach_document_payloads(
                document,
                pdf=data.get('pdf'),
                xml=data.get('xml'),
                json_raw=response.get('raw'),
            )
            source_record.message_post(body=_('Documento Openfactura emitido correctamente. Folio: %s') % (document.folio or '-'))
            return document
        except Exception as err:
            document.write({'state': 'retry', 'error_message': str(err), 'response_at': fields.Datetime.now()})
            source_record.message_post(body=_('Error de emisión Openfactura: %s') % err)
            raise UserError(_('No se pudo emitir en Openfactura. Revise el documento técnico para detalle.'))
