from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ReportFromattingSchema(BaseModel):
    SMTP_server: str = Field(description='The each mail will be sending through this server')
    SMTP_account: str = Field(description='Sender and owner of the SMTP account')
    SMTP_password: str = Field(description='The password of owner of the SMTP account')
    report: List[Dict[str, Any]] = Field(description='The report about last task, which will be sending to sender')