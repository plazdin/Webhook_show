from re import U
from fastapi import APIRouter, Body, Form
from fastapi.responses import JSONResponse

from auth.auth_handler import signJWT
from schemas.login import UserLoginSchema, TokenResponse
from schemas.error import ValidationError
from crud.user import check_user


login = APIRouter(tags=['Auth'])

@login.post(
    '/login',
    response_model=TokenResponse,
    responses={
        422: {'model': ValidationError}
    },
    summary=' ')
async def user_login(username:str = Form(), password:str = Form()):
    user = UserLoginSchema(username=username, password=password)
    if check_user(user):
        return signJWT(user.username)
    return JSONResponse(status_code=401,
    content={'error_message':'Wrong login details!'})

