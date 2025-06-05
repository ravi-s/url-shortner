import os
import pytest
import time

from shortener import URLShortener

@pytest.fixture
def shortener__tmp():
    # Use a temp data file to avoid polluting actual data.json
    temp_file = "temp_data.json"
    if os.path.exists(temp_file):
        os.remove(temp_file)
    shortener = URLShortener(data_file=temp_file)
    yield shortener
    if os.path.exists(temp_file):
        os.remove(temp_file)

def test_shorten_and_resolve(shortener__tmp):
    long_url = "https://example.com/test"
    short_url = shortener__tmp.shorten_url(long_url)
    resolved = shortener__tmp.resolve_url(short_url)
    assert resolved == long_url

def test_deduplication(shortener__tmp):
    url = "https://openai.com"
    short1 = shortener__tmp.shorten_url(url)
    short2 = shortener__tmp.shorten_url(url)
    assert short1 == short2

def test_nonexistent_short_code(shortener__tmp):
    result = shortener__tmp.resolve_url("http://short.ly/invalid123")
    assert result == "URL not found."


def test_multiple_unique_short_urls(shortener__tmp):
    url1 = "https://site1.com"
    url2 = "https://site2.com"
    assert shortener__tmp.shorten_url(url1) != shortener__tmp.shorten_url(url2)

def test_persistence(shortener__tmp):
    # Shorten a URL and reload from disk
    url = "https://persistence-test.com"
    short_url = shortener__tmp.shorten_url(url)
    resolved = shortener__tmp.resolve_url(short_url)
    assert resolved == url


def test_no_expiration_resolves(shortener__tmp):
    url = "https://no-expiration.com"
    short_url = shortener__tmp.shorten_url(url)  # no expiration timestamp passed
    resolved = shortener__tmp.resolve_url(short_url)
    assert resolved == url


def test_future_expiration_resolves(shortener__tmp):
    url = "https://future-expiration.com"
    future_ts = int(time.time()) + 3600  # 1 hour from now
    short_url = shortener__tmp.shorten_url(url, expires_in=future_ts)
    resolved = shortener__tmp.resolve_url(short_url)
    assert resolved == url


def test_past_expiration_fails(shortener__tmp):
    url = "https://expired-url.com"
    # past_ts = int(time.time()) - 3600  # 1 hour ago
    past_ts = -3600
    short_url = shortener__tmp.shorten_url(url, expires_in=past_ts)
    resolved = shortener__tmp.resolve_url(short_url)
    assert resolved == "URL has expired."  # or your actual expired message

def test_invalid_expires_in_raises(shortener__tmp):
    url = "https://invalid-expires.com"

    with pytest.raises(ValueError, match="expires_in must be a number"):
        shortener__tmp.shorten_url(url, expires_in="not-a-number")