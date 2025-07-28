# model/db.py
"""
This module provides database utilities for managing SQLAlchemy sessions and engine creation.

Classes:
    Base: A declarative base class for defining ORM models.

Functions:
    get_engine(db_uri="sqlite:///data.db"):
        Creates and returns a SQLAlchemy engine for the given database URI.

    get_session_factory(db_uri="sqlite:///data.db"):
        Creates and returns a SQLAlchemy session factory bound to the engine.

    get_session(session_factory):
        A context manager that provides a SQLAlchemy session, ensuring proper
        handling of commit, rollback, and close operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager
import os

# Use environment variable if provided, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data.db")

def get_engine(db_uri=DATABASE_URL):
    return create_engine(db_uri, echo=False)


def get_session_factory(db_uri=DATABASE_URL):
    """
    Creates and returns a SQLAlchemy session factory bound to the engine.

    Args:
        db_uri (str): The database URI to connect to. Defaults to DATABASE_URL.

    Returns:
        sessionmaker: A session factory for creating new sessions.
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine(db_uri), expire_on_commit=False)


# Base class for all models
Base = declarative_base()

@contextmanager
def get_session():
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# ✅ One-time schema creation (optional)
# Comment this out after first run in production
Base.metadata.create_all(get_engine())


