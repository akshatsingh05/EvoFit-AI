from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# SQLite needs check_same_thread=False for FastAPI's threaded request
# handling; pool_size/max_overflow are Postgres-only concepts (SQLite here
# uses SQLAlchemy's default SingletonThreadPool/NullPool instead).
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine_kwargs = {"pool_pre_ping": True}
if not is_sqlite:
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs)

if is_sqlite:
    # SQLite does not enforce foreign key constraints (or ON DELETE CASCADE)
    # unless explicitly told to per-connection. Without this, FK behavior
    # silently differs between local SQLite development and production
    # PostgreSQL (which enforces FKs by default) -- e.g. orphaned rows on
    # SQLite that a real FK constraint would have cascaded or rejected.
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
