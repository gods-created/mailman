from serializers import AccountSerializer
from models import Account

from typing import List
from datetime import datetime, timedelta

from loguru import logger

def delete_old_accounts(
    serializer: AccountSerializer,
    accounts: List[Account]
) -> List[Account]:
    if not accounts:
        return []
    
    now_time = datetime.now()

    delete_accounts = []
    for index, account in enumerate(accounts):
        created_at = account.created_at
        if now_time - timedelta(minutes=15) > created_at:
            delete_accounts.append(account)
            del accounts[index]

    try:
        res = serializer.delete(accounts=delete_accounts)
        if not res['status']:
            raise Exception(res['err_description'])

    except Exception as e:
        logger.error(f'Error during job with \'delete_old_accounts\' signal: {str(e)}')

    return accounts