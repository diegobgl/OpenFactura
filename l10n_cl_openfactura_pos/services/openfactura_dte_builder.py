import hashlib


DOCUMENT_CODE_MAP = {
    'receipt': 39,
    'invoice': 33,
    'credit_note': 61,
    'debit_note': 56,
}


def build_idempotency_key(company_id, source_channel, source_model, source_res_id, document_type):
    base = f"{company_id}:{source_channel}:{source_model}:{source_res_id}:{document_type}"
    return hashlib.sha256(base.encode('utf-8')).hexdigest()


def get_document_code(document_type):
    return DOCUMENT_CODE_MAP[document_type]
