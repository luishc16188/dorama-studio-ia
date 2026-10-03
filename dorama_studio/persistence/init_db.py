"""
Database initialization for DORAMA STUDIO IA V2.
Sets up SQLite database with all tables and provides session management.
"""

import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base

# Default database path
DEFAULT_DB_PATH = "dorama_studio.db"

_engine = None
_SessionFactory = None


def get_engine(db_path: str = None, echo: bool = False):
    """
    Get or create the SQLAlchemy engine.

    Args:
        db_path: Path to SQLite database file
        echo: Whether to echo SQL statements

    Returns:
        SQLAlchemy Engine
    """
    global _engine

    if _engine is None:
        db_path = db_path or DEFAULT_DB_PATH

        # Create SQLite engine with appropriate settings
        _engine = create_engine(
            f"sqlite:///{db_path}",
            echo=echo,
            poolclass=StaticPool,
            connect_args={
                "check_same_thread": False,  # Allow multi-threaded access
                "timeout": 30
            }
        )

        # Enable foreign key constraints for SQLite
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")  # Better concurrency
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-32768")  # 32MB cache
            cursor.close()

    return _engine


def get_session_factory(db_path: str = None) -> sessionmaker:
    """
    Get or create the session factory.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Session factory
    """
    global _SessionFactory

    if _SessionFactory is None:
        engine = get_engine(db_path)
        _SessionFactory = sessionmaker(
            bind=engine,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )

    return _SessionFactory


def init_db(db_path: str = None, echo: bool = False) -> None:
    """
    Initialize the database by creating all tables.

    Args:
        db_path: Path to SQLite database file
        echo: Whether to echo SQL statements
    """
    engine = get_engine(db_path, echo)
    Base.metadata.create_all(engine)
    print(f"Database initialized at: {db_path or DEFAULT_DB_PATH}")


def close_db() -> None:
    """Close database connections."""
    global _engine, _SessionFactory

    if _engine:
        _engine.dispose()
        _engine = None
    _SessionFactory = None


def get_session(db_path: str = None) -> Session:
    """
    Get a new database session.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLAlchemy Session
    """
    factory = get_session_factory(db_path)
    return factory()


@contextmanager
def session_scope(db_path: str = None):
    """
    Provide a transactional scope around a series of operations.

    Usage:
        with session_scope() as session:
            session.add(some_object)
            session.commit()

    Args:
        db_path: Path to SQLite database file

    Yields:
        SQLAlchemy Session
    """
    session = get_session(db_path)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def drop_all_tables(db_path: str = None) -> None:
    """
    Drop all tables (use with caution!).

    Args:
        db_path: Path to SQLite database file
    """
    engine = get_engine(db_path)
    Base.metadata.drop_all(engine)
    print("All tables dropped")


def get_db_info(db_path: str = None) -> dict:
    """
    Get database information.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Dictionary with database info
    """
    import sqlite3

    db_path = db_path or DEFAULT_DB_PATH

    if not os.path.exists(db_path):
        return {"exists": False, "path": db_path}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # Get row counts for each table
    table_counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        table_counts[table] = cursor.fetchone()[0]

    # Get database size
    size = os.path.getsize(db_path)

    conn.close()

    return {
        "exists": True,
        "path": db_path,
        "size_bytes": size,
        "size_mb": round(size / (1024 * 1024), 2),
        "tables": tables,
        "table_counts": table_counts
    }


# Convenience function for migrations
def run_migration(db_path: str = None, migration_name: str = None) -> None:
    """
    Run a database migration (placeholder for future migrations).

    Args:
        db_path: Path to SQLite database file
        migration_name: Name of migration to run
    """
    # This would integrate with Alembic or similar in production
    print(f"Migration '{migration_name}' not yet implemented")
    pass


if __name__ == "__main__":
    # Allow running as script for quick initialization
    import sys

    db_path = sys.argv[1] if len(sys.argv) > 1 else None

    if "drop" in sys.argv:
        drop_all_tables(db_path)
    else:
        init_db(db_path)
        info = get_db_info(db_path)
        print(f"Database info: {info}")
