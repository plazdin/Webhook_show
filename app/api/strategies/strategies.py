from datetime import datetime

from api.strategies.client_operations import insert_new_client, update_dbm_client
from crud import clients
from exceptions import ApiException
from schemas import Transaction, Response, ErrorResponse
from utils.logger import log


def verify_fields(keys: list) -> list:
    '''Verifies that the payload is complete whit all fields required for the transaction.'''
    pl_required_fields = [
            'id', 'vat_number', 'firstname',
            'lastname', 'address', 'city','state',
            'email', 'telephone', 'zipcode',
            'type', 'country', 'birthdate'
    ]
    missing = []
    for field in pl_required_fields:
        if field not in keys:
            missing.append({
                'field': field,
                'message': 'DMS_REQUIRED_PARAMETER'
                })
    return missing
        

def client_strategy(obj: Transaction) -> Response:
    '''Client operations when CAR sends data to San Jorge.'''

    response = {
        'controller': obj.controller,
        'issued': datetime.now().isoformat(),#.strftime('%Y-%m-%d %H:%M:%S'),
        'success': True
    }

    jsn = obj.object

    if obj.operation == 'insert':
        # Verification of required fields in the insert.
        errors = verify_fields(jsn.keys())    

        if len(errors) > 0:
            log.error(f'Payload incompleto. \
                Campos requeridos: {", ".join([n["field"] for n in errors])}')
            response['error'] = errors
            response['success'] = False
            
            raise ApiException(
                status_code=400,
                content=response)

        car_id = jsn['id']
        result = insert_new_client(jsn)
        
        if result[0] == 200:
            new_id = result[1]
            clients.create_client_index([(car_id, new_id)])
            response['data'] = f'Succesfully inserted with id {new_id}.'
            return response

        if result[0] == 409:
            log.error(f'Car id {car_id} ya existe en DBM como id {result[1]}.')
            response['data'] = f'Existant element with id {result[1]}'
            response['success'] = False
            response['error'] = [{
                        'field': 'id',
                        'error': '10004_DMS_ELEMENT_ALREADY_EXSITS'
                        }]
            raise ApiException(
                status_code=result[0],
                content=response)
        

    if obj.operation == 'update':
        upd_response = update_dbm_client(jsn)
        
        if upd_response[0] == 200:
            response['data'] = f'Car Client {jsn["id"]} updated successfully.'
            return response

        elif upd_response[0] == 404:
            response['success'] = False
            response['error'] = [{
                        'field': 'id',
                        'message': '10003_DMS_ELEMENT_NOT_FOUND'
                    }]
            raise ApiException(
                status_code=upd_response[0],
                content=response)


def vehicle_strategy():
    issued = datetime.now()
    pass


def schededule_strategy():
    issued = datetime.now()
    pass