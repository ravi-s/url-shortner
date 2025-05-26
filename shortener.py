import string
import random
import sys

import json
import os

class URLShortener:
    def __init__(self, data_file='data.json'):
        self.data_file = data_file
        self.url_map = {}
        self.reverse_map = {}  # long_url -> short_code (for deduplication)
        self.base_url = "http://short.ly/"
        self._load_data()

    def _generate_short_code(self, length=6):
        import random, string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def shorten_url(self, long_url):
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
        if long_url in self.reverse_map:
            return self.base_url + self.reverse_map[long_url]

        short_code = self._generate_short_code()
        while short_code in self.url_map:
            short_code = self._generate_short_code()

        self.url_map[short_code] = long_url
        self.reverse_map[long_url] = short_code
        self._save_data()
        return self.base_url + short_code

    def resolve_url(self, short_url):
        short_code = short_url.split('/')[-1]
        return self.url_map.get(short_code, "URL not found.")

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
        with open(self.data_file, 'w') as f:
            json.dump({
                "url_map": self.url_map,
                "reverse_map": self.reverse_map
            }, f, indent=2)



# Example usage
# shortener = URLShortener()
# short = shortener.shorten_url("https://en.wikipedia.org/wiki/Main_Page")
# print("Short URL:", short)
# print("Resolved:", shortener.resolve_url(short))

def print_usage():
    print("Usage:")
    print("  python shortner.py shorten <long_url>")
    print("  python shortner.py resolve <short_url>")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print_usage()

    command = sys.argv[1]
    value = sys.argv[2]
    shortener = URLShortener()

    if command == "shorten":
        short_url = shortener.shorten_url(value)
        print("Short URL:", short_url)
    elif command == "resolve":
        long_url = shortener.resolve_url(value)
        print("Original URL:", long_url)
    else:
        print_usage()