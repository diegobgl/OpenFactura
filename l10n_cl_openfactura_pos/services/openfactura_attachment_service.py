import base64


class OpenfacturaAttachmentService:
    def __init__(self, env):
        self.env = env

    def _create_attachment(self, record, filename, content):
        if not content:
            return False
        return self.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'res_model': record._name,
            'res_id': record.id,
        })

    def attach_document_payloads(self, document, pdf=None, xml=None, json_raw=None):
        if pdf:
            document.pdf_attachment_id = self._create_attachment(document, f'{document.name}.pdf', pdf)
        if xml:
            document.xml_attachment_id = self._create_attachment(document, f'{document.name}.xml', xml)
        if json_raw:
            document.json_attachment_id = self._create_attachment(document, f'{document.name}.json', json_raw)
