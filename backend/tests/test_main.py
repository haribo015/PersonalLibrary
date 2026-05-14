import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app.main import app, root, startup_event


def test_root_endpoint() -> None:
    assert root() == {"message": "Personal Library API is ready"}


def test_cors_preflight_is_allowed_for_register_endpoint() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/v1/auth/register",
        headers={
            "Origin": "http://localhost:9000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:9000"


class FakeConnection:
    def __init__(self) -> None:
        self.run_sync_calls = []
        self.executed_statements = []

    async def run_sync(self, callback) -> None:
        self.run_sync_calls.append(callback)

    async def execute(self, statement) -> None:
        self.executed_statements.append(str(statement))


class FakeBeginContext:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    async def __aenter__(self) -> FakeConnection:
        return self.connection

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class FakeEngine:
    def __init__(self, connection: FakeConnection) -> None:
        self.connection = connection

    def begin(self) -> FakeBeginContext:
        return FakeBeginContext(self.connection)


@pytest.mark.asyncio
async def test_startup_event_creates_tables_and_applies_schema_updates(monkeypatch) -> None:
    connection = FakeConnection()
    monkeypatch.setattr(main_module.session, "engine", FakeEngine(connection))

    await startup_event()

    assert connection.run_sync_calls == [main_module.models.Base.metadata.create_all]
    assert len(connection.executed_statements) == 14
    assert any("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS category" in stmt for stmt in connection.executed_statements)
    assert any("ALTER TABLE users ADD COLUMN IF NOT EXISTS reading_goal" in stmt for stmt in connection.executed_statements)
