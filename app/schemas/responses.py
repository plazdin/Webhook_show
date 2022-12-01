from datetime import datetime

from typing import Literal, Optional
from pydantic import BaseModel



# As CAR integrations documentation suggests...
errors = {
    1: '10001_DMS_INVALID_PARAMETER',
    2: '10002_DMS_MAX_LENGTH_REACHED',
    3: '10003_DMS_ELEMENT_NOT_FOUND', # (UPDATE/DELETE)
    4: '10004_DMS_ELEMENT_ALREADY_EXISTS' # (INSERT)
}


class Response(BaseModel):
    controller: Literal['client', 'vehicle', 'schedule']
    success: bool = True
    data: Optional[str]
    issued: datetime
    

class FieldError(BaseModel):
    field: str
    message: str


class ErrorResponse(Response):
    success: bool = False 
    error: list[FieldError]



