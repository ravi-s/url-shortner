# model/db.py
"""
This module sets up the database connection and session management for the URL shortener application.

Classes:
    Base: Declarative base class for defining ORM models.

Functions:
    get_session():
        Context manager that provides a database session. It ensures that the session is committed
        if no exceptions occur, or rolled back in case of an exception. The session is always closed
        after use.

Constants:
    DATABASE_URL (str): The URL for the SQLite database file.
    engine: SQLAlchemy engine instance for connecting to the database.
    SessionLocal: SQLAlchemy session factory for creating database sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# SQLite database file
DATABASE_URL = "sqlite:///shortener.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

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

