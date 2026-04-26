import os
import requests
from dotenv import load_dotenv
from utils.logger import get_logger
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

if os.path.exists('.env'):
    load_dotenv()

logger = get_logger(__name__)

class FreshDeskClient:
    def __init__(self):
        self.api_key = os.getenv('FRESHDESK_API_KEY')
        self.domain = os.getenv('FRESHDESK_DOMAIN')
        if not self.api_key or not self.domain:
            raise ValueError("FRESHDESK_API_KEY and FRESHDESK_DOMAIN must be set")

        self.base_url = f'https://{self.domain}.freshdesk.com/api/v2'
        self.auth = (self.api_key, 'X')
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        self.session = session

    def _get(self, endpoint, params=None):
        full_url = f'{self.base_url}/{endpoint}'
        response = self.session.get(full_url, auth=self.auth, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def _get_all_pages(self, endpoint, params=None):
        page = 1
        while True:
            request_params = {'per_page': 100, 'page': page}
            if params:
                request_params.update(params)
            logger.info(f"Fetching {endpoint} page {page}")
            result = self._get(endpoint, params=request_params)
            if not result:
                break
            yield result
            page += 1