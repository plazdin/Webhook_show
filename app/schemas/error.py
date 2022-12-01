from pydantic import BaseModel
from typing import Literal


class ErrorResponse(BaseModel):
    controller: Literal['client', 'vehicle', 'schedule']
    error_message: str
    isued: str


class ValidationError(BaseModel):
    error_messages: dict


