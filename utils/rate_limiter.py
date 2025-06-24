import time
"""
RateLimiter provides a simple in-memory rate limiting mechanism for clients identified by a unique client_id (e.g., IP address).
It restricts the number of allowed requests per client within a specified time window.

Attributes:
    max_requests (int): Maximum number of requests allowed per client within the time window.
    window_seconds (int): Duration of the time window in seconds.
    clients (dict): Stores client-specific data, mapping client_id to a dictionary containing:
        - 'count': Number of requests made in the current window.
        - 'reset_time': Timestamp when the current window expires for the client.

Methods:
    is_allowed(client_id):
        Checks if a request from the given client_id is allowed under the current rate limit.
        Returns True if allowed, otherwise False. Resets the counter when the time window expires.
"""

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients = {}  # key: client_id (IP), value: {count, reset_time}

    def is_allowed(self, client_id):
        current_time = int(time.time())
        client_data = self.clients.get(client_id)

        if not client_data:
            # First request from this client
            self.clients[client_id] = {"count": 1, "reset_time": current_time + self.window_seconds}
            return True

        if current_time > client_data["reset_time"]:
            # Time window expired → Reset counter
            self.clients[client_id] = {"count": 1, "reset_time": current_time + self.window_seconds}
            return True

        if client_data["count"] < self.max_requests:
            self.clients[client_id]["count"] += 1
            return True
        else:
            return False  # Limit reached
