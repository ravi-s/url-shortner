from flask import Flask
from flask import render_template, request, redirect, url_for,jsonify
import logging
from logging.handlers import RotatingFileHandler
from shortener import URLShortener
from functools import wraps

import redis
from utils.redis_rate_limiter import RedisRateLimiter

'''
Flask application for URL shortening service.


    GET /: Serves the main page with a form to shorten URLs.
    POST /shorten: Shortens a long URL submitted via the form.
    GET /s/<short_code>: Displays the shortened URL and resolves it to its original form.

Classes:
    URLShortener: Handles the core URL shortening and resolution logic.

Functions:
    index(): Serves the main page with a form to shorten URLs.
    shorten(): Handles form submission to create a short URL.
    show_short_url(short_code): Displays the shortened URL and resolves it to its original form.

Usage:
    Run this script to start the Flask development server. The application will be
    accessible at http://localhost:6000.
'''



app = app = Flask(__name__, static_folder="static", template_folder="templates")



# Set this to your Redis Cloud URL
REDIS_URL = "redis://:3jovYCcF0BqY68VIBBZdDLjUJsLG9KEd@redis-17837.c330.asia-south1-1.gce.redns.redis-cloud.com:17837"
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# Replace old limiter
rate_limiter = RedisRateLimiter(redis_client, max_requests=5, window_seconds=60)


# Configure logging
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# Example: Hardcoded valid API keys (set of strings)
VALID_API_KEYS = {
    "api_key_123",
    "api_key_456",
    "api_key_789"
}

def require_api_key(f):
    """Decorator to enforce API key validation via request headers."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key or api_key not in VALID_API_KEYS:
            return jsonify({"error": "Invalid or missing API key."}), 401
        return f(*args, **kwargs)
    return decorated_function

shortener = URLShortener(base_url="http://short.ly/", redis_client=redis_client)

@app.route('/')
def index():
    """Serve the main page with form to shorten URLs."""
    app.logger.info("Serving index page")
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten():
    """Create a short URL from form submission."""
    client_ip = request.remote_addr
    if not rate_limiter.is_allowed(client_ip):
        app.logger.info(f"Rate limit exceeded for {client_ip}")
        return render_template('rate_limit.html'), 429
    
    app.logger.info(f"Rate limit check passed for {client_ip}")
    app.logger.info("Received request to shorten URL")
    long_url = request.form['long_url']

    short_url = shortener.shorten_url(long_url)
    app.logger.info(f"Shortened URL: {short_url}")
    return redirect(url_for('show_short_url', short_code=short_url.split('/')[-1]))

@app.route('/s/<short_code>')
def show_short_url(short_code):

    """Displays the shortened URL after it's been created."""
    app.logger.info(f"Resolving short code: {short_code}")
    entry = shortener.resolve_url(f'{request.host_url}s/{short_code}')

    return render_template('short_url.html', short_code=short_code, resolved=entry)

@app.route('/api/shorten', methods=['POST'])
@require_api_key
def shorten_api():
    """API-only URL shortening endpoint with API key and rate limiting."""
    client_ip = request.remote_addr

    # Rate limiting check
    if not rate_limiter.is_allowed(client_ip):
        app.logger.info(f"Rate limit exceeded for {client_ip}")
        return jsonify({"error": "Rate limit exceeded. Try again later."}), 429

    data = request.get_json()
    long_url = data.get('long_url')
    if not long_url:
        return jsonify({"error": "Missing long_url"}), 400

    short_url = shortener.shorten_url(long_url)
    return jsonify({"short_url": short_url})

@app.route('/admin/cleanup', methods=['POST'])
def trigger_cleanup():
    """
        Endpoint to trigger cleanup of expired data via a POST request.

        This route is intended for administrative use and should be protected with a secret token.
        It expects an 'x-cron-token' header containing the correct secret token. If the token is invalid or missing,
            the request is rejected with a 401 Unauthorized response.

        Upon successful authentication, it imports and executes the `clean_expired` function from the `cleanup` module
        to perform the cleanup operation.

    Returns:
        str: A message indicating the result of the operation.
        int: HTTP status code (200 for success, 401 for unauthorized).
    """
    # Optional: Protect with a secret API key or token
    token = request.headers.get('x-cron-token')
    if token != "example_secret_token":
        return "Unauthorized", 401

    from cleanup import clean_expired
    clean_expired()
    return "Cleanup triggered.", 200
