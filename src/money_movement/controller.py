from sqlalchemy import Transaction
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session

from money_movement.models import FundAccount, InvestorAccount


def process_transaction(investor_id, fund_id, amount):
    session = Session()
    try:
        investor = (
            session.query(InvestorAccount)
            .filter_by(id=investor_id)
            .with_for_update()
            .one()
        )
        fund = session.query(FundAccount).filter_by(id=fund_id).with_for_update().one()

        if investor.balance < amount:
            raise ValueError("Insufficient funds")

        if fund.seat_availability <= 0 or amount < fund.min_investment_threshold:
            raise ValueError("Fund criteria not met")

        original_investor_version = investor.version
        original_fund_version = fund.version

        investor.balance -= amount
        fund.balance += amount

        investor.version += 1
        fund.version += 1

        session.commit()
    except NoResultFound:
        session.rollback()
        return "failure", "Investor or Fund not found"
    except Exception as e:
        session.rollback()
        # Retry mechanism in case of concurrent updates
        if "could not serialize access due to concurrent update" in str(e):
            return "retry", "Transaction conflict detected, retrying..."
        return "failure", f"Transaction failed: {e}"


def transaction_status(transaction_id):
    session = Session()
    try:
        transaction = session.query(Transaction).filter_by(id=transaction_id).one()
        return transaction.state
    except Exception as e:
        print(f"Failed to fetch transaction status: {e}")
    finally:
        session.close()
        return None
