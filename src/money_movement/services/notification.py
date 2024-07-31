from abc import abstractmethod

from money_movement.models import FundingTransaction


class AbstractNotificationService(ABC):
    @abstractmethod
    def funds_transfered(self, funding_transaction: FundingTransaction):
        pass


class LoggingNotificationService(AbstractNotificationService):

    def __init__(self):
        pass

    def funds_transfered(self, funding_transaction: FundingTransaction):
        print(
            f"Funds transfered: {funding_transaction.amount_money()} from 
            {funding_transaction.investor_account.external_account_uid} to 
            {funding_transaction.fund_account.external_account_uid}")
        

