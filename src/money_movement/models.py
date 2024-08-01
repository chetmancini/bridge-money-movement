from decimal import Decimal
from enum import Enum as PyEnum
from datetime import UTC, datetime
from moneyed import Money
from sqlalchemy import (
    DECIMAL,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
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
    __tablename__ = "investor_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_account_uid: Mapped[str] = mapped_column(nullable=True)

    funding_transactions = relationship(
        "FundingTransaction", back_populates="investor_account"
    )
    withdrawal_transactions = relationship(
        "WithdrawalTransaction", back_populates="investor_account"
    )


class WithdrawalTransaction(Base):
    __tablename__ = "withdrawal_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    investor_account_id: Mapped[int] = mapped_column(ForeignKey(InvestorAccount.id))
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    state: Mapped[PyEnum] = mapped_column(nullable=False)

    funding_transactions = relationship(
        "FundingTransaction", back_populates="withdrawal_transaction"
    )
    investor_account = relationship(
        "InvestorAccount", back_populates="withdrawal_transactions"
    )

    def amount_money(self) -> Money:
        return Money(self.amount, "USD")


class FundAccount(Base, TimestampMixin):
    """
    Represents an investment firm account that investors can deposit funds into.
    """

    __tablename__ = "fund_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_account_uid: Mapped[str] = mapped_column(nullable=True)
    min_investment_threshold: Mapped[int] = mapped_column(nullable=True)
    seat_availability: Mapped[int] = mapped_column(nullable=True)

    funding_transactions = relationship(
        "FundingTransaction", back_populates="fund_account"
    )
    deposit_transactions = relationship(
        "FundDepositTransaction", back_populates="fund_account"
    )


class FundDepositTransaction(Base, TimestampMixin, VersionedMixin):
    __tablename__ = "fund_deposit_transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    fund_account_id: Mapped[int] = mapped_column(ForeignKey(FundAccount.id))
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    state: Mapped[PyEnum] = mapped_column(nullable=False)

    funding_transactions = relationship(
        "FundingTransaction", back_populates="deposit_transaction"
    )
    fund_account = relationship("FundAccount", back_populates="deposit_transactions")


class TransactionState(PyEnum):
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
    __tablename__ = "funding_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    investor_account_id: Mapped[int] = mapped_column(
        ForeignKey(InvestorAccount.id), nullable=False
    )
    fund_account_id: Mapped[int] = mapped_column(
        ForeignKey(FundAccount.id), nullable=False
    )
    withdrawal_transaction_id: Mapped[int] = mapped_column(
        ForeignKey(WithdrawalTransaction.id), nullable=True
    )
    deposit_transaction_id: Mapped[int] = mapped_column(
        ForeignKey(FundDepositTransaction.id), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    state: Mapped[TransactionState] = mapped_column(
        default=TransactionState.INITIATED, nullable=False
    )

    investor_account = relationship(
        "InvestorAccount", back_populates="funding_transactions"
    )
    fund_account = relationship(
        "FundAccount",
        back_populates="funding_transactions",
    )
    withdrawal_transaction = relationship(
        "WithdrawalTransaction", back_populates="funding_transactions"
    )
    deposit_transaction = relationship(
        "FundDepositTransaction", back_populates="funding_transactions"
    )

    def amount_money(self) -> Money:
        return Money(self.amount, "USD")


engine = create_engine("sqlite:///money_movement.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
