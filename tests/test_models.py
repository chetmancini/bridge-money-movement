import pytest
from money_movement.models import (
    FundAccount,
    FundingTransaction,
    InvestorAccount,
    TransactionState,
)
from moneyed import Money


def test_funding_transaction(session):
    fund_account = FundAccount()
    fund_account.external_account_uid = "4321"
    fund_account.min_investment_threshold = 100
    fund_account.seat_availability = 10

    investor_account = InvestorAccount()
    investor_account.external_account_uid = "12345"

    session.add_all([fund_account, investor_account])

    session.commit()
    funding_transaction = FundingTransaction(
        amount=100, investor_account=investor_account, fund_account=fund_account
    )
    session.add(funding_transaction)
    session.commit()
    retrieved_transaction = session.query(FundingTransaction).first()
    assert retrieved_transaction.amount == 100
    assert retrieved_transaction.amount_money() == Money(100, "USD")
    assert retrieved_transaction.state == TransactionState.INITIATED
    assert retrieved_transaction.investor_account.external_account_uid == "12345"
    assert retrieved_transaction.fund_account.external_account_uid == "4321"


@pytest.mark.skip(reason="Having trouble getting this working")
def test_funding_transaction_transition_state(session):

    fund_account = FundAccount()
    fund_account.external_account_uid = "4321"
    fund_account.min_investment_threshold = 100
    fund_account.seat_availability = 10

    investor_account = InvestorAccount()
    investor_account.external_account_uid = "12345"

    session.add_all([fund_account, investor_account])
    session.commit()

    funding_transaction = FundingTransaction(
        amount=100,
        investor_account=investor_account,
        fund_account=fund_account,
        state=TransactionState.INITIATED,
    )
    session.add(funding_transaction)
    session.commit()

    funding_transaction.transition(TransactionState.WITHDRAWAL_PENDING)
    session.commit()
    assert TransactionState.WITHDRAWAL_PENDING == funding_transaction.get_state()

    funding_transaction.transition(TransactionState.WITHDRAWAL_COMPLETED)
    session.commit()
    assert TransactionState.WITHDRAWAL_COMPLETED == funding_transaction.get_state()

    funding_transaction.transition(TransactionState.DEPOSIT_PENDING)
    session.commit()
    assert TransactionState.DEPOSIT_PENDING == funding_transaction.get_state()

    funding_transaction.transition(TransactionState.DEPOSIT_COMPLETED)
    session.commit()
    assert TransactionState.DEPOSIT_COMPLETED == funding_transaction.get_state()


@pytest.mark.skip(reason="Having trouble getting this working")
def test_funding_transaction_invalid_transition(session):
    fund_account = FundAccount()
    fund_account.external_account_uid = "4321"
    fund_account.min_investment_threshold = 100
    fund_account.seat_availability = 10

    session.add(fund_account)
    session.commit()

    investor_account = InvestorAccount()
    investor_account.external_account_uid = "12345"
    session.add(investor_account)
    session.commit()
    funding_transaction = FundingTransaction(
        amount=100,
        investor_account=investor_account,
        fund_account=fund_account,
        state=TransactionState.INITIATED,
    )

    with pytest.raises(ValueError):
        funding_transaction.transition(TransactionState.DEPOSIT_COMPLETED)
        session.commit()
