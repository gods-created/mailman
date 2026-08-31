from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from .read_table import ReadTableService
from .send_mail import SendMailService
from .build_html_report import BuildHtmlReport

from typing import List, Any, Optional, Dict, Any
from os import remove, path

from validators import ReadFileSchema, SendMailSchema, ReportFromattingSchema, TemporaryFileSchema

from loguru import logger

@tool(
    'read_table',
    args_schema=ReadFileSchema,
    description='Read file and extract content for next using'
)
def read_table(
    path_to_file: str
) -> List[List[Any]]:
    logger.debug('Launched \'read_table\' tool')

    service = ReadTableService(path_to_file=path_to_file)
    return service()

@tool(
    'send_mail',
    args_schema=SendMailSchema,
    description='Sending mail to each recipient with prepared content for him'
)
async def send_mail(
    recipients: List[Dict],
    SMTP_server: str,
    SMTP_account: str,
    SMTP_password: str,
    subject: Optional[str] = None
) -> None:
    logger.debug('Launched \'send_mail\' tool')

    service = SendMailService(
        SMTP_server=SMTP_server,
        SMTP_account=SMTP_account,
        SMTP_password=SMTP_password,
        subject=subject
    )

    return await service(recipients)

@tool(
    'report_formatting',
    args_schema=ReportFromattingSchema,
    description='After the emails are sent, generate a report for the sender'
)
async def report_formatting(
    SMTP_server: str,
    SMTP_account: str,
    SMTP_password: str,
    report: List[Dict[str, Any]]
) -> None:
    logger.debug('Launched \'report_formatting\' tool')
    
    html_report = BuildHtmlReport()(report=report)

    service = SendMailService(
        SMTP_server=SMTP_server,
        SMTP_account=SMTP_account,
        SMTP_password=SMTP_password,
        subject='MailmanAI report: conclusion about your last task'
    )

    return await service([{'email': SMTP_account, 'content': html_report}])

@tool(
    'delete_temporary_file',
    args_schema=TemporaryFileSchema,
    description='After al tools before is completed, temporary file must to be remove'
)
async def delete_temporary_file(
    path_to_file: str
) -> None:
    logger.debug('Launched \'delete_temporary_file\' tool')

    if path.exists(path_to_file):
        remove(path_to_file)

TOOLS = [read_table, send_mail, report_formatting, delete_temporary_file]

class InitAgentService:
    def __init__(
        self,
        gemini_model_name: str,
        gemini_api_key: str,
        template: str
    ):
        self._gemini_model_name = gemini_model_name 
        self._gemini_api_key = gemini_api_key 
        self._template = template

    def __call__(self) -> CompiledStateGraph:
        model = ChatGoogleGenerativeAI(
            model=self._gemini_model_name,
            api_key=self._gemini_api_key,
            temperature=0.1
        )

        return create_agent(
            model=model,
            tools=TOOLS,
            system_prompt=SystemMessage(content=self._template)
        )