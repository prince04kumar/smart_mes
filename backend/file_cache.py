"""
Simple file-based cache service as alternative to Redis
This will work without any external dependencies
"""
import os
import json
import time
import hashlib
from pathlib import Path

class FileCacheService:
    def __init__(self, cache_dir="cache"):
        """Initialize file-based cache service"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        print(f"📁 File cache initialized: {self.cache_dir.absolute()}")
    
    def _get_cache_path(self, key):
        """Get file path for cache key"""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.cache"
    
    def _get_meta_path(self, key):
        """Get metadata file path for cache key"""
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{safe_key}.meta"
    
    def set_document(self, key, data, expire_seconds=3600):
        """Store document (bytes) in file cache"""
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_meta_path(key)
            
            # Write the binary data
            with open(cache_path, 'wb') as f:
                f.write(data)
            
            # Write metadata
            metadata = {
                'key': key,
                'expires': time.time() + expire_seconds,
                'size': len(data),
                'created': time.time()
            }
            
            with open(meta_path, 'w') as f:
                json.dump(metadata, f)
            
            print(f"📦 Document cached to file: {key} ({len(data)} bytes)")
            
        except Exception as e:
            print(f"⚠️ File cache set error: {e}")
    
    def get_document(self, key):
        """Retrieve document (bytes) from file cache"""
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_meta_path(key)
            
            # Check if files exist
            if not cache_path.exists() or not meta_path.exists():
                return None
            
            # Check metadata and expiration
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
            
            if time.time() > metadata['expires']:
                # Expired, remove files
                self.delete_document(key)
                return None
            
            # Read and return data
            with open(cache_path, 'rb') as f:
                data = f.read()
            
            print(f"📦 Document retrieved from file: {key} ({len(data)} bytes)")
            return data
            
        except Exception as e:
            print(f"⚠️ File cache get error: {e}")
            return None
    
    def delete_document(self, key):
        """Delete document from file cache"""
        try:
            cache_path = self._get_cache_path(key)
            meta_path = self._get_meta_path(key)
            
            if cache_path.exists():
                cache_path.unlink()
            
            if meta_path.exists():
                meta_path.unlink()
                
            print(f"🗑️ Document deleted from file cache: {key}")
            
        except Exception as e:
            print(f"⚠️ File cache delete error: {e}")
    
    def get_status(self):
        """Get cache service status"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        return {
            "cache_type": "file_based",
            "cache_directory": str(self.cache_dir.absolute()),
            "cached_files": len(cache_files),
            "directory_exists": self.cache_dir.exists()
        }
    
    def cleanup_expired(self):
        """Clean up expired cache files"""
        try:
            current_time = time.time()
            cleaned = 0
            
            for meta_file in self.cache_dir.glob("*.meta"):
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                    
                    if current_time > metadata['expires']:
                        # Delete expired files
                        key = metadata['key']
                        self.delete_document(key)
                        cleaned += 1
                        
                except Exception as e:
                    print(f"⚠️ Error cleaning {meta_file}: {e}")
            
            if cleaned > 0:
                print(f"🧹 Cleaned up {cleaned} expired cache files")
                
        except Exception as e:
            print(f"⚠️ Cache cleanup error: {e}")

# Test function
def test_file_cache():
    """Test file cache functionality"""
    cache = FileCacheService()
    
    # Test storing data
    test_data = b"Hello, this is test cache data!"
    cache.set_document("test_key", test_data, 60)  # 60 seconds expiry
    
    # Test retrieving data
    retrieved = cache.get_document("test_key")
    
    if retrieved == test_data:
        print("✅ File cache test passed!")
        return True
    else:
        print("❌ File cache test failed!")
        return False

if __name__ == "__main__":
    test_file_cache()