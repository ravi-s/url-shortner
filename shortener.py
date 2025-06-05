import string
import random
import sys

import json
import os
import logging
import time

from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Or DEBUG if you want more detail


logger.info("LOADED: shortener.py")

class URLShortener:
    def __init__(self, data_file='data.json'):
        
        self.data_file = os.path.join(os.path.dirname(__file__), data_file)
        self.url_map = {}
        self.reverse_map = {}  # long_url -> short_code (for deduplication)
        self.base_url = "http://short.ly/"
        self._load_data()

    def _generate_short_code(self, length=6):
        import random, string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def shorten_url(self, long_url, expires_in = None):
        """
        Shortens a given URL by generating a unique short code and mapping it to the long URL.

        This method checks if the URL has already been shortened before. If it has, returns the existing
        shortened URL. Otherwise, generates a new short code, ensures it's unique, and creates
        bi-directional mappings between the long URL and short code.

        Args:
            long_url (str): The original URL that needs to be shortened.

        Returns:
            str: The shortened URL consisting of the base URL concatenated with the short code.

        Example:
            >>> url_shortener = URLShortener()
            >>> url_shortener.shorten_url("https://www.example.com/very/long/path")
            'http://short.url/abc123'
        """
        logger.info(f"SHORTEN called with: {long_url}, expires_in={expires_in}")

        if long_url in self.reverse_map:
            short_code = self.reverse_map[long_url]
            return self.base_url + short_code
        
        # Validate expires_in
        if expires_in is not None:
            if not isinstance(expires_in, (int, float)):
                raise ValueError("expires_in must be a number (seconds from now)")
            if expires_in < 0:
                logger.warning(f"Expiration time is in the past: {expires_in} seconds")
    

        short_code = self._get_unique_short_code()

        # Explicit variable for expiration timestamp
        expiration_timestamp_or_None = time.time() + expires_in if expires_in else None

        # Store both long URL and expiration in the map
        self.url_map[short_code] = {
            "long_url": long_url,
            "expires_at": expiration_timestamp_or_None
     }

        self.reverse_map[long_url] = short_code
        self._save_data()
        return self.base_url + short_code

    def resolve_url(self, short_url):

        short_code = short_url.split('/')[-1]
        entry = self.url_map.get(short_code)

        if not entry:
            return "URL not found."
        # If using new format with expiration
        if isinstance(entry, dict):
            long_url = entry.get("long_url")
            expires_at = entry.get("expires_at")

        if expires_at and int(time.time()) > expires_at:
            logger.info(f"URL expired for short_code: {short_code}")
            # Delete expired entry
            del self.url_map[short_code]
            if long_url in self.reverse_map:
                del self.reverse_map[long_url]
            self._save_data()
            return "URL has expired."
        else:
            return long_url

    # Fallback for old data format (string, no expiration)
        return entry
    

    def _load_data(self):
        """
        Load URL mapping data from a JSON file.

        This method reads the stored URL mappings from a JSON file if it exists.
        The data file contains two mappings:
        - url_map: Maps shortened URLs to their original URLs
        - reverse_map: Maps original URLs to their shortened versions

        The mappings are loaded into the instance variables:
        - self.url_map
        - self.reverse_map

        If the file doesn't exist, the mappings remain empty dictionaries.

        Returns:
            None
        """
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.url_map = data.get("url_map", {})
                self.reverse_map = data.get("reverse_map", {})

    def _save_data(self):
        """Save URL mapping data to a JSON file.

        This method persists both the URL mapping and reverse mapping dictionaries
        to the specified data file in JSON format with proper indentation.

        Returns:
            None

        Raises:
            IOError: If there is an error writing to the data file.
        """
        
        logger.info("Saving to file...")

        with open(self.data_file, 'w') as f:
            json.dump({
                "url_map": self.url_map,
                "reverse_map": self.reverse_map
            }, f, indent=2)

    def get_all_mappings(self):
        """
            Returns a dictionary mapping of full short URLs to their long URLs.
        """
        return {self.base_url + code: url for code, url in self.url_map.items()}
    
    def _is_valid_url(self, url):
        """Check if the URL is syntactically valid."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
        
    def _get_unique_short_code(self, max_attempts=5):
        """
        Generate a unique short code, retrying if there's a collision.
        Args:
            max_attempts (int): Maximum number of attempts to generate a unique code.
        Returns:
            str: A unique short code.
        Raises:
            Exception: If a unique code cannot be generated after several attempts.
        """
        
        for _ in range(max_attempts):
            short_code = self._generate_short_code()
            if short_code not in self.url_map:
                return short_code
        raise Exception("Failed to generate unique short code after several attempts.")
    
    def get_stats(self):
        """
        Retrieve statistics about the URL shortener's stored data.

        Returns:
            dict: A dictionary containing:
                - "total_urls" (int): Total number of URLs stored.
                - "active_urls" (int): Number of active (non-expired) URLs.
                - "expired_urls" (int): Number of expired URLs.
                - "data_file_size" (int): Size of the data file in bytes.
        """
        total = 0
        active = 0
        expired = 0
        now = int(time.time())

        for entry in self.url_map.values():
            if isinstance(entry, dict):
                total += 1
                expires_at = entry.get("expires_at")
                if expires_at is None or expires_at > now:
                    active += 1
                else:
                    expired += 1
            else:
                total += 1
                active += 1  # Old format: no expiration

        data_file_size = os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0

        return {
            "total_urls": total,
            "active_urls": active,
            "expired_urls": expired,
            "data_file_size": data_file_size
        }





# Example usage
# shortener = URLShortener()
# short = shortener.shorten_url("https://en.wikipedia.org/wiki/Main_Page")
# print("Short URL:", short)
# print("Resolved:", shortener.resolve_url(short))

def print_usage():
    print("Usage:")
    print("  python shortener.py shorten <long_url>")
    print("  python shortener.py resolve <short_url>")
    sys.exit(1)

if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print_usage()

    command = sys.argv[1]
    value = sys.argv[2]

    shortener = URLShortener()
    # Save the original method
    original_generate = shortener._generate_short_code


    if command == "shorten":
        short_url = shortener.shorten_url(value)
        print("Short URL:", short_url)
    elif command == "resolve":
        long_url = shortener.resolve_url(value)
        print("Original URL:", long_url)
    else:
        print_usage()