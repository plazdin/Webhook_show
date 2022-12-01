import os
from dotenv import dotenv_values, load_dotenv

class Config:
    '''Inicia la obtención de variables de entorno.'''
    def __init__(self) -> None:
        load_dotenv()
        self.__dict__.update({
            **dotenv_values(os.environ['CAR_CONFIG']),
            **dotenv_values(os.environ['DB_CREDENTIALS']),
            **dotenv_values(os.environ['DB_SETTINGS']),
            **dotenv_values(os.environ['JWT']),
            **dotenv_values(os.environ['REDIS_SETTINGS'])
        })
    def __repr__(self):
        return(f'Avilable keys:\n{", ".join(self.__dict__.values())}')

if __name__ == '__main__':
    print(Config())
