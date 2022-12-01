import bcrypt
from config import Config
from database import bq
from schemas.login import UserLoginSchema


def add_new_api_user():
    username = input('Ingrese nuevo usuario: ')
    email = input('Ingrese mail: ')
    passwd = bytes(input('Ingrese contraseña: '), 'utf-8')
    
    salt = bcrypt.gensalt()
    hs_pass = bcrypt.hashpw(passwd, salt)
    passwd = hs_pass.decode('utf-8')

    bq.query('insert into SIMTEC.login(username, email, password) VALUES(\'%s\',\'%s\',\'%s\')' % (username, email, passwd))


def check_user(user: UserLoginSchema) -> bool:
    result = bq.query('Select * from bd-sanjorge.SIMTEC.login where email = \'%s\'' % (user.username))
    if result.total_rows > 0:
        passw = list(result)[0].password
        if bcrypt.checkpw(bytes(user.password, 'utf-8'), bytes(passw, 'utf-8')):
            return True
    return False
