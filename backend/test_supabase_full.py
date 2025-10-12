"""
Full test script for Supabase integration
Run this after creating tables to verify everything works
"""

from supabase_manager import SupabaseManager
import json

def test_complete_supabase_functionality():
    """Test all Supabase functionality"""
    print("🧪 Testing Complete Supabase Functionality")
    print("=" * 50)
    
    try:
        # Initialize Supabase
        db = SupabaseManager()
        
        # Test 1: Connection
        print("1. Testing connection...")
        if not db.test_connection():
            print("❌ Connection failed. Make sure tables are created.")
            return False
        print("✅ Connection successful!")
        
        # Test 2: Create person
        print("\n2. Testing person creation...")
        person_id = db.create_person(
            name="John Doe",
            roll_number="2024001",
            branch="Computer Science",
            email="john.doe@example.com",
            phone="+1234567890"
        )
        
        if not person_id:
            print("❌ Failed to create person")
            return False
        print(f"✅ Created person with ID: {person_id}")
        
        # Test 3: Find person by name
        print("\n3. Testing person search...")
        found_person = db.find_person_by_name("John Doe")
        if not found_person:
            print("❌ Failed to find person")
            return False
        print(f"✅ Found person: {found_person['name']}")
        
        # Test 4: Find by roll number
        print("\n4. Testing roll number search...")
        found_by_roll = db.find_person_by_roll_number("2024001")
        if not found_by_roll:
            print("❌ Failed to find person by roll number")
            return False
        print(f"✅ Found by roll number: {found_by_roll['name']}")
        
        # Test 5: Add scan history
        print("\n5. Testing scan history...")
        scan_data = {
            "student_name": "John Doe",
            "roll_number": "2024001",
            "branch": "Computer Science",
            "confidence": 95.5
        }
        
        scan_id = db.add_scan_history(
            person_id=person_id,
            scanned_text="Test document content",
            confidence_score=95.5,
            document_type="Student ID",
            extracted_data=scan_data
        )
        
        if not scan_id:
            print("❌ Failed to add scan history")
            return False
        print(f"✅ Added scan history with ID: {scan_id}")
        
        # Test 6: Get scan history
        print("\n6. Testing scan history retrieval...")
        history = db.get_person_scan_history(person_id)
        if not history:
            print("❌ Failed to get scan history")
            return False
        print(f"✅ Retrieved {len(history)} scan history records")
        
        # Test 7: Update person
        print("\n7. Testing person update...")
        updated = db.update_person(
            person_id, 
            email="john.doe.updated@example.com",
            phone="+0987654321"
        )
        if not updated:
            print("❌ Failed to update person")
            return False
        print("✅ Person updated successfully")
        
        # Test 8: Search functionality
        print("\n8. Testing search functionality...")
        search_results = db.search_persons("John")
        if not search_results:
            print("❌ Search failed")
            return False
        print(f"✅ Search found {len(search_results)} results")
        
        # Test 9: Get all persons
        print("\n9. Testing get all persons...")
        all_persons = db.get_all_persons()
        if not all_persons:
            print("❌ Failed to get all persons")
            return False
        print(f"✅ Retrieved {len(all_persons)} persons")
        
        # Test 10: Clean up (delete test person)
        print("\n10. Testing deletion...")
        deleted = db.delete_person(person_id)
        if not deleted:
            print("❌ Failed to delete person")
            return False
        print("✅ Person deleted successfully")
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED!")
        print("🚀 Supabase is ready for your Smart Campus application!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def create_sample_data():
    """Create some sample data for testing"""
    print("\n📊 Creating sample data...")
    
    try:
        db = SupabaseManager()
        
        sample_students = [
            {
                "name": "Alice Johnson",
                "roll_number": "CS2024001", 
                "branch": "Computer Science",
                "email": "alice.johnson@university.edu"
            },
            {
                "name": "Bob Smith",
                "roll_number": "EE2024002",
                "branch": "Electrical Engineering", 
                "email": "bob.smith@university.edu"
            },
            {
                "name": "Charlie Brown",
                "roll_number": "ME2024003",
                "branch": "Mechanical Engineering",
                "email": "charlie.brown@university.edu"
            }
        ]
        
        created_count = 0
        for student in sample_students:
            person_id = db.create_person(**student)
            if person_id:
                created_count += 1
                
                # Add sample scan history
                db.add_scan_history(
                    person_id=person_id,
                    scanned_text=f"Student ID for {student['name']}",
                    confidence_score=92.3,
                    document_type="Student ID",
                    extracted_data=student
                )
        
        print(f"✅ Created {created_count} sample students")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")

if __name__ == "__main__":
    # Run complete test
    success = test_complete_supabase_functionality()
    
    if success:
        # Ask if user wants sample data
        print("\n" + "="*50)
        response = input("🤔 Would you like to create sample student data? (y/n): ")
        if response.lower() in ['y', 'yes']:
            create_sample_data()
    else:
        print("\n💡 Please ensure tables are created in Supabase dashboard")
        print("   Run: python setup_supabase.py for instructions")