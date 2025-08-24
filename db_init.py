# db_init.py
from model.db import Base, get_engine
from model.models import URLMap  # Import all your models here

if __name__ == "__main__":
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(get_engine())
    print("✅ Tables created.")
