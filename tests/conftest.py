import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def activity_data(monkeypatch):
    data = {
        "Chess Club": {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["michael@example.com", "daniel@example.com"],
        },
        "Art Club": {
            "description": "Create art",
            "schedule": "Mondays",
            "max_participants": 15,
            "participants": [],
        },
        "Arts & Crafts": {
            "description": "Explore crafts",
            "schedule": "Tuesdays",
            "max_participants": 10,
            "participants": ["student+arts@example.com"],
        },
    }
    monkeypatch.setattr(app_module, "activities", data)
    return data


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client
