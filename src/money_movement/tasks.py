# tasks.py
from celery import Celery
from money_movement.models import (
    FundingTransaction,
    TransactionState,
)
from money_movement.services.fund_accounts import (
    AbstractFundAccountsService,
    MockFundAccountsService,
)
from money_movement.services.investor_accounts import (
    AbstractInvestorAccountsService,
    MockInvestorAccountsService,
    WithdrawalState,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from moneyed import Money

from money_movement.services.notification import (
    AbstractNotificationService,
    LoggingNotificationService,
)

app = Celery("tasks", broker="pyamqp://guest@localhost//")
# coreate a new sqlalchemy session

engine = create_engine("sqlite:///money_movement.db")
Session = sessionmaker(bind=engine)

investor_account_service: AbstractInvestorAccountsService = (
    MockInvestorAccountsService()
)

fund_account_service: AbstractFundAccountsService = MockFundAccountsService()

notification_service: AbstractNotificationService = LoggingNotificationService()


@app.task
def process_withdrawal(transaction_id):
    session = Session()
    transaction: FundingTransaction = (
        session.query(FundingTransaction).filter_by(id=transaction_id).one()
    )
    try:

        # Implement withdrawal logic here
        # Simulate long-running task with sleep
        import time

        time.sleep(10)

        # Balance check
        balance: Money = investor_account_service.check_balance(
            transaction.investor_account.external_account_uid
        )
        if balance < transaction.amount_money():
            transaction.transition(TransactionState.FAILED)
            session.commit()
            raise ValueError("Insufficient funds")

        # Withdraw funds
        withdrawal = investor_account_service.withdraw_funds(
            account_id=transaction.investor_account.external_account_uid,
            amount=transaction.amount_money(),
        )
        if withdrawal is None or withdrawal.state == WithdrawalState.FAILED:
            transaction.transition(TransactionState.FAILED)
            session.commit()
            raise ValueError("Withdrawal failed")
        if withdrawal.state == WithdrawalState.IN_PROGRESS:
            transaction.transition(TransactionState.WITHDRAWAL_PENDING)
            session.commit()

        # Queue the deposit task
        complete_withdrawal.delay(transaction_id, withdrawal.get_withdrawal_id())
    except Exception as e:
        transaction.transition(TransactionState.FAILED)
        session.commit()
        raise e
    finally:
        session.close()


@app.task
def complete_withdrawal(transaction_id, withdrawal_id: str = None):
    session = Session()
    transaction: FundingTransaction = (
        session.query(FundingTransaction).filter_by(id=transaction_id).one()
    )
    try:
        # Implement withdrawal logic here
        # Simulate long-running task with sleep
        import time

        time.sleep(10)

        # Fake withdrawal completion
        investor_account_service._complete_withdrawal(withdrawal_id=withdrawal_id)

        state: WithdrawalState = investor_account_service.withdrawal_status(
            withdrawal_id=withdrawal_id
        )

        if state == WithdrawalState.COMPLETED:
            transaction.transition(TransactionState.WITHDRAWAL_COMPLETED)
            session.commit()
        else:
            transaction.transition(TransactionState.FAILED)
            session.commit()
            raise ValueError("Withdrawal failed")

        # Queue the deposit task
        process_deposit.delay(transaction_id)

    except Exception as e:
        transaction.transition(TransactionState.FAILED)
        session.commit()
        raise e
    finally:
        session.close()


@app.task
def process_deposit(transaction_id):
    session = Session()
    transaction: FundingTransaction = (
        session.query(FundingTransaction).filter_by(id=transaction_id).one()
    )

    try:
        # Implement deposit logic here
        # Simulate long-running task with sleep
        import time

        time.sleep(10)

        # Update transaction state
        transaction.state = TransactionState.DEPOSIT_COMPLETED
        session.commit()
    except Exception as e:
        transaction.transition(TransactionState.FAILED)
        session.commit()
        raise e
    finally:
        session.close()


@app.task
def complete_deposit(transaction_id):
    session = Session()
    transaction: FundingTransaction = (
        session.query(FundingTransaction).filter_by(id=transaction_id).one()
    )

    try:
        # Implement deposit logic here
        # Simulate long-running task with sleep
        import time

        time.sleep(10)

        # Update transaction state
        transaction.transition(TransactionState.DEPOSIT_COMPLETED)
        session.commit()
        notification_service.funds_transfered(transaction)
    except Exception as e:
        transaction.transition(TransactionState.FAILED)
        session.commit()
        raise e
    finally:
        session.close()
