# model/db.py
"""
This module provides database utilities for managing SQLAlchemy sessions and engine creation.

Classes:
    Base: A declarative base class for defining ORM models.

Functions:
    get_engine(db_uri="sqlite:///shortener.db"):
        Creates and returns a SQLAlchemy engine for the given database URI.

    get_session_factory(db_uri="sqlite:///shortener.db"):
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

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False,
    bind=engine, expire_on_commit=False
)

# Base class for all models
Base = declarative_base()

@contextmanager
def get_session():
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
Base.metadata.create_all(engine)


