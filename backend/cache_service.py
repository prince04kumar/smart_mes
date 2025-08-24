import redis
import os

class CacheService:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', '6379'))
        self.redis_db = int(os.getenv('REDIS_DB', '0'))
        self.client = redis.Redis(host=self.redis_host, port=self.redis_port, db=self.redis_db)

    def set_document(self, key, data, expire_seconds=3600):
        """Store document (bytes) in Redis cache."""
        self.client.set(key, data, ex=expire_seconds)

    def get_document(self, key):
        """Retrieve document (bytes) from Redis cache."""
        return self.client.get(key)

    def delete_document(self, key):
        self.client.delete(key)

cache_service = CacheService()
