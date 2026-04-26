from utils.logger import get_logger
from extract.client import FreshDeskClient

logger = get_logger(__name__)

class TicketsExtractor:
    def __init__(self):
        self.client = FreshDeskClient()

    def get_all_tickets(self):
        return self.get_incremental_tickets('2010-01-01T00:00:00Z')
    
    def get_incremental_tickets(self, since_timestamp):
        result = []
        for page in self.client._get_all_pages('tickets', params={'updated_since': since_timestamp}):
            result.extend(page)
        logger.info(f"Extracted {len(result)} tickets")

        return result