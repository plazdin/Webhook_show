#system imports
from datetime import datetime

from fastapi import APIRouter, Depends

from api import strategies
from auth.auth_bearer import JWTBearer
import schemas
from utils.logger import log

webhook = APIRouter(tags=['WebHook'])


@webhook.post('/webhook', dependencies=[Depends(JWTBearer())],
    response_model=schemas.Response,
    summary=' ',
    responses={
        404: {'model': schemas.ErrorResponse},
        409: {'model': schemas.ErrorResponse},
        422: {'model': schemas.ErrorResponse}
    })
async def whook(obj: schemas.Transaction):
    log.info('Nueva transacción.')
    issued = datetime.now()

    if obj.controller == 'client':
        result = strategies.client_strategy(obj)
        return result

    elif obj.controller == 'vehicle':
        pass
        # vehicle_strategy()
    else:
        pass
        # schededule_strategy()
