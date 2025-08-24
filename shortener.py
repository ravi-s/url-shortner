import json
import string
import random
import time
from sqlalchemy.exc import IntegrityError
from model.models import URLMap
from model.db import Base, get_engine, get_session_factory, get_session
import logging




logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Or DEBUG if you want more detail


logger.info("LOADED: shortener.py")

"""
A class to handle URL shortening functionality.

Methods:
    shorten_url(long_url, expires_in=None):
        Shortens a given long URL and optionally sets an expiration time.
"""
class URLShortener:
    BASE_URL = "http://short.est/"

    def __init__(self, db_uri="sqlite:///data.db", base_url=None, redis_client=None):
        self.engine = get_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = get_session_factory(db_uri)
        self.db_uri = db_uri
        self.base_url = base_url or self.BASE_URL
        self.redis = redis_client

    def _generate_short_code(self, length=6):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def shorten_url(self, long_url, expires_in = 60):
        """
        Shortens a given long URL and optionally sets an expiration time.

        Args:
            long_url (str): The original URL to be shortened.
            expires_in (int, optional): Time in seconds until the shortened URL expires. Defaults to None.

        Returns:
            str: The shortened URL if successful, or an error message if a database error occurs.

        Raises:
            IntegrityError: If a database integrity issue occurs during URL mapping creation.
        """
        created_at = int(time.time())
        expires_at = created_at + expires_in if expires_in else None

        with get_session() as session:
            # Check if URL already exists
            existing = session.query(URLMap).filter_by(long_url=long_url).first()
            if existing:
                return f"{self.base_url}{existing.short_code}"

            # Generate initial short_code
            short_code = self._generate_short_code()

            # Retry if duplicate short_code
            while session.query(URLMap).filter_by(short_code=short_code).first():
                short_code = self._generate_short_code()

        
        new_map = URLMap(
            short_code=short_code,
            long_url=long_url,
            created_at=created_at,
            expires_at=expires_at
        )
        session.add(new_map)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            logger.error("Failed to commit new URL mapping due to IntegrityError.")
            return "Failed to shorten URL due to a database error."
        
        # Cache in Redis (write-through)
        cache_value = json.dumps({
            "long_url": long_url,
            "expires_at": expires_at
        })
        if self.redis is not None:
            self.redis.set(short_code, cache_value)
        else:
            logger.error("Redis client is not configured. Cannot cache shortened URL.")

        return f"{self.base_url}{short_code}"
        
    def resolve_url(self, short_url):
        """
        Resolves a shortened URL to its original long URL.

        Args:
            short_url (str): The shortened URL to be resolved.

        Returns:
            str: The original long URL if the short URL is valid and not expired.
                 Returns "URL not found." if the short URL does not exist in the database.
                 Returns "URL has expired." if the short URL has expired.

        Behavior:
            - Extracts the short code from the given short URL.
            - Queries the database for the corresponding entry using the short code.
            - If the entry is not found, returns "URL not found."
            - If the entry has an expiration time and it has passed, deletes the entry
              from the database and returns "URL has expired."
            - If the entry is valid, returns the original long URL.
        """
        if not short_url:
            return "Invalid URL provided."
        
        short_code = short_url.split('/')[-1]
        cache_key = f"url_cache:{short_code}"
        # 1. Try Redis cache first
        cached_url = self.redis.get(cache_key) # type: ignore
        if cached_url:
            logger.info(f"Cache hit for {short_code}")
            return cached_url
        
        logger.info(f"Cache miss for {short_code}")
    
        with get_session() as session:
            entry = session.query(URLMap).filter_by(short_code=short_code).first()

            if not entry:
                return "URL not found."

            expires_at = getattr(entry, "expires_at", None)
            if expires_at is not None and int(time.time()) > expires_at:
                session.delete(entry)
                return "URL has expired."
            
            # 3. Cache result for future lookups (5 min TTL)
            # self.redis.setex(cache_key, 300, entry.long_url) # type: ignore
            # Repopulate Redis for next time
            cache_value = json.dumps({
                "long_url": entry.long_url,
                "expires_at": entry.expires_at
            })
            if self.redis is not None:
                self.redis.set(short_code, cache_value)
            else:
                logger.error("Redis client is not configured. Cannot cache resolved URL.")

            return entry.long_url

    def get_all_mappings(self):
        with get_session() as session:
            entries = session.query(URLMap).all()
            return {f"{self.base_url}{entry.short_code}": entry.long_url for entry in entries}
    
    

# Example usage
# shortener = URLShortener()
# short = shortener.shorten_url("https://en.wikipedia.org/wiki/Main_Page")
# print("Short URL:", short)
# print("Resolved:", shortener.resolve_url(short))

# def print_usage():
#     print("Usage:")
#     print("  python shortener.py shorten <long_url>")
#     print("  python shortener.py resolve <short_url>")
#     sys.exit(1)

# if __name__ == "__main__":
    
#     if len(sys.argv) != 3:
#         print_usage()

#     command = sys.argv[1]
#     value = sys.argv[2]

#     shortener = URLShortener()
#     # Save the original method
#     original_generate = shortener._generate_short_code


#     if command == "shorten":
#         short_url = shortener.shorten_url(value)
#         print("Short URL:", short_url)
#     elif command == "resolve":
#         long_url = shortener.resolve_url(value)
#         print("Original URL:", long_url)
#     else:
#         print_usage()