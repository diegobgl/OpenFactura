class OpenfacturaStatusService:
    STATUS_MAP = {
        'accepted': 'accepted',
        'rejected': 'rejected',
        'sent': 'sent',
        'pending': 'pending_status',
    }

    @classmethod
    def normalize(cls, external_status):
        return cls.STATUS_MAP.get((external_status or '').lower(), 'pending_status')
