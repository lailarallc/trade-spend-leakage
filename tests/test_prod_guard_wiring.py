"""The prod guard sits in front of the Postgres read path.

pipeline.db.source_conn() is used by every move script and by the live tests,
which run whenever DATABASE_URL is set. .env points it at localhost, which is a
`fly proxy` tunnel to production when one is open. This test fakes a flyctl
listener and asserts nothing connects.
"""

import pytest

from pipeline import db, prod_guard


def test_source_conn_refuses_fly_tunnel(monkeypatch):
    seen = []
    monkeypatch.delenv("ALLOW_PROD_DB", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost:5434/db")
    monkeypatch.setattr(prod_guard, "_listener", lambda port: seen.append(port) or "flyctl")
    monkeypatch.setattr(db.psycopg2, "connect", lambda *a, **kw: pytest.fail("connected"))
    with pytest.raises(prod_guard.ProdDatabaseError):
        with db.source_conn():
            pass
    assert seen == [5434]
