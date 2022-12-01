from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    expires: str


class UserLoginSchema(BaseModel):
    username: EmailStr
    password: str