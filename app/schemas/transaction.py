from typing import Literal, Optional
from pydantic import BaseModel

class Transaction(BaseModel):
    controller: Literal['client', 'vehicle', 'schedule']
    operation: Literal['insert', 'update']
    object: dict #puede ser cualquier objeto que permita una operation.