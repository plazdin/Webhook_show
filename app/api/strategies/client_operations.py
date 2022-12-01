from datetime import datetime, date
from typing import List, Tuple

from crud import clients
from utils import log



def format_date(date: int | str) -> str | None:
    '''Creates an isoformat datestring from a date obtained in MACLI1 from 
    macli1 table in SJ database
    
    Param:
    ------
    - date: MC_FENAC. Should be a 6-length or 8-length int variable'''
    
    # this is only for testing purposes
    if isinstance(date, int):
        if date == 0:
            return None
        date = str(date)
    
    log.debug(f'{date}, {len(date)}')

    if len(date) == 5:
        date = date.rjust(6, '0')
    if len(date) == 6:
        str_time = datetime.strptime(date, '%y%m%d')
        cyp = int(datetime.now().strftime('%Y')[:2])
      
        if int(str(date)[:2]) > int(cyp):
            cyp = str(int(cyp) - 1)
        
        bd = str_time.strftime(f'{cyp}%y%m%d')
        birthdate = datetime.strptime(bd, '%Y%m%d').isoformat(timespec='seconds')


    if len(str(date)) == 8:
        str_time = datetime.strptime(str(date), '%Y%m%d')
        birthdate = str_time.isoformat(timespec='seconds')
    
    return birthdate


def client_format(c_body: dict) -> tuple:
    '''Formats the object that's going to be added to SJ database.
    
    Params:
    -------
    - c_body: Body of the client. Extracted from the object field that is sended by CAR.'''

    dk = c_body.keys()
    # Formateado de nombre de cliente
    firstname = c_body['firstname'] if 'firstname' in dk else ''
    lastname = c_body['lastname'] if 'lastname' in dk else ''
    s_lastname = c_body['secondlastname'] if 'secondlastname' in dk else ''
    razon_soc = f'{lastname} {s_lastname} {firstname}'.strip()
    if len(razon_soc) > 30:
        razon_soc1, razon_soc2 = razon_soc[:30], razon_soc[30:].ljust(30)
    else:
        razon_soc1 = razon_soc.ljust(30)
        razon_soc2 = ''.ljust(30)


    # Formateo de dirección
    if 'address' in dk:
        address = c_body['address']
        if len(address) > 30:
            address = address[:30]

    # Formateo de personería
    if 'type' in dk:
        if c_body['type'] == 0:
            personeria = 'F'
        elif c_body['type'] == 1:
            personeria = 'J'
        else:
            personeria = None

    else:
        personeria = None

    if 'birthdate' in dk:
        bd_str = datetime.fromisoformat(c_body['birthdate'])
        fenac = bd_str.strftime('%Y%m%d')
    else:
        fenac = None


    values = (
        int(c_body['vat_number'].replace('.','')),                                                  # 0 DNI
        f'{razon_soc1}',                                                            # 1 Nombre1
        f'{razon_soc2}',                                                            # 2 Nombre2
        f'{address}',                                                     # 3 Dirección - calle
        f'{c_body["city"]}' if 'city' in dk else f'',                               # 4 Ciudad
        f'{c_body["state"].upper()}',                                               # 5 Provincia
        c_body["email"] if 'email' in dk else '',                                   # 6 Email
        f'{c_body["telephone"].replace(" ", "").replace("(", "").replace(")", "")}'
            if 'telephone' in dk else '',                                           # 7 Teléfono
        
        int(c_body['zipcode']),                                                     # 8 Código Postal
        f'{personeria}' if personeria else None,                                    # 9 Persona Jurídica o Entidad
        f'{c_body["country"]}' if 'country' in dk else '',                          # 10 País
        int(fenac) if fenac else None                                               # 11 Nacimiento
    )
    return values


def masive_client_format(limit: int = None, client: int = None) -> list[dict]:
    '''Formats client or clients that are going to be pushed to CAR API.
    
    Params:
    -------
    limit: The limit of clients that are fetched from DBMaker.
    client: The specific client (this is for updates from DBM to CAR.)'''
    rows = clients.get_dbm_clients(limit=limit, client=client)
    clients_list = []
    
    for r in rows:

        client_name = f'{r.MC_RAZONSOC1.strip()}{r.MC_RAZONSOC2.strip()}'
        address = '{}{}{}{}'.format(
            str(r.MC_CALLE).strip() + ' ' if len(str(r.MC_CALLE).strip()) > 2 else '',
            r.MC_NUMERO if r.MC_NUMERO is not None and len(str(r.MC_NUMERO).strip()) > 0 else '',
           ' ' + r.MC_PISO.strip() if r.MC_PISO is not None
           and len(r.MC_PISO.strip()) > 0 else '',
            ' ' + r.MC_DPTO.strip() if r.MC_DPTO is not None and
            len(r.MC_DPTO.strip()) > 0 else ''
        )
        if r.MC_FENAC is not None:
            birthdate = format_date(r.MC_FENAC)
        else:
            birthdate = None

        client_body = {
    'DBM_ID': str(r.MC_CLIENTE).strip(),
    'vat_number': int(r.MC_NUMDOC),
    'firstname': client_name,
    'lastname': client_name,
    'address': address if len(address) > 1 else None,
    'city': r.MC_LOCAL.strip() 
        if len(r.MC_LOCAL.strip()) > 1 else None,

    'state':r.PROVINCIA.strip()
        if len(r.PROVINCIA.strip()) > 1 else None,

    'email': r.EMAIL.strip() if r.EMAIL else None,
    'telephone':r.TEL.strip() 
        if len(r.TEL.strip()) > 1 else None,

    'mobile': r.MCT_TEL.strip() if r.MCT_TEL else None,
    'zipcode': r.MC_CODPOS if r.MC_CODPOS != 0 else None,
    'send_commercial': 0,
    'type': r.MC_PERSONERIA,
    'number_family_members': None,
    'birthdate': birthdate
        }
        clients_list.append(client_body)

    return clients_list


def insert_new_client(c_body: dict) -> tuple:
    '''Inserts a client into the SJ database.
    
    Params:
    -------
    - c_body: Body of the client. Extracted from the object field that is sended by CAR.'''

    car_client = c_body['id']
    log.info('Verificando si entrada existe.')
    existant_client = clients.get_client_index(car_client_id=car_client)
    if existant_client != None:
        return (409, existant_client)

    new_client_id = clients.get_last_nupar()
    clients.update_nupar(new_client_id)

    client_v = list(client_format(c_body))
    values = [new_client_id] + client_v

    mactel_values = [values.pop(7), values[7]]
    values = tuple(values)

    log.debug('Insertando nuevo cliente.')
    clients.insert_client(values)

    if len(mactel_values[0].strip()) > 0: # Inserto email en tabla mactel
        log.debug('Insertando EMAIL.')
        clients.insert_client_mct(
            new_client_id, mactel_values[0],
            mct_type='M')
    
    if len(mactel_values[1].strip()) > 0: # Inserto teléfono en tabla mactel
        log.debug('Insertando TELEFONO.')
        clients.insert_client_mct(new_client_id, mactel_values[1])

    return (200, new_client_id)


def update_dbm_client(c_body: dict) -> tuple:
    '''Updates SJ client.

    Params:
    -------
    - c_body: Body of the client. Extracted from the object field that is sended by CAR.'''

    car_client = c_body['id']
    mc_client = clients.get_client_index(car_client_id=car_client)    
    if mc_client == None:
        return (404,)

    client_values = list(client_format(c_body))
    client_values.pop(6)
    client_values.append(mc_client)

    clients.update_client(tuple(client_values))
    return (200, mc_client)
