
    
import random
import string
from typing import Dict, List
import moneyed

from money_movement.util import GenericStateMachine


class DepositState(Enum):
    CREATED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    FAILED = 4


class Deposit(GenericStateMachine[DepositState]):
    """
    Represents a transaction of deposit of funds into an investment firm account.
    """
    def __init__(self, account_id: str, amount: moneyed.Money):
        self.account_id = account_id
        self.amount = amount
        self.state = DepositState.CREATED
        self.transitions = {
            DepositState.CREATED: [DepositState.IN_PROGRESS, DepositState.FAILED],
            DepositState.IN_PROGRESS: [DepositState.COMPLETED, DepositState.FAILED],
            DepositState.COMPLETED: [],
            DepositState.FAILED: []
        }
    
    def fail(self):
        self.transition(DepositState.FAILED)

class AbstractFundAccountsService:
    """
    Abstract class for a service that handles depositing funds into investment firm accounts.
    In production would wrap a third-party API or service with a standardized interface.
    In testing allows subclassing with MockFundAccountsService to simulate depositing funds.
    """
    
    def __init__(self):
        pass

    def deposit_funds(self, account_id: str, amount: moneyed) -> Deposit:
        pass

    def deposit_status(self, withdrawal_id: str) -> DepositState:
        pass

class MockFundAccountsService:
    """
    Mock implementation of a service that handles depositing funds into investment firm accounts.
    """
    def __init__(self, accounts: List[str] = []):
        self.accounts = accounts 
        self.default_currency = 'USD'
        self.deposits: Dict[str, Dict[str]] = {}
        for account_id in accounts:
            self.deposits[account_id] = []

    def deposit_funds(self, account_id: str, amount: moneyed.Money) -> str:
        deposit_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        if account_id in self.deposits:
            self.deposits[account_id][deposit_id] = DepositState.INITIATED 

    def deposit_status(self, account_id: str, deposit_id: str) -> DepositState:
        if deposit_id in self.deposits[account_id]:
            return DepositState.COMPLETED
        else:
            raise ValueError("Deposit not found")
