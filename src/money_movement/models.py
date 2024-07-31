from datetime import datetime
from moneyed import Money
from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, Float, String, create_engine
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class TimestampMixin:
    created = Column(Integer)
    modified = Column(Integer)

    def created_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.created)
    
    def modified_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.modified)

class VersionedMixin:
    version = Column(Integer, default=1)


class InvestorAccount(Base):
    __tablename__ = 'investor_accounts'
    id = Column(Integer, primary_key=True)
    account_id = Column(String)

class WithdrawalTransaction(Base):
    __tablename__ = 'withdrawal_transactions'
    id = Column(Integer, primary_key=True)
    investor_account_id: Mapped[int] = mapped_column(ForeignKey(InvestorAccount.id))
    amount = Column(DECIMAL)
    state = Column(String)

    def amount_money(self):
        return Money(self.amount, 'USD')


class FundAccount(Base):
    __tablename__ = 'fund_accounts'
    id = Column(Integer, primary_key=True)
    min_investment_threshold = Column(Integer)
    seat_availability = Column(Integer)
    version = Column(Integer, default=1)

class FundDepositTransaction(Base, TimestampMixin, VersionedMixin):
    __tablename__ = 'fund_deposit_transactions'
    id = Column(Integer, primary_key=True)
    fund_account_id = Column(Integer)
    amount = Column(DECIMAL)
    state = Column(String)


class FundingTransaction(Base, TimestampMixin, VersionedMixin):
    __tablename__ = 'funding_transactions'
    id = Column(Integer, primary_key=True)
    investor_account_id = Column(Integer)
    fund_account_id = Column(Integer)
    amount = Column(DECIMAL)
    state = Column(String)

    def amount_money(self):
        return Money(self.amount, 'USD')


engine = create_engine('sqlite:///accounts.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
