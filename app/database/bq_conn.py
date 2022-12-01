import sys
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
from config import Config
from utils.logger import log


class BQuery:

    def __init__(self) -> None:
        self._conf = Config()
        try:
            self._cred = Credentials.from_service_account_file(self._conf.JSONPATH)
        except Exception as err:
            log.critical(err)
            sys.exit()
    
    def query(self, query):
        client = bigquery.Client(
            credentials=self._cred,
            project='bd-sanjorge')
        job = client.query(query)
        return job.result()