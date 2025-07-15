import time

class RedisRateLimiter:
    def __init__(self, redis_client, max_requests, window_seconds):
        """
        Initializes the RedisRateLimiter instance.

        Args:
            redis_client: An instance of a Redis client used to interact with the Redis datastore.
            max_requests (int): The maximum number of allowed requests within the specified time window.
            window_seconds (int): The duration of the rate limiting window in seconds.

        Attributes:
            redis: Stores the provided Redis client instance.
            max_requests: Stores the maximum number of allowed requests.
            window_seconds: Stores the duration of the rate limiting window in seconds.
        """
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, client_id):
        """
        Implements a fixed window rate limiter using Redis.
        """
        key = f"rate_limit:{client_id}"
        current_count = self.redis.incr(key)

        if current_count == 1:
            # Set the TTL on first request
            self.redis.expire(key, self.window_seconds)

        if current_count > self.max_requests:
            return False
        return True
