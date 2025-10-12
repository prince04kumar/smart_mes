import redis
import os
import logging
import time
from file_cache import FileCacheService

class CacheService:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', '6379'))  # Standard Redis port
        self.redis_db = int(os.getenv('REDIS_DB', '0'))
        self.client = None
        self.redis_enabled = False
        self.file_cache = FileCacheService()  # Always available file cache
        
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with error handling"""
        try:
            self.client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                db=self.redis_db,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            self.redis_enabled = True
            print(f"✅ Redis cache connected: {self.redis_host}:{self.redis_port}")
        except redis.ConnectionError as e:
            print(f"⚠️ Redis connection failed: {e}")
            print("� Using file-based cache as primary")
            self.redis_enabled = False
        except Exception as e:
            print(f"⚠️ Redis initialization error: {e}")
            print("� Using file-based cache as primary")
            self.redis_enabled = False

    def set_document(self, key, data, expire_seconds=3600):
        """Store document (bytes) in cache."""
        try:
            # Always use file cache as primary
            self.file_cache.set_document(key, data, expire_seconds)
            
            # Also try Redis if available
            if self.redis_enabled and self.client:
                try:
                    self.client.set(key, data, ex=expire_seconds)
                    print(f"📦 Document also cached in Redis: {key}")
                except:
                    pass  # Redis failure is OK, we have file cache
                    
        except Exception as e:
            print(f"⚠️ Cache set error: {e}")

    def get_document(self, key):
        """Retrieve document (bytes) from cache."""
        try:
            # First try Redis if available
            if self.redis_enabled and self.client:
                try:
                    data = self.client.get(key)
                    if data:
                        print(f"📦 Document retrieved from Redis: {key}")
                        return data
                except:
                    pass  # Fall through to file cache
            
            # Try file cache
            return self.file_cache.get_document(key)
            
        except Exception as e:
            print(f"⚠️ Cache get error: {e}")
            return None

    def delete_document(self, key):
        """Delete document from cache."""
        try:
            # Delete from file cache
            self.file_cache.delete_document(key)
            
            # Also delete from Redis if available
            if self.redis_enabled and self.client:
                try:
                    self.client.delete(key)
                except:
                    pass  # Redis failure is OK
                    
        except Exception as e:
            print(f"⚠️ Cache delete error: {e}")
    
    def get_status(self):
        """Get cache service status"""
        file_status = self.file_cache.get_status()
        return {
            "redis_enabled": self.redis_enabled,
            "redis_host": self.redis_host,
            "redis_port": self.redis_port,
            "file_cache": file_status
        }

cache_service = CacheService()
