from datetime import datetime

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
import schemas
from pydantic.error_wrappers import ValidationError
from starlette.responses import JSONResponse

from api.webhook import webhook
from api.user_login import login
from exceptions import ApiException


app = FastAPI(
    title='DBMWebHook',
    description='Interface para el intercambio de datos entre\
        Automóviles San Jorge y servicios externos.')

app.include_router(login)
app.include_router(webhook)


@app.exception_handler(RequestValidationError)
async def http_exception_handler(request, exc):
    errors = list()
    for err in exc.errors():
        errors.append({
            'field': err['loc'][1],
            'message': err['msg']
            })
    return JSONResponse(
        status_code=422,
        content={
            'success': False,
            'error': errors,
        })


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    errors = list()
    for err in exc.errors():
        errors.append({
            'field': err['loc'][0],
            'message': err['msg']
            })
    
    return JSONResponse(
        status_code=422,
        content={
            'success':False,
            'error':errors
        })


@app.exception_handler(ApiException)
async def common_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.content
    )