from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from uvicorn import run

from contextlib import asynccontextmanager

from loguru import logger
from pydantic import ValidationError
from os import path, makedirs

from services import InitAgentService
from validators import InitAgentSchema
from middlewares import IfEndpointNotExists
from exceptions import UnicornException
from config import GEMINI_API_KEY, GEMINI_MODEL_NAME, TEMPLATE, TEMPORARY_STORE

from routers import agent_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not path.exists(TEMPORARY_STORE):
        makedirs(TEMPORARY_STORE)

    try:
        schema = InitAgentSchema(
            gemini_api_key=GEMINI_API_KEY,
            gemini_model_name=GEMINI_MODEL_NAME,
            template=TEMPLATE
        )
            
        service = InitAgentService(**schema.model_dump())
        agent = service()
        app.state.agent = agent

        logger.success('The agent initialized success')

        yield

    except ValidationError as e:
        errors = e.errors()
        err_description = errors[0].get('msg')
        logger.error(err_description)

    except Exception as e:
        logger.error(f'Unexpected error: {str(e)}')

app = FastAPI(
    title='MailmanAI',
    description='MailmanAI - An AI agent for extracting recipients from files and pre-written emails, ' \
                'as well as for sending emails',
    version='0.0.1',
    redoc_url=None,
    docs_url='/api/docs',
    lifespan=lifespan
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'status': False,
            'err_description': str(exc.detail)
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    err_description = errors[0].get('msg')

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'status': False,
            'err_description': err_description
        },
    )

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'status': False,
            'err_description': exc.err_description
        },
    )

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_headers=['*'],
    allow_methods=['*'],
    allow_origins=['*']
)

app.add_middleware(IfEndpointNotExists)

app.include_router(router=agent_router, prefix='/api', tags=['API'])

if __name__ == '__main__':
    run('main:app', host='0.0.0.0', port=8001, reload=True)