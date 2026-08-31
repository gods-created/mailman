from pydantic import BaseModel, Field 
from typing import List, Optional, Dict

class SendMailSchema(BaseModel):
    recipients: List[Dict] = Field(description='A list with dictionaries with keys: email, ' \
                            'content (info about each recipient)')
    SMTP_server: str = Field(description='The each mail will be sending through this server')
    SMTP_account: str = Field(description='Sender and owner of the SMTP account')
    SMTP_password: str = Field(description='The password of owner of the SMTP account')
    subject: Optional[str] = Field(description='Mail subject (can to be None)', default=None)