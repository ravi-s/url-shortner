# model/models.py
"""
This module defines the SQLAlchemy ORM model for the URL mapping table.

Classes:
    URLMap: Represents a mapping between a short code and a long URL.

    Attributes:
        id (int): Primary key for the URL mapping.
        short_code (str): Unique short code for the URL.
        long_url (str): The original long URL.
        created_at (int): Timestamp indicating when the mapping was created.
        expires_at (int, optional): Timestamp indicating when the mapping expires.

    Methods:
        __repr__: Returns a string representation of the URLMap instance.
"""

# model/url_map.py
from sqlalchemy import Column, Integer, String, BigInteger
from model.db import Base  # ✅ Import the shared Base

class URLMap(Base):
    __tablename__ = 'url_map'

    id = Column(Integer, primary_key=True)
    short_code = Column(String(10), unique=True, nullable=False)
    long_url = Column(String, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    expires_at = Column(BigInteger, nullable=True)

    def __repr__(self):
        return f"<URLMap(short_code='{self.short_code}', long_url='{self.long_url}')>"

