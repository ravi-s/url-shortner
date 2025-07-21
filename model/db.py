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

Base = declarative_base()

def get_engine(db_uri="sqlite:///data.db"):
    return create_engine(db_uri, echo=False)

def get_session_factory(db_uri="sqlite:///data.db"):
    engine = get_engine(db_uri)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

@contextmanager
def get_session(session_factory):
    session = session_factory()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


