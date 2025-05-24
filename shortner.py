import string
import random
import sys

class URLShortener:
    def __init__(self):
        self.url_map = {}
        self.base_url = "http://short.ly/"
    
    def _generate_short_code(self, length=6):
        """
        Generate a random short code using a combination of ASCII letters and digits.
        
        This method creates a pseudo-random string intended as a unique identifier for a shortened URL.
        It selects characters randomly from uppercase and lowercase ASCII letters and digits.
        The length of the generated code is configurable through the 'length' parameter (default is 6).
        
        Parameters:
            length (int): The number of characters to include in the generated short code (default is 6).
        
        Returns:
            str: A string representing the generated short code.
        
        Security Note:
            - Utilizes the random.choices function to select characters.
            - Draws from a pool of characters provided by string.ascii_letters and string.digits.
            - Designed to be called repeatedly until a unique code is obtained within the URL mapping.
        
        Security Note:
            Since this method depends on the Python random module's pseudo-random number generator,
            it should not be used for cryptographic or security-sensitive applications.
        
        Examples:
            >>> shortener = URLShortener()
            >>> code = shortener._generate_short_code()
            >>> len(code)
            6
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def shorten_url(self, long_url):
        """
        Shortens the provided long URL by generating a unique short code and appending it to the base URL.
        
        Parameters:
            long_url (str): The original URL to shorten.
        
        Returns:
            str: The complete shortened URL, composed of the base URL and the unique short code.
        
        Notes:
            - If the long URL has already been shortened, the existing short URL is returned.
            - The method generates a short code using an internal helper method (_generate_short_code).
            - It ensures uniqueness by checking the generated code against an existing url mapping (self.url_map)
              and regenerates it if a collision is found.
        """
        # Check if the long URL has already been shortened
        for code, url in self.url_map.items():
            if url == long_url:
                return self.base_url + code
        
        short_code = self._generate_short_code()
        while short_code in self.url_map:
            short_code = self._generate_short_code()
        self.url_map[short_code] = long_url
        return self.base_url + short_code
        short_code = self._generate_short_code()
        while short_code in self.url_map:
            short_code = self._generate_short_code()
        self.url_map[short_code] = long_url
        return self.base_url + short_code

    def resolve_url(self, short_url):
        """
        Resolve a short URL to its corresponding original URL.

        Args:
            short_url (str): The shortened URL from which the unique short code is extracted. 
                             The code is expected to be the last segment of the URL.

        Returns:
            str: The original URL if the corresponding short code exists in the mapping,
                 otherwise returns "URL not found.".
        """
        short_code = short_url.split('/')[-1]
        return self.url_map.get(short_code, "URL not found.")

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