from pydantic import BaseModel, Field, field_validator
from email_validator import validate_email, EmailNotValidError

from typing import Optional

class ExecuteSchema(BaseModel):
    SMTP_server: str = Field()
    SMTP_account: str = Field()
    SMTP_password: str = Field()
    subject: Optional[str] = Field(default=None)
    mail: str

    @field_validator('SMTP_account')
    @classmethod
    def validate_SMTP_account(cls, value: str) -> str:
        try:
            validate_email(value)

        except EmailNotValidError:
            raise ValueError(f'The email is not valid (\'{value}\')')

        return value

    @field_validator('SMTP_password')
    @classmethod
    def validate_SMTP_password(cls, value: str) -> str:
        if not len(value) >= 12:
            raise ValueError('The SMTP password must have no less than 12 characters')

        return value