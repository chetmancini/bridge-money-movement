from abc import ABC, abstractmethod
from logging import Logger, getLogger
from money_movement.models import FundingTransaction

logger: Logger = getLogger(__name__)


class AbstractNotificationService(ABC):
    @abstractmethod
    def funds_transfered(self, funding_transaction: FundingTransaction):
        pass


class LoggingNotificationService(AbstractNotificationService):

    def __init__(self):
        pass

    def funds_transfered(self, funding_transaction: FundingTransaction):
        logger.log(
            f"Funds transfered: {funding_transaction.amount_money()} from"
            f"{funding_transaction.investor_account.external_account_uid} to"
            f"{funding_transaction.fund_account.external_account_uid}"
        )
