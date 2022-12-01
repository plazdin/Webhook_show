import requests
from config import Config as conf
from database.redis_conn import Cache
from utils.logger import log

def get_token() -> dict:
    '''Returns a bearer token to access CAR API Webhooks.'''

    token_key = 'sim1tech_CAR_token'
    cache = Cache()
    token = cache.load(token_key)
    if token is None:
        log.info('No hay registros de token en caché. Creando registros.')
        r = requests.post(
        f'{conf().API_URL}/auth/login',
        headers={
            'accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded'},
        data=f'username={conf().CAR_USER}&password={conf().CAR_PASS}')
        
        token = r.json()['access_token']
        cache.persist(token_key, token, exp=863500)
    else:
        log.info('Token encontrado en cache!')
    
    return token
