import pytest
from cianmon.model import create_tables
from cianmon.model import drop_tables


@pytest.fixture
def response_html():
    with open("./tests/data/response.html") as fl:
        return fl.read()


@pytest.yield_fixture(autouse=True)
def setup_database():
    create_tables()
    yield
    drop_tables()
