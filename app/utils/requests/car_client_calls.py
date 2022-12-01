import requests

from typing import Tuple

from config import Config
from utils.login import get_token


token = get_token()
conf = Config()


headers = {
    'accept': '*/*',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}


def post_client(client: dict) -> Tuple[int] | None:
    '''Post client in in CAR api.
    
    Params:
    -------
    client: A dictionary of a client, specified in http://ws1.cloudactivereception.com/Api/Docs/#postclient
    
    Returns a tuple with both ids (CAR_ID, MC_CLIENTE).'''
    dbm_id = client.pop('DBM_ID')
    r = requests.post(f'{conf.API_URL}/Clients',
    headers=headers,
    json=client)
    if r.status_code != 201:
        print(r.json())
        return None
    indx = (r.json()['id'], int(dbm_id))
    return indx


def put_car_user(payload: dict, car_client_id: int):
    '''Updates a client in the CAR database.
    
    Params:
    -------
    payload: the client to be updated
    '''
    r = requests.put(
        f'{conf.API_URL}/Clients/{car_client_id}',
        headers=headers,
        json=payload
        )
    return r


def get_car_clients(limit=50, offset=0, car_id=None):
    url = f'{conf.API_URL}/Clients'
    if car_id:
        url += f'/{car_id}'
    r = requests.get(
         url,
         params={'offset': offset, 'limit':limit},
         headers=headers
    )
    return r


def delete_car_users(car_id:int):
    r = requests.delete(
         f'{conf.API_URL}/Clients/{car_id}',
         headers=headers
    )
    return r

