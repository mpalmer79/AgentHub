"""
Tests for the agents API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.agents.registry import AgentType, AGENT_REGISTRY


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


class TestAgentCatalog:

    def test_catalog_returns_all_agents(self, client):
        response = client.get("/api/agents/catalog")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == len(AGENT_REGISTRY)

    def test_catalog_agent_has_required_fields(self, client):
        response = client.get("/api/agents/catalog")
        data = response.json()

        for agent in data["agents"]:
            assert "type" in agent
            assert "name" in agent
            assert "description" in agent
            assert "price_monthly" in agent
            assert "features" in agent
            assert "integrations" in agent
            assert "category" in agent

    def test_catalog_includes_bookkeeper(self, client):
        response = client.get("/api/agents/catalog")
        data = response.json()
        agent_types = [a["type"] for a in data["agents"]]
        assert "bookkeeper" in agent_types

    def test_catalog_no_auth_required(self, client):
        response = client.get("/api/agents/catalog")
        assert response.status_code == 200


class TestAgentSubscriptions:

    def test_subscriptions_requires_auth(self, client):
        response = client.get("/api/agents/subscriptions")
        assert response.status_code == 401

    def test_subscribe_requires_auth(self, client):
        response = client.post("/api/agents/subscribe", json={"agent_type": "bookkeeper"})
        assert response.status_code == 401

    def test_run_requires_auth(self, client):
        response = client.post("/api/agents/run", json={"agent_type": "bookkeeper", "task": "test"})
        assert response.status_code == 401


class TestAgentTypes:

    def test_all_agent_types_in_registry(self):
        for agent_type in AgentType:
            assert agent_type in AGENT_REGISTRY

    def test_registry_has_required_fields(self):
        required_fields = ["name", "description", "price_monthly", "features", "integrations", "category"]
        for _, info in AGENT_REGISTRY.items():
            for field in required_fields:
                assert field in info

    def test_prices_are_positive(self):
        for _, info in AGENT_REGISTRY.items():
            assert info["price_monthly"] >= 0

    def test_features_is_list(self):
        for _, info in AGENT_REGISTRY.items():
            assert isinstance(info["features"], list)

    def test_integrations_is_list(self):
        for _, info in AGENT_REGISTRY.items():
            assert isinstance(info["integrations"], list)
