from flask import Flask, request, jsonify
from shortener import URLShortener
# import logging


"""Flask application for URL shortening service.

This module provides HTTP endpoints for shortening URLs and resolving shortened URLs
back to their original form. It uses the URLShortener class to handle the core
URL shortening functionality.

Endpoints:
    POST /shorten: Shortens a long URL
    GET /resolve/<short_code>: Resolves a short URL to its original long URL
"""

app = Flask(__name__)
shortener = URLShortener()

@app.route('/')
def home():
    """Home route for the Flask application."""
    app.logger.debug("Home route accessed")
    return 'Flask app is running.'



@app.route('/shorten', methods=['POST'])
def shorten():
    """Shorten a long URL.
    Expects a POST request with JSON payload containing 'long_url' key.
    Returns:
        JSON response with shortened URL or error message
        200: Successfully shortened URL
        400: Missing long_url in request
    """
    app.logger.debug("Shorten route accessed")
    data = request.get_json()
    long_url = data.get('long_url')
    if not long_url:
        return jsonify({"error": "Missing long_url"}), 400

    result = shortener.shorten_url(long_url)

    if isinstance(result, tuple):  # Means we got an error like ("Invalid URL", 400)
        return jsonify({"error": result[0]}), result[1]
    
    short_url = shortener.shorten_url(long_url)
    return jsonify({"short_url": short_url})

@app.route('/resolve/<short_code>', methods=['GET'])
def resolve(short_code):
    short_url = shortener.base_url + short_code
    long_url = shortener.resolve_url(short_url)
    if long_url == "URL not found.":
        return jsonify({"error": "Short URL not found"}), 404
    return jsonify({"long_url": long_url})

@app.route('/list', methods=['GET'])
def list_all():
    """List all short → long URL mappings."""
    url_map = shortener.get_all_mappings()
    return jsonify(url_map)


if __name__ == '__main__':
    app.run(port=6000, debug=True)
    # app.run(host='127.0.0.1', port=5000, debug=True)


