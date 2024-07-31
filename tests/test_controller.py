import pytest
from money_movement.controller import process_transaction
from money_movement.models import Session, InvestorAccount, FundAccount, Base, engine


@pytest.fixture(scope="module")
def setup_database():
    # Set up the database
    Base.metadata.create_all(engine)
    session = Session()
    investor = InvestorAccount(id=1, balance=1000)
    fund = FundAccount(
        id=1, balance=0, min_investment_threshold=100, seat_availability=10
    )
    session.add(investor)
    session.add(fund)
    session.commit()
    yield session
    session.query(InvestorAccount).delete()
    session.query(FundAccount).delete()
    session.commit()
    session.close()


@pytest.mark.skip(reason="Test is not ready")
def test_transaction(setup_database):
    session = setup_database

    # Perform the transaction
    process_transaction(1, 1, 100)

    # Fetch the updated data
    investor = session.query(InvestorAccount).filter_by(id=1).one()
    fund = session.query(FundAccount).filter_by(id=1).one()

    # Assert the balances
    assert investor.balance == 900
    assert fund.balance == 100
