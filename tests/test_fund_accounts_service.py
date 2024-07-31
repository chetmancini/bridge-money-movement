from moneyed import Money
import pytest
from money_movement.services.fund_accounts import DepositState, MockFundAccountsService


def test_deposit_funds():
    subject = MockFundAccountsService(accounts={"12345": 1000})
    subject.deposit_funds("12345", Money(100, "USD"))


def test_deposit_status():
    subject = MockFundAccountsService(accounts={"12345": 1000})
    deposit = subject.deposit_funds("12345", Money(100, "USD"))
    assert DepositState.CREATED == subject.deposit_status(
        deposit_id=deposit.get_deposit_id(), account_id=deposit.get_account_id()
    )


def test_withdrawal_status_invalid():
    subject = MockFundAccountsService(accounts={"12345": 1000})
    deposit = subject.deposit_funds("12345", Money(100, "USD"))
    with pytest.raises(ValueError):
        subject.deposit_status(deposit_id="54321", account_id="12345")
