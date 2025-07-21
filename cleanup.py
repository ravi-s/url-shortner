from model.db import get_session,get_session_factory
from model.models import URLMap
import time

# This script cleans up expired URL mappings from the database.
# It queries for URLMap entries where the expiration time is set and has passed,
# then deletes those entries and prints the count of deleted URLs.
# It is intended to be run periodically to maintain the database. 

def clean_expired():
    now = int(time.time())
    session_factory = get_session_factory()
    with get_session(session_factory) as session:
    
        expired = session.query(URLMap).filter(URLMap.expires_at != None).filter(URLMap.expires_at < now).all()
        count = len(expired)
        for entry in expired:
            session.delete(entry)
        
        # Step 2: Get remaining count after deletion
        remaining = session.query(URLMap).count()
        print(f"[{time.ctime()}] Deleted {count} expired URLs.")
        print(f"Remaining entries in DB: {remaining}")


if __name__ == "__main__":
    clean_expired()
  