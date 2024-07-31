
from typing import List, Tuple
from moneyed import Money

from money_movement.util import GenericStateMachine

class WithdrawalState(Enum):
    CREATED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    FAILED = 4


class Withdrawal(GenericStateMachine[WithdrawalState]):
    """
    Represents a transaction of withdrawal of funds from an investment firm account.
    """
    def __init__(self, account_id: str, amount: Money):
        self.account_id = account_id
        self.amount = amount
        self.state = WithdrawalState.CREATED
        self.transitions = {
            WithdrawalState.CREATED: [WithdrawalState.IN_PROGRESS, WithdrawalState.FAILED],
            WithdrawalState.IN_PROGRESS: [WithdrawalState.COMPLETED, WithdrawalState.FAILED],
            WithdrawalState.COMPLETED: [],
            WithdrawalState.FAILED: []
        }
    
    def fail(self):
        self.transition(WithdrawalState.FAILED)

    
class AbstractInvestorAccountsService:
    def __init__(self):
        pass

    def check_balance(self, account_id: str) -> Money:
        pass

    def withdraw_funds(self, account_id: str, amount: Money) -> Withdrawal:
        pass

    def withdrawal_status(self, withdrawal_id: str) -> WithdrawalState:
        pass



class MockInvestorAccountsService:
    def __init__(self, accounts: List[Tuple[str, float]] = []):
        self.accounts = {}
        self.default_currency = 'USD'
        for account_id, balance in accounts:
            self.accounts[account_id] = Money(balance, self.default_currency)

    def check_balance(self, account_id: str) -> Money: 
        return self.accounts[account_id]

    def withdraw_funds(self, account_id: str, amount: Money):
        self.accounts[account_id] -= amount
        