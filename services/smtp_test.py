from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPException
from aiohttp.client_exceptions import ClientResponseError
from aiohttp.http_exceptions import HttpProcessingError

from typing import Optional

from asyncio import sleep
from bs4 import BeautifulSoup
from loguru import logger

class SMTPTestService:
    def __init__(
        self,
        SMTP_server: str,
        SMTP_account: str,
        SMTP_password: str
    ):
        self._SMTP_server = SMTP_server
        self._SMTP_account = SMTP_account
        self._SMTP_password = SMTP_password

    async def _send_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
    ):
        response = {
            'status': False,
            'err_description': None,
            'data': {}
        }

        try:
            async with ClientSession() as session:
                async with session.request(
                    url=url,
                    method=method,
                    headers=headers,
                    data=data
                ) as request:
                    request.raise_for_status()

                    text = await request.text()

            response['data']['text'] = text
            response['status'] = True

        except HTTPException as e:
            response['err_description'] = e.text

        except (ClientResponseError, HttpProcessingError) as e:
            response['err_description'] = e.message

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        return response

    async def __call__(self) -> dict:
        response = {
            'status': False,
            'err_description': None,
            'data': {}
        }

        try:
            create_test = await self._send_request(
                method='POST',
                url='https://wwwhelper2.gmass.co/smtptest/createtest',
                data={
                    'SmtpServer': self._SMTP_server,
                    'username': self._SMTP_account,
                    'password': self._SMTP_password,
                    'from': self._SMTP_account,
                    'to': self._SMTP_account
                }
            )

            # logger.debug(create_test)

            if not create_test['status']:
                response['err_description'] = create_test['err_description']
                return response

            test_id = create_test['data']['text'].strip('"')

            await sleep(1.5)

            test_status = await self._send_request(
                method='GET',
                url=f'https://wwwhelper2.gmass.co/smtptest/teststatus?testId={test_id}'
            )

            # logger.debug(test_status)

            if not test_status['status']:
                response['err_description'] = test_status['err_description']
                return response

            text = test_status['data']['text']
            soup = BeautifulSoup(text, 'html.parser')
            errors = soup.find_all('div', class_='error')

            if errors:
                error = errors[0]
                response['err_description'] = error.get_text()
                return response

            response['status'] = True

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        return response