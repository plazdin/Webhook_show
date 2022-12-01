import sys
import pyodbc
from config import Config
from utils.logger import log

class DBM:
    _conf = Config()
    def __init__(self) -> None:
        try:
            #self.conx = pyodbc.connect(f'DRIVER={self._conf.DB_DRIVER};SERVER={self._conf.SERVER};\
            #                DATABASE={self._conf.DB};UID={self._conf.USER};PWD={self._conf.PASS}')
            self.conx = pyodbc.connect(f'DSN={self._conf.DSN};SVADR={self._conf.SVADR};\
                PTNUM={self._conf.PTNUM};UID={self._conf.DBMUSER};PWD={self._conf.DBMPASS}')
            #SVARD=10.200.1.1;PTNUM=1102;UID=PYTHON;PWD=chevro2022
        except Exception as err:
            print(err)

        self.cursor = self.conx.cursor()
    
    def query(self, query_str: str, proc: bool=False, commit: bool=False, rtc: bool=False):
        '''
        Params:
        -------
        - query_str: Self explainatory.
        - proc: procesure. Set to True to return nothing but a notification if insert / update is successfull.
        - commit: If the operations needs to be commited. Default False.
        - rtc: Stands for ReTurn Cursor instead of a list from cursor.fetchall(). Default False.'''
        try:
            self.cursor.execute(query_str)
            
            if commit == True:
                self.conx.commit()
            
            if rtc == True:
                return self.cursor
            
            if proc == True:
                log.info('Procedure executed successfully')
                return

            rows = self.cursor.fetchall()
            return rows
            
        except Exception as err:
            log.error(err)
            return None
