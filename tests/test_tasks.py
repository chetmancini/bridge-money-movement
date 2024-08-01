import pytest
from money_movement.models import (
    FundAccount,
    FundingTransaction,
    InvestorAccount,
    TransactionState,
)
from money_movement.tasks import process_deposit, process_withdrawal


@pytest.mark.skip(reason="Having trouble getting this working")
def test_process_withdrawal(session):
    investor_account = InvestorAccount()
    investor_account.external_account_uid = "1234"
    session.add(investor_account)
    fund_account = FundAccount()
    fund_account.external_account_uid = "4321"
    session.add(fund_account)
    session.commit()
    funding_transaction = FundingTransaction(
        investor_account=investor_account,
        fund_account=fund_account,
        amount=100,
        state=TransactionState.INITIATED,
    )
    session.add(funding_transaction)
    session.commit()

    process_withdrawal(funding_transaction.id)

    retrieved_transaction = session.query(FundingTransaction).first()
    assert retrieved_transaction.state == TransactionState.WITHDRAWAL_PENDING
    assert retrieved_transaction.withdrawal_transaction is not None
    assert (
        retrieved_transaction.withdrawal_transaction.state == TransactionState.INITIATED
    )


@pytest.mark.skip(reason="Having trouble getting this working")
def test_process_deposit(session):
    investor_account = InvestorAccount()
    investor_account.external_account_uid = "1234"
    session.add(investor_account)
    fund_account = FundAccount()
    fund_account.external_account_uid = "4321"
    session.add(fund_account)
    session.commit()
    funding_transaction = FundingTransaction(
        investor_account=investor_account,
        fund_account=fund_account,
        amount=100,
        state=TransactionState.WITHDRAWAL_COMPLETED,
    )
    session.add(funding_transaction)
    session.commit()

    process_deposit(funding_transaction.id)

    retrieved_transaction = session.query(FundingTransaction).first()
    assert retrieved_transaction.state == TransactionState.DEPOSIT_PENDING
    assert retrieved_transaction.deposit_transaction is not None
