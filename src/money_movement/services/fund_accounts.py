
    
import random
import string
from typing import Dict, List
import moneyed

from bridge_money_movement.util import GenericStateMachine


class DepositState(Enum):
    INITIATED = 1
    COMPLETED = 2
    FAILED = 3


class Deposit(GenericStateMachine[DepositState]):
    def __init__(self, account_id: str, amount: moneyed.Money):
        self.account_id = account_id
        self.amount = amount
        self.state = DepositState.INITIATED
        self.transitions = {
            DepositState.INITIATED: [DepositState.COMPLETED, DepositState.FAILED],
            DepositState.COMPLETED: [],
            DepositState.FAILED: []
        }

class AbstractFundAccountsService:
    def __init__(self):
        pass

    def deposit_funds(self, account_id: str, amount: moneyed) -> Deposit:
        pass

    def deposit_status(self, withdrawal_id: str) -> DepositState:
        pass

class MockFundAccountsService:
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
