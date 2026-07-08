"""
Startup-time schema verification.

`main.py` no longer calls `Base.metadata.create_all()` -- schema is owned
entirely by Alembic (see DATABASE_MIGRATION_GUIDE.md). That means if an
operator starts the app against a database that was never migrated (a
pre-existing/legacy DB file, or any deploy path that skips
`alembic upgrade head`), every table the ORM expects to exist simply won't,
and requests will only fail lazily -- e.g. login/signup crash with a raw
"relation refresh_tokens does not exist" the first time anyone tries to
authenticate, long after the app appeared to start up "successfully".

This check runs once at startup and fails loudly and immediately instead,
so a missing/incomplete schema is caught in the deploy logs rather than
discovered by a confused user hitting 500s.

Two checks are performed, because either alone is insufficient:

1. `alembic_version` matches the latest local migration. Catches a
   never-migrated database outright.
2. Every table SQLAlchemy actually maps (`Base.metadata.tables`) physically
   exists in the database. Catches drift that check #1 alone misses -- most
   notably `alembic stamp head` (marks a DB as migrated *without* running
   the migration; commonly reached for by an operator "fixing" a DB that
   already had some tables from an older, pre-Alembic version of the app),
   but equally a restored backup from a different revision, a manually
   dropped/altered table, or a partially-applied migration that errored
   out partway through. Version-string equality says nothing about whether
   the tables the ORM expects are actually present.
"""
import logging
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.database.base import Base
import app.models  # noqa: F401  (registers every model on Base.metadata)

logger = logging.getLogger("evofit.startup")

_BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _latest_local_revision() -> str | None:
    alembic_cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    script = ScriptDirectory.from_config(alembic_cfg)
    return script.get_current_head()


def verify_database_schema(engine: Engine) -> None:
    expected_head = _latest_local_revision()
    if expected_head is None:
        # No migrations exist yet at all (shouldn't happen once the baseline
        # migration is committed) -- nothing to verify against.
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "alembic_version" not in table_names:
        raise RuntimeError(
            "Database has not been migrated: no 'alembic_version' table found. "
            "Run `alembic upgrade head` before starting the app "
            "(see DATABASE_MIGRATION_GUIDE.md)."
        )

    with engine.connect() as conn:
        current = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()

    if current != expected_head:
        raise RuntimeError(
            f"Database schema is out of date (at revision {current!r}, "
            f"expected {expected_head!r}). Run `alembic upgrade head` before "
            "starting the app (see DATABASE_MIGRATION_GUIDE.md)."
        )

    # `alembic_version` says we're current -- now actually verify the tables
    # the ORM depends on are physically present, rather than trusting that
    # marker alone (see module docstring for why this matters).
    expected_tables = set(Base.metadata.tables.keys())
    missing_tables = expected_tables - table_names
    if missing_tables:
        raise RuntimeError(
            "Database is marked as migrated (alembic_version="
            f"{current!r}) but is missing expected table(s): "
            f"{', '.join(sorted(missing_tables))}. This usually means "
            "`alembic stamp` was used instead of `alembic upgrade`, or a "
            "migration failed partway through. Restore from a known-good "
            "backup or drop and re-run `alembic upgrade head` from scratch "
            "(see DATABASE_MIGRATION_GUIDE.md)."
        )

    logger.info("Database schema verified at revision %s (%d tables present)", current, len(expected_tables))
