from flask import Flask
from flask import render_template, request, redirect, url_for
import logging
from logging.handlers import RotatingFileHandler
from shortener import URLShortener
from utils.rate_limiter import RateLimiter

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

# Example: 5 requests per 60 seconds
rate_limiter = RateLimiter(max_requests = 5, window_seconds = 60)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# app.py (add these)

# (you already have) from shortener import URLShortener

shortener = URLShortener(base_url="http://short.ly/")

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
