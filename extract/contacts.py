from utils.logger import get_logger
from extract.client import FreshDeskClient

logger = get_logger(__name__)

class ContactsExtractor:
    def __init__(self):
        self.client = FreshDeskClient()

    def get_all_contacts(self):
        return self.get_incremental_contacts('2010-01-01T00:00:00Z')
    
    def get_incremental_contacts(self, since_timestamp):
        result = []
        for page in self.client._get_all_pages('contacts', params={'updated_since': since_timestamp}):
            result.extend(page)
        logger.info(f"Extracted {len(result)} contacts")

        return result