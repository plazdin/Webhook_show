from datetime import datetime

from typing import List, Tuple

from database import dbm, bq
from utils import log


# Big query interactions
def create_client_index(ids: List[Tuple[int]]):
    '''Updates the index in bigquery.
    Format is [(CAR_ID, MC_CLIENTE),].'''
    
    if len(ids) > 1:
        values = ',\n'.join([f'{tup}' for tup in ids])
    else:
        values = f'{ids[0]}'

    result = bq.query('INSERT INTO bd-sanjorge.SIMTEC.CLIENTES (CAR_ID, MC_CLIENTE)\
                     VALUES%s;' % values)
    return result


def get_client_index(sj_client_id: int = None, car_client_id: int = None) -> int | None:
    '''Returns equivalent client id from either CAR or San Jorge.
    
    Params:
    -------
    - sj_client_id: San Jorge MC_CLIENT id
    - car_client_id: Car Client id.'''
    if sj_client_id:
        query = bq.query(
            'select CAR_ID from bd-sanjorge.SIMTEC.CLIENTES\
            where MC_CLIENTE = %s' % sj_client_id)
        if query.total_rows > 0:
            return int(list(query)[0].CAR_ID)
    else:
        if car_client_id:
            query = bq.query(
            'select MC_CLIENTE from bd-sanjorge.SIMTEC.CLIENTES\
            where CAR_ID = %s' % car_client_id)
        if query.total_rows > 0:
            return int(list(query)[0].MC_CLIENTE)
    return None


def get_dbm_clients(limit: int = None, client: int = None) ->list[dict]:
    '''Query to extract client's neccesary data to be sended to CAR.
    
    Params:
    -------
    - limit: how many clients you want to extract.
    - client: specific client you want to extract.'''
    if limit:
        limit_str = ' limit %s' % limit
    else:
        limit_str = ''

    if client:
        client_str = ' and MC_CLIENTE = %s' % client
    else:
        client_str = ''

    rows = dbm.query('''
    SELECT MC_CLIENTE,MC_RAZONSOC1,MC_RAZONSOC2,MC_TIPODOC,MC_NUMDOC,MC_NUMEIVA,
	CASE MC_PERSONERIA
        WHEN 'J' THEN 1 
        ELSE 0 
        END MC_PERSONERIA,
        MC_TELEFONO TEL,
        MIN(TEL.MCT_TELEFONO)  MCT_TEL,
        MAX(MAIL.MCT_TELE1) EMAIL,
	PRO.PV_DETALLE PROVINCIA, 
	MC_NACION,MC_CALLE,MC_NUMERO,MC_PISO,
	MC_DPTO,MC_LOCAL,MC_CODPOS,MC_FENAC
    FROM SYSADM.MACLI1 M1
    LEFT OUTER JOIN SYSADM.PROVINC PRO ON PRO.PV_NUMERO = M1.MC_PROVI
	LEFT OUTER JOIN SYSADM.MACTEL TEL ON TEL.MCT_CLIENTE1 = M1.MC_CLIENTE AND TEL.MCT_TIPO = 'T'
	LEFT OUTER JOIN SYSADM.MACTEL MAIL ON MAIL.MCT_CLIENTE1 = M1.MC_CLIENTE AND MAIL.MCT_TIPO = 'M'
    WHERE M1.MC_REPUESTO != 'S' %s
    group by MC_CLIENTE,MC_RAZONSOC1,MC_RAZONSOC2,MC_TIPODOC,MC_NUMDOC,MC_NUMEIVA,MC_PERSONERIA,
    MC_TELEFONO,PRO.PV_DETALLE,MC_NACION,MC_CALLE,MC_NUMERO,MC_PISO,
	MC_DPTO,MC_LOCAL,MC_CODPOS,MC_FENAC %s
    ''' % (client_str, limit_str))

    return rows


def get_last_nupar() -> int:
    '''Function to extract last nupar (as the table MACLI has no index whatsoever, it is
    neccessary to extract this info from another table that has all tables last indexes.)'''
    log.debug('Obteniendo nuevo MC_CLIENTE.')
    result = dbm.query('SELECT RE_NUPAR FROM SYSADM.PARM\
        WHERE RE_TIPAR = \'CLI\'')

    last_nupar = int(result[0].RE_NUPAR)
    
    if last_nupar == None:
        return get_last_nupar()

    new_client_id = last_nupar + 1
    return new_client_id


def update_nupar(new_nupar: int) -> None:
    log.debug('Haciendo update de RE_NUPAR')
    result = dbm.query(  # Query para actualizar ultimo cliente.
        "UPDATE SYSADM.PARM SET RE_NUPAR = %s\
        WHERE RE_TIPAR = \'CLI\'" % new_nupar, proc=True, commit=True
        )


def insert_client(values: tuple) -> None:
    '''Query to insert new client into SJ database.'''
    dbm.query(
    '''INSERT INTO SYSADM.MACLI1 (
            MC_CLIENTE, MC_NUMDOC, MC_RAZONSOC1,
			MC_RAZONSOC2, MC_CALLE,
            MC_LOCAL, MC_PROVI, MC_TELEFONO, MC_CODPOS,
            MC_PERSONERIA, MC_NACION, MC_FENAC, MC_VACIO2, MC_REPUESTO
            )
        VALUES (%s, %s, \'%s\', \'%s\', \'%s\', \'%s\',
        (SELECT PV_NUMERO from SYSADM.PROVINC WHERE PV_DETALLE = \'%s\'),
        \'%s\', %s,\'%s\', \'%s\', %s, \'PYTHON\', \'N\')''' % values
        , proc=True, commit=True)


def insert_client_mct(client_id: int, tel: str, mct_type: str = 'T') -> None:
    '''Query to insert a client phone / email into MACTEL.
    
    Params:
    - client_id: client index id.
    - tel: either phone or email.
    - mct_type: \'T\' when tel is a phone, \'M\' when it\'s an email.'''
    if mct_type == 'M':
        prefijo = 'EMAIL'
        phone = tel
    else:
       prefijo, phone = tel[:7], tel[7:]     
    dbm.query(
            """INSERT INTO SYSADM.MACTEL(MCT_CLIENTE, MCT_PREFIJO, MCT_TELEFONO, MCT_TIPO)
            VALUES(%s, '%s', '%s', '%s');"""
            % (client_id, prefijo, phone, mct_type), proc=True, commit=True)


def update_client(c_body: tuple) -> None:
    '''Operation that updates a client information.
    
    Params:
    -------
    - c_body: object that is sended by car.
    - mc_client: index id of the client that is wanted to be updated.'''
    update_query = """UPDATE SYSADM.MACLI1 SET
                    MC_NUMDOC = %s,
                    MC_RAZONSOC1 = '%s',
			        MC_RAZONSOC2 = '%s',
                    MC_CALLE = '%s',
                    MC_LOCAL = '%s',
                    MC_PROVI = (SELECT COALESCE(PV_NUMERO,0)
                        FROM SYSADM.PROVINC 
                        WHERE PV_DETALLE = (UPPER(TRIM('%s')))),
                    MC_TELEFONO = '%s',
                    MC_CODPOS = %s,
                    MC_PERSONERIA = '%s',
                    MC_NACION = '%s',
                    MC_FENAC = %s,
                    MC_VACIO2= 'PYTHON'
                    WHERE MC_CLIENTE = %s""" % c_body
    dbm.query(update_query, proc=True, commit=True)
    log.debug(update_query)