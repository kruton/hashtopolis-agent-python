import pytest
from typing import Generator, Self
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.mysql import MySqlContainer


@pytest.fixture(scope="session")
def network() -> Generator[Network, None, None]:
    with Network() as network:
        yield network


@pytest.fixture(scope="session")
def database(network: Network) -> Generator[MySqlContainer, None, None]:
    with MySqlContainer("mysql:8.0").with_network(network) as db:
        yield db


class HashtopolisBackend(DockerContainer):
    """
    Hashtopolis backend container for testing. Must be on the same network as the database.
    """

    def __init__(
        self,
        image: str = "hashtopolis/backend:v0.14.4",
        *,
        network: Network,
        database: MySqlContainer,
    ) -> None:
        super().__init__(image)
        self.with_env("HASHTOPOLIS_DB_HOST", f"{database.get_wrapped_container().name}")
        self.with_env("HASHTOPOLIS_DB_USER", "test")
        self.with_env("HASHTOPOLIS_DB_PASS", "test")
        self.with_env("HASHTOPOLIS_DB_DATABASE", "test")
        self.with_network(network)
        self.with_exposed_ports(80)

    @property
    def url(self) -> str:
        return f"http://{self.get_container_host_ip()}:{self.get_exposed_port(80)}"

    def start(self) -> Self:
        super().start()
        wait_for_logs(self, "Hashtopolis is now ready")
        return self


@pytest.fixture(scope="session")
def backend(
    database: MySqlContainer, network: Network
) -> Generator[HashtopolisBackend, None, None]:
    with HashtopolisBackend(network=network, database=database) as backend:
        yield backend
