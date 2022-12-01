import pickle
import sys
from redis import Redis
from utils.logger import log
from config import Config


class Cache:
    def __init__(self) -> None:
        self._conf = Config()
        try:
            self._redis = Redis(
                host=self._conf.REDIS_HOST,
                port=self._conf.REDIS_PORT,
                password=self._conf.REDIS_PASS
                )
        except Exception as err:
            log.critical(f'No se pudo extablecer conexión con redis. Error: {err}')
            sys.exit()
    
    def persist(self, key: str, val, exp: int=3600):
        '''Persists data to a redis database as a pickle.
        
        Params:
        -------
        - key: string;
        - val: any value you want;
        - exp: expiration time. By default, it is 1 hour'''
        self._redis.set(key, pickle.dumps(val), ex=exp)
        log.info(f'Nueva info en caché para {key}.')
        return val

    def load(self, key: str):
        '''Loads a previously persisted pickled data.
                
        Params:
        -------
        - key: string.'''
        data = self._redis.get(key)
        if data is None:
            return None
        return pickle.loads(data)

    def check(self):
        try:
            return self._redis.ping()
        except Exception as err:
            log.critical(err)
            sys.exit()