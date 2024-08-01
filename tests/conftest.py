import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from sqlalchemy.ext.declarative import declarative_base
from money_movement.models import (
    Base,
    FundingTransaction,
    InvestorAccount,
    FundAccount,
    WithdrawalTransaction,
    FundDepositTransaction,
)

# Create an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    return create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def tables(engine):
    # Create all tables in the test database
    Base.metadata.create_all(engine)
    yield
    # Drop all tables in the test database after the test session
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine, tables):
    """Creates a new database session for a test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    clear_mappers()
