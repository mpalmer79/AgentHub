import pytest

@pytest.mark.parametrize("path", [
    "/api",
    "/api/agents",
])
def test_api_routes_exist(client, path):
    response = client.get(path)
    assert response.status_code != 500
