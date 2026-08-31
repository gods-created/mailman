from sqlalchemy import select as select_query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import Account

from typing import Optional, List

class AccountSerializer:
    def __init__(self, db_connection: Session):
        self._db_connection = db_connection

    def select(
        self,
        smtp_account: Optional[str] = None
    ) -> dict:
        response = {
            'status': False,
            'err_description': None,
            'data': {
                'accounts': []
            }
        }

        try:
            stmt = select_query(Account)

            if smtp_account is not None:
                stmt = stmt.filter_by()

            for acc in self._db_connection.scalars(stmt):
                response['data']['accounts'].append(acc)

            response['status'] = True

        except SQLAlchemyError as e:
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            response['err_description'] = f'Unexpected error: {str(e)}'

        return response

    def insert(
        self,
        smtp_server: str,
        smtp_account: str,
        smtp_password: str
    ) -> dict:
        response = {
            'status': False,
            'err_description': None,
            'data': {}
        }

        try:
            acc = Account(smtp_account=smtp_account, smtp_server=smtp_server, smtp_password=smtp_password)
            self._db_connection.add(acc)
            self._db_connection.commit()
            self._db_connection.refresh(acc)

            response['data']['account'] = acc
            response['status'] = True

        except SQLAlchemyError as e:
            self._db_connection.rollback()
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            self._db_connection.rollback()
            response['err_description'] = f'Unexpected error: {str(e)}'

        return response

    def delete(self, accounts: List[Account]) -> dict:
        response = {
            'status': False,
            'err_description': None
        }

        try:
            for acc in accounts:
                self._db_connection.delete(acc)

            self._db_connection.commit()

            response['status'] = True

        except SQLAlchemyError as e:
            self._db_connection.rollback()
            response['err_description'] = f'Unexpected SQLAlchemy error: {str(e)}'

        except Exception as e:
            self._db_connection.rollback()
            response['err_description'] = f'Unexpected error: {str(e)}'

        return response
