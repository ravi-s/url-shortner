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

class URLShortener:
    def __init__(self, db_uri="sqlite:///data.db"):
        self.engine = get_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = get_session_factory(db_uri)
        # self.base_url = "http://short.ly/"

    def _generate_short_code(self, length=6):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def shorten_url(self, long_url, expires_in=None):
        created_at = int(time.time())
        expires_at = created_at + expires_in if expires_in else None

        with get_session(self.Session) as session:
            # Check if URL already exists
            existing = session.query(URLMap).filter_by(long_url=long_url).first()
            if existing:
                return f"http://short.est/{existing.short_code}"

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

        return f"http://short.est/{short_code}"

    def resolve_url(self, short_url):
        short_code = short_url.split("/")[-1]

        with get_session(self.Session) as session:
            entry = session.query(URLMap).filter_by(short_code=short_code).first()

            if not entry:
                return "URL not found."

            if entry.expires_at and int(time.time()) > entry.expires_at:
                session.delete(entry)
                return "URL has expired."

            return entry.long_url

    def get_all_mappings(self):
        with get_session(self.Session) as session:
            entries = session.query(URLMap).all()
            return {f"http://short.est/{entry.short_code}": entry.long_url for entry in entries}
    
    # def _is_valid_url(self, url):
    #     """Check if the URL is syntactically valid."""
    #     try:
    #         result = urlparse(url)
    #         return all([result.scheme, result.netloc])
    #     except:
    #         return False
        
    # def _get_unique_short_code(self, max_attempts=5):
    #     """
    #     Generate a unique short code, retrying if there's a collision.
    #     Args:
    #         max_attempts (int): Maximum number of attempts to generate a unique code.
    #     Returns:
    #         str: A unique short code.
    #     Raises:
    #         Exception: If a unique code cannot be generated after several attempts.
    #     """
        
    #     for _ in range(max_attempts):
    #         short_code = self._generate_short_code()
    #         if short_code not in self.url_map:
    #             return short_code
    #     raise Exception("Failed to generate unique short code after several attempts.")
    
    # def get_stats(self):
    #     """
    #     Retrieve statistics about the URL shortener's stored data.

    #     Returns:
    #         dict: A dictionary containing:
    #             - "total_urls" (int): Total number of URLs stored.
    #             - "active_urls" (int): Number of active (non-expired) URLs.
    #             - "expired_urls" (int): Number of expired URLs.
    #             - "data_file_size" (int): Size of the data file in bytes.
    #     """
    #     total = 0
    #     active = 0
    #     expired = 0
    #     now = int(time.time())

    #     for entry in self.url_map.values():
    #         if isinstance(entry, dict):
    #             total += 1
    #             expires_at = entry.get("expires_at")
    #             if expires_at is None or expires_at > now:
    #                 active += 1
    #             else:
    #                 expired += 1
    #         else:
    #             total += 1
    #             active += 1  # Old format: no expiration

    #     data_file_size = os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0

    #     return {
    #         "total_urls": total,
    #         "active_urls": active,
    #         "expired_urls": expired,
    #         "data_file_size": data_file_size
    #     }





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