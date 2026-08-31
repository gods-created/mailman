from fastapi import (
    APIRouter, Request, Depends, BackgroundTasks,
    Form, File, UploadFile, status
)
from fastapi.responses import JSONResponse

from langgraph.graph.state import CompiledStateGraph

from exceptions import UnicornException, SerializerException
from validators import ExecuteSchema
from services import SMTPTestService
from signals import delete_old_accounts

from json import loads, JSONDecodeError
from uuid import uuid4 

from os.path import join

from pydantic import ValidationError
from loguru import logger
from argon2 import PasswordHasher

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from serializers import AccountSerializer

from config import TEMPORARY_STORE, DB_URL

async def _if_agent_initialized(request: Request) -> None:
    if not hasattr(request.app.state, 'agent'):
        raise UnicornException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            err_description='Agent didn\'t initialize'
        )
    
async def _file_handler(file: UploadFile = File(...)) -> str:
    filename = str(file.filename)

    if not any((
        filename.endswith('.csv'),
        filename.endswith('.xlsx')
    )):
        raise UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            err_description='Invalid file extension (only .csv and .xlsx)'
        )

    path_to_file = join(TEMPORARY_STORE, f'{uuid4().hex}_{filename}')

    with open(path_to_file, mode='wb') as f:
        f.write(await file.read())

    return path_to_file

async def _data_handler(data: str = Form(...)) -> str:
    try:
        json_data = loads(data)

        try:
            validated_data = ExecuteSchema(**json_data)
        except ValidationError as e:
            errors = e.errors()
            err_description = errors[0].get('msg')

            raise UnicornException(
                status_code=status.HTTP_400_BAD_REQUEST,
                err_description=err_description
            )

        account_exists = False
        account_found = False

        if DB_URL is not None:
            try:
                engine = create_engine(
                    url=DB_URL,
                    pool_size=1,
                    echo=False
                )

                with Session(bind=engine) as db_connection:
                    serializer = AccountSerializer(db_connection)

                    res = serializer.select(
                        smtp_account=validated_data.SMTP_account
                    )

                    if not res['status']:
                        raise SerializerException(
                            res['err_description']
                        )

                    accounts = res['data']['accounts']
                    accounts = delete_old_accounts(serializer, accounts)

                    if len(accounts) > 0:
                        account_found = True
                        account = accounts[0]

                        try:
                            ph = PasswordHasher()
                            ph.verify(
                                account.smtp_password,
                                validated_data.SMTP_password
                            )
                            account_exists = True

                        except:
                            pass

                engine.dispose()

            except SQLAlchemyError as e:
                logger.error(
                    f'SQLALchemy error during job with AccountSerializer: {str(e)}'
                )

            except SerializerException as e:
                logger.error(str(e))

            except Exception as e:
                logger.error(
                    f'Unexpected error during job with AccountSerializer: {str(e)}'
                )

        else:
            logger.warning('\'DB_URL\' is not specified')

        if not account_exists:
            service = SMTPTestService(
                SMTP_server=validated_data.SMTP_server,
                SMTP_account=validated_data.SMTP_account,
                SMTP_password=validated_data.SMTP_password
            )

            response = await service()

            if not response['status']:
                err_description = response['err_description']

                raise UnicornException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    err_description=(
                        'SMTP error: Username and Password not accepted'
                        if 'ERROR:  535' in err_description
                        else err_description
                    )
                )

            if DB_URL is not None and not account_found:
                try:
                    engine = create_engine(
                        url=DB_URL,
                        pool_size=1,
                        echo=False
                    )

                    with Session(bind=engine) as db_connection:
                        serializer = AccountSerializer(db_connection)

                        res = serializer.insert(
                            smtp_server=validated_data.SMTP_server,
                            smtp_account=validated_data.SMTP_account,
                            smtp_password=validated_data.SMTP_password
                        )

                        if not res['status']:
                            raise Exception(res['err_description'])

                    engine.dispose()

                except SQLAlchemyError as e:
                    logger.error(
                        f'SQLALchemy error during job with AccountSerializer: {str(e)}'
                    )

                except SerializerException as e:
                    logger.error(str(e))

                except Exception as e:
                    logger.error(
                        f'Unexpected error during job with AccountSerializer: {str(e)}'
                    )

        message = f'''
            Use the uploaded file to generate emails for each recipient.

            The exact file path is:
            [FILE]

            The SMTP server is:
            {validated_data.SMTP_server}

            The SMTP account is:
            {validated_data.SMTP_account}

            The SMTP password is:
            {validated_data.SMTP_password}

            The email subject is:
            {validated_data.subject}

            The email template/content is:
            {validated_data.mail}

            CRITICAL:
            When calling read_table, use EXACTLY this path:

            [FILE]

            Do not change the filename.
            Do not invent a different filename.
            Do not use "input.csv".
        '''

        return message

    except JSONDecodeError:
        raise UnicornException(
            status_code=status.HTTP_400_BAD_REQUEST,
            err_description='Invalid data format (only JSON)'
        )
    
agent = APIRouter(
    prefix='/agent',
    tags=['AGENT'],
    default_response_class=JSONResponse,
    dependencies=[Depends(_if_agent_initialized)]
)

@agent.post('/execute')
async def execute(
    request: Request,
    background_task: BackgroundTasks,
    data: str = Depends(_data_handler),
    file: UploadFile = Depends(_file_handler)
) -> JSONResponse:
    agent: CompiledStateGraph = request.app.state.agent

    path_to_file: str = str(file)
    message: str = data.replace('[FILE]', path_to_file)
    background_task.add_task(agent.ainvoke, input={'messages': [('human', message)]})

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'status': True,
            'err_description': None,
            'data': {
                'messgage': 'The task in progress'
            }
        }
    )