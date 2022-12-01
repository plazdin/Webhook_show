import logging
import os
from datetime import timedelta


log = logging.getLogger('PURGE')
if os.getenv('DEBUG') == 'True':
    log.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")

file_handler = logging.FileHandler('PURGE.log', encoding='utf-8')
log.addHandler(file_handler)

console = logging.StreamHandler()
if os.getenv('DEBUG') == 'True':
    print('debug activado')
    console.setLevel(logging.DEBUG)

console.setFormatter(formatter)
log.addHandler(console)

def timer_format(tm):
    return str(timedelta(seconds = tm))
