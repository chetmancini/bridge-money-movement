from enum import Enum
from typing import Dict, List, Tuple
from moneyed import Money
from money_movement.util import generate_random_id

from money_movement.util import GenericStateMachine


class WithdrawalState(Enum):
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Withdrawal(GenericStateMachine[WithdrawalState]):
    """
    Represents a transaction of withdrawal of funds from an investment firm account.
    """

    def __init__(self, withdrawal_id: str, account_id: str, amount: Money):
        self.withdrawal_id = withdrawal_id
        self.account_id = account_id
        self.amount = amount
        super().__init__(
            initial_state=WithdrawalState.CREATED,
            transitions={
                WithdrawalState.CREATED: [
                    WithdrawalState.IN_PROGRESS,
                    WithdrawalState.FAILED,
                ],
                WithdrawalState.IN_PROGRESS: [
                    WithdrawalState.COMPLETED,
                    WithdrawalState.FAILED,
                ],
                WithdrawalState.COMPLETED: [],
                WithdrawalState.FAILED: [],
            },
        )

    def fail(self):
        self.transition(WithdrawalState.FAILED)

    def get_withdrawal_id(self) -> str:
        return self.withdrawal_id

    def get_state(self) -> WithdrawalState:
        return super().get_state()

    def get_amount(self) -> Money:
        return self.amount

    def get_account_id(self) -> str:
        return self.account_id


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
    def __init__(self, accounts: Dict[str, int] = {}):
        self.accounts = {}
        self.default_currency = "USD"
        for account_id, balance in accounts.items():
            self.accounts[account_id] = Money(balance, self.default_currency)
        self._transactions = {}

    def check_balance(self, account_id: str) -> Money:
        if account_id in self.accounts:
            return self.accounts[account_id]
        else:
            raise ValueError("Account not found")

    def withdraw_funds(self, account_id: str, amount: Money) -> Withdrawal:
        self.accounts[account_id] -= amount
        withdrawal_id = generate_random_id()
        withdrawal = Withdrawal(withdrawal_id, account_id, amount)
        self._transactions[withdrawal_id] = withdrawal
        return withdrawal

    def withdrawal_status(self, withdrawal_id: str, account_id: str) -> WithdrawalState:
        if withdrawal_id not in self._transactions:
            raise ValueError("Withdrawal not found")
        withdrawal = self._transactions[withdrawal_id]
        if withdrawal.get_account_id() != account_id:
            raise ValueError("Withdrawal does not match account")
        return withdrawal.get_state()

    def _complete_withdrawal(self, withdrawal_id: str):
        self._transactions[withdrawal_id].transition(WithdrawalState.COMPLETED)

    def _fail_withdrawal(self, withdrawal_id: str):
        self._transactions[withdrawal_id].transition(WithdrawalState.FAILED)
