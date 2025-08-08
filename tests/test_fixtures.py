import requests

from tests.conftest import HashtopolisBackend


def test_backend_is_up(backend: HashtopolisBackend) -> None:
    resp = requests.get(f"{backend.url}/api/server.php?action=testConnection")
    assert resp.status_code == 200
