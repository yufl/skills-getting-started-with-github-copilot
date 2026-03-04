import copy

def pytest_configure(config):
    # ensure src is on the path; pytest.ini already sets pythonpath=. but import may need explicit reference
    pass


import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(scope="session")
def client():
    """TestClient instance for the FastAPI app."""
    return TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dictionary before each test."""
    # make a deep copy of the original state
    original = copy.deepcopy(app_module.activities)
    yield
    # restore after test completes (in case test mutated during yield)
    app_module.activities.clear()
    app_module.activities.update(original)
