"""
Test the updated cache service with file fallback
"""
from cache_service import cache_service

def test_cache_service():
    """Test the cache service with both Redis and file fallback"""
    print("🧪 Testing Cache Service")
    print("=" * 40)
    
    # Test status
    status = cache_service.get_status()
    print(f"📊 Cache Status: {status}")
    
    # Test storing a document
    test_data = b"This is a test document for caching!"
    cache_key = "test_document_123"
    
    print(f"\n📤 Storing test document: {len(test_data)} bytes")
    cache_service.set_document(cache_key, test_data, 300)  # 5 minutes
    
    # Test retrieving document
    print(f"\n📥 Retrieving test document...")
    retrieved_data = cache_service.get_document(cache_key)
    
    if retrieved_data == test_data:
        print("✅ Cache service test PASSED!")
        print(f"   Original: {len(test_data)} bytes")
        print(f"   Retrieved: {len(retrieved_data)} bytes")
    else:
        print("❌ Cache service test FAILED!")
        return False
    
    # Test deletion
    print(f"\n🗑️ Deleting test document...")
    cache_service.delete_document(cache_key)
    
    # Verify deletion
    deleted_check = cache_service.get_document(cache_key)
    if deleted_check is None:
        print("✅ Document deletion confirmed!")
    else:
        print("❌ Document deletion failed!")
        return False
    
    print("\n🎉 All cache service tests passed!")
    return True

if __name__ == "__main__":
    test_cache_service()