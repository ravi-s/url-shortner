import time
from shortener import URLShortener

def run_cache_test():
    shortener = URLShortener()

    url = "https://example.com/test-cache"
    short_url = shortener.shorten_url(url)
    print("Short URL:", short_url)

    # First resolve → DB hit + cache populate
    start = time.time()
    resolved = shortener.resolve_url(short_url)
    print("First resolve:", resolved, "took", round(time.time() - start, 5), "seconds")

    # Second resolve → Redis cache hit
    start = time.time()
    resolved = shortener.resolve_url(short_url)
    print("Second resolve:", resolved, "took", round(time.time() - start, 5), "seconds")

if __name__ == "__main__":
    run_cache_test()
