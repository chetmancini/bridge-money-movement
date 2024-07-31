from moneyed import Money
import pytest
from money_movement.services.investor_accounts import (
    MockInvestorAccountsService,
    WithdrawalState,
)


def test_check_balance():
    subject = MockInvestorAccountsService(accounts={"12345": 1000})
    assert subject.check_balance("12345") == Money(1000, "USD")


def test_check_balance_invalid():
    mock_investor_account_service = MockInvestorAccountsService(
        accounts={"12345": 1000}
    )
    with pytest.raises(ValueError):
        mock_investor_account_service.check_balance("54321")


def test_withdraw_funds():
    subject = MockInvestorAccountsService(accounts={"12345": 1000})
    subject.withdraw_funds("12345", Money(100, "USD"))
    assert subject.check_balance("12345") == Money(900, "USD")


def test_withdrawal_status():
    subject = MockInvestorAccountsService(accounts={"12345": 1000})
    withdrawal = subject.withdraw_funds("12345", Money(100, "USD"))
    assert WithdrawalState.IN_PROGRESS == subject.withdrawal_status(
        withdrawal_id=withdrawal.get_withdrawal_id(),
        account_id=withdrawal.get_account_id(),
    )


def test_withdrawal_status_invalid():
    subject = MockInvestorAccountsService(accounts={"12345": 1000})
    withdrawal = subject.withdraw_funds("12345", Money(100, "USD"))
    with pytest.raises(ValueError):
        subject.withdrawal_status(withdrawal_id="54321", account_id="12345")
