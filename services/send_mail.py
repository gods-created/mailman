from typing import List, Dict, Optional

from loguru import logger

from asyncio import to_thread

from SMTPEmail import SMTP

class SendMailService:
    def __init__(
        self,
        SMTP_server: str,
        SMTP_account: str,
        SMTP_password: str,
        subject: Optional[str] = None
    ):  
        self._SMTP_server = SMTP_server
        self._SMTP_account = SMTP_account
        self._SMTP_password = SMTP_password
        self._subject = subject

        self._client = None

    def _send_msg(self, email: str, content: str) -> None:
        try:
            self._client.create_mime(
                recipient_email_addr=email,
                sender_email_addr=self._SMTP_account,
                subject=self._subject or '',
                content_html=content,
                content_text=content
            )

            self._client.send_msg()
        
        except Exception as e:
            logger.error(f'It happened unexpected error during sending mail to {email}: {str(e)}')

        return None

    async def __call__(
        self,
        recipients: List[Dict]
    ) -> None:
        self._client = SMTP(
            SMTP_server=self._SMTP_server,
            SMTP_account=self._SMTP_account,
            SMTP_password=self._SMTP_password
        )

        for recipient in recipients:
            email = recipient.get('email')
            content = recipient.get('content')
            await to_thread(
                self._send_msg,
                email, 
                content
            )

        return None