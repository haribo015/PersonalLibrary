from app.db import session as session_module


class FakeSessionContext:
    def __init__(self, session) -> None:
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


async def test_get_db_yields_session_from_factory(monkeypatch) -> None:
    sentinel = object()
    monkeypatch.setattr(session_module, "AsyncSessionLocal", lambda: FakeSessionContext(sentinel))

    generator = session_module.get_db()
    session = await anext(generator)

    assert session is sentinel

    try:
        await anext(generator)
    except StopAsyncIteration:
        pass
