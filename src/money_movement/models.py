from decimal import Decimal
from enum import Enum as PyEnum
from datetime import UTC, datetime
from typing import List
from moneyed import Money
from sqlalchemy import (
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from money_movement.state_machine import GenericStateMachine

Base = declarative_base()


class TimestampMixin:
    created: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    modified: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)


class VersionedMixin:
    version: Mapped[int] = mapped_column(nullable=False, default=1)


class InvestorAccount(Base, TimestampMixin):
    __tablename__ = "investor_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_account_uid: Mapped[str] = mapped_column(nullable=True)

    funding_transactions = relationship(
        "FundingTransaction", back_populates="investor_account"
    )
    withdrawal_transactions = relationship(
        "WithdrawalTransaction", back_populates="investor_account"
    )


class SingleTransferState(PyEnum):
    """
    Represents the state of a single transfer transaction."""

    INITIATED = "INITIATED"
    TRANSFER_PENDING = "PENDING"
    TRANSFER_COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SingleTransactionSM(GenericStateMachine[SingleTransferState]):
    transitions = {
        SingleTransferState.INITIATED: [
            SingleTransferState.TRANSFER_PENDING,
            SingleTransferState.FAILED,
        ],
        SingleTransferState.TRANSFER_PENDING: [
            SingleTransferState.TRANSFER_COMPLETED,
            SingleTransferState.FAILED,
        ],
        SingleTransferState.TRANSFER_COMPLETED: [],
        SingleTransferState.FAILED: [],
    }

    state: Mapped[SingleTransferState] = mapped_column(
        nullable=False, default=SingleTransferState.INITIATED
    )


class WithdrawalTransaction(Base, TimestampMixin, VersionedMixin, SingleTransactionSM):
    __tablename__ = "withdrawal_transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    investor_account_id: Mapped[int] = mapped_column(ForeignKey("investor_account.id"))
    investor_account: Mapped[InvestorAccount] = relationship(
        back_populates="withdrawal_transactions"
    )
    funding_transactions: Mapped[List["FundingTransaction"]] = relationship(
        back_populates="withdrawal_transaction"
    )

    amount: Mapped[Decimal] = mapped_column(nullable=False)

    def amount_money(self) -> Money:
        return Money(self.amount, "USD")


class FundAccount(Base, TimestampMixin):
    """
    Represents an investment firm account that investors can deposit funds into.
    """

    __tablename__ = "fund_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_account_uid: Mapped[str] = mapped_column(nullable=True)
    min_investment_threshold: Mapped[int] = mapped_column(nullable=True)
    seat_availability: Mapped[int] = mapped_column(nullable=True)

    funding_transactions: Mapped[List["FundingTransaction"]] = relationship(
        "FundingTransaction", back_populates="fund_account"
    )
    deposit_transactions: Mapped[List["FundDepositTransaction"]] = relationship(
        back_populates="fund_account"
    )


class FundDepositTransaction(Base, TimestampMixin, VersionedMixin, SingleTransactionSM):
    __tablename__ = "deposit_transaction"
    id: Mapped[int] = mapped_column(primary_key=True)
    fund_account_id: Mapped[int] = mapped_column(ForeignKey("fund_account.id"))
    fund_account: Mapped[FundAccount] = relationship(
        back_populates="deposit_transactions"
    )
    amount: Mapped[Decimal] = mapped_column(nullable=False)

    funding_transactions: Mapped[List["FundingTransaction"]] = relationship(
        back_populates="deposit_transaction"
    )


class TransactionState(PyEnum):
    """
    Represents the state of a funding transaction from an investor to a fund account.
    """

    INITIATED = "Initiated"
    WITHDRAWAL_PENDING = "Withdrawal Pending"
    WITHDRAWAL_COMPLETED = "Withdrawal Completed"
    DEPOSIT_PENDING = "Deposit Pending"
    DEPOSIT_COMPLETED = "Deposit Completed"
    FAILED = "Failed"


class TransactionSM(GenericStateMachine[TransactionState]):
    transitions = {
        TransactionState.INITIATED: [
            TransactionState.WITHDRAWAL_PENDING,
            TransactionState.FAILED,
        ],
        TransactionState.WITHDRAWAL_PENDING: [
            TransactionState.WITHDRAWAL_COMPLETED,
            TransactionState.FAILED,
        ],
        TransactionState.WITHDRAWAL_COMPLETED: [
            TransactionState.DEPOSIT_PENDING,
            TransactionState.FAILED,
        ],
        TransactionState.DEPOSIT_PENDING: [
            TransactionState.DEPOSIT_COMPLETED,
            TransactionState.FAILED,
        ],
        TransactionState.DEPOSIT_COMPLETED: [],
        TransactionState.FAILED: [],
    }


class FundingTransaction(Base, TimestampMixin, VersionedMixin, TransactionSM):
    __tablename__ = "funding_transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    investor_account_id: Mapped[int] = mapped_column(
        ForeignKey("investor_account.id"), nullable=False
    )
    investor_account: Mapped[InvestorAccount] = relationship(
        back_populates="funding_transactions"
    )
    fund_account_id: Mapped[int] = mapped_column(
        ForeignKey("fund_account.id"), nullable=False
    )
    fund_account: Mapped[FundAccount] = relationship(
        back_populates="funding_transactions"
    )
    withdrawal_transaction_id: Mapped[int] = mapped_column(
        ForeignKey("withdrawal_transaction.id"), nullable=True
    )
    withdrawal_transaction: Mapped[WithdrawalTransaction] = relationship(
        back_populates="funding_transactions"
    )
    deposit_transaction_id: Mapped[int] = mapped_column(
        ForeignKey("deposit_transaction.id"), nullable=True
    )
    deposit_transaction: Mapped[FundDepositTransaction] = relationship(
        back_populates="funding_transactions"
    )
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    state: Mapped[TransactionState] = mapped_column(
        default=TransactionState.INITIATED, nullable=False
    )

    def amount_money(self) -> Money:
        return Money(self.amount, "USD")


engine = create_engine("sqlite:///money_movement.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
