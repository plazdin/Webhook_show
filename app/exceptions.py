import schemas


class ApiException(Exception):
    def __init__(self, status_code: int, 
    content: schemas.ErrorResponse):
        self.status_code = status_code
        self.content = content