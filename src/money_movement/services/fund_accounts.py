from enum import Enum
import random
import string
from typing import Dict, List
from moneyed import Money

from money_movement.util import GenericStateMachine, generate_random_id


class DepositState(Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Deposit(GenericStateMachine[DepositState]):
    """
    Represents a transaction of deposit of funds into an investment firm account.
    """

    def __init__(self, deposit_id: str, account_id: str, amount: Money):
        self.deposit_id = deposit_id
        self.account_id = account_id
        self.amount = amount
        super().__init__(
            initial_state=DepositState.CREATED,
            transitions={
                DepositState.CREATED: [DepositState.IN_PROGRESS, DepositState.FAILED],
                DepositState.IN_PROGRESS: [DepositState.COMPLETED, DepositState.FAILED],
                DepositState.COMPLETED: [],
                DepositState.FAILED: [],
            },
        )

    def fail(self):
        self.transition(DepositState.FAILED)

    def get_account_id(self) -> str:
        return self.account_id

    def get_deposit_id(self) -> str:
        return self.deposit_id


class AbstractFundAccountsService:
    """
    Abstract class for a service that handles depositing funds into investment firm accounts.
    In production would wrap a third-party API or service with a standardized interface.
    In testing allows subclassing with MockFundAccountsService to simulate depositing funds.
    """

    def __init__(self):
        pass

    def deposit_funds(self, account_id: str, amount: Money) -> Deposit:
        pass

    def deposit_status(self, deposit_id: str) -> DepositState:
        pass


class MockFundAccountsService:
    """
    Mock implementation of a service that handles depositing funds into investment firm accounts.
    """

    def __init__(self, accounts: List[str] = []):
        self.accounts = accounts
        self.default_currency = "USD"
        self.deposits: Dict[str, Dict[str]] = {}
        for account_id in accounts:
            self.deposits[account_id] = {}

    def deposit_funds(self, account_id: str, amount: Money) -> str:
        deposit_id = generate_random_id()
        deposit = Deposit(deposit_id, account_id, amount)
        if account_id in self.deposits:
            self.deposits[account_id][deposit_id] = deposit
        return deposit

    def deposit_status(self, account_id: str, deposit_id: str) -> DepositState:
        if deposit_id in self.deposits[account_id]:
            return self.deposits[account_id][deposit_id].get_state()
        else:
            raise ValueError("Deposit not found")
