# model/__init__.py
"""
This module initializes the database for the URL shortener application.

It imports the database base class (`Base`) and engine from the `db` module,
as well as the `URLMap` model from the `models` module. The `init_db` function
is responsible for creating all the necessary tables in the database by binding
the metadata to the engine.

Functions:
    init_db(): Creates all tables defined in the database models.
"""

from .db import Base, engine
from .models import URLMap  # Import all models here

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
