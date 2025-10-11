import os
from importlib import reload

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path_factory: pytest.TempPathFactory) -> TestClient:
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"

    from app.core import config

    config.get_settings.cache_clear()  # type: ignore[attr-defined]

    from app import main
    from app.db import session as db_session

    reload(db_session)
    reload(main)

    app = main.app
    with TestClient(app) as test_client:
        yield test_client

    if db_file.exists():
        db_file.unlink()
