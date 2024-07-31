from sqlalchemy import Transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session

from money_movement.models import (
    FundAccount,
    InvestorAccount,
    FundingTransaction,
    TransactionState,
)
from money_movement.tasks import process_withdrawal


def process_new_transaction(investor_id, fund_id, amount):
    session = Session()
    try:
        investor_account: InvestorAccount = (
            session.query(InvestorAccount).filter_by(id=investor_id).one()
        )
        fund_account: FundAccount = (
            session.query(FundAccount).filter_by(id=fund_id).one()
        )
        transaction = FundingTransaction(
            investor_account=investor_account,
            fund_account=fund_account,
            amount=amount,
            state=TransactionState.INITIATED,
        )
        session.add(transaction)
        session.commit()
        process_withdrawal.delay(transaction.id)
    finally:
        session.close()


def transaction_status(transaction_id) -> TransactionState:
    session = Session()
    try:
        transaction = (
            session.query(FundingTransaction).filter_by(id=transaction_id).one()
        )
        return transaction.get_state()
    except Exception as e:
        print(f"Failed to fetch transaction status: {e}")
    finally:
        session.close()
        return None
