import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://admin:password123@localhost:27017/')
        self.database_name = os.getenv('DATABASE_NAME', 'id_card_system')
        self.collection_name = os.getenv('COLLECTION_NAME', 'persons')
        self.client = None
        self.db = None
        self.collection = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection with timeout
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print(f"✅ Connected to MongoDB: {self.database_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("📡 Disconnected from MongoDB")
    
    def create_person(self, name, roll_number=None, branch=None, email=None, phone=None):
        """Create a new person in the database"""
        try:
            person_data = {
                "name": name,
                "roll_number": roll_number,
                "branch": branch,
                "email": email,
                "phone": phone,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "scan_history": []
            }
            
            result = self.collection.insert_one(person_data)
            print(f"✅ Created person: {name} with ID: {result.inserted_id}")
            return result.inserted_id
        except Exception as e:
            print(f"❌ Error creating person: {str(e)}")
            return None
    
    def find_person_by_name(self, name):
        """Find a person by name with flexible matching"""
        try:
            if not name or name.strip() == "":
                return None
                
            name = name.strip()
            print(f"🔍 Searching for person: '{name}'")
            
            # Strategy 1: Exact case-insensitive match
            person = self.collection.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})
            if person:
                print(f"✅ Found person (exact match): {person['name']}")
                return person
            
            # Strategy 2: Partial match - check if any part of the name matches
            # Split the extracted name into parts
            name_parts = name.lower().split()
            if len(name_parts) >= 2:
                # Try to match first and last name parts
                first_name = name_parts[0]
                last_name = name_parts[-1]
                
                # Search for documents where name contains both first and last name parts
                regex_pattern = f".*{first_name}.*{last_name}.*|.*{last_name}.*{first_name}.*"
                person = self.collection.find_one({"name": {"$regex": regex_pattern, "$options": "i"}})
                if person:
                    print(f"✅ Found person (partial match): {person['name']} for search: '{name}'")
                    return person
            
            # Strategy 3: Try matching individual name parts
            for name_part in name_parts:
                if len(name_part) >= 3:  # Only search for meaningful name parts
                    person = self.collection.find_one({"name": {"$regex": f".*{name_part}.*", "$options": "i"}})
                    if person:
                        print(f"✅ Found person (name part match): {person['name']} for part: '{name_part}'")
                        return person
            
            print(f"❌ Person not found with any strategy: '{name}'")
            
            # Debug: Show all persons in database for troubleshooting
            all_persons = list(self.collection.find({}, {"name": 1}))
            print(f"📋 Available persons in database: {[p['name'] for p in all_persons]}")
            
            return None
        except Exception as e:
            print(f"❌ Error finding person: {str(e)}")
            return None
    
    def find_person_by_roll_number(self, roll_number):
        """Find a person by roll number"""
        try:
            person = self.collection.find_one({"roll_number": roll_number})
            if person:
                print(f"✅ Found person by roll number: {person['name']}")
                return person
            else:
                print(f"❌ Person not found with roll number: {roll_number}")
                return None
        except Exception as e:
            print(f"❌ Error finding person by roll number: {str(e)}")
            return None
    
    def update_person_info(self, person_id, **kwargs):
        """Update person information"""
        try:
            kwargs['updated_at'] = datetime.now()
            result = self.collection.update_one(
                {"_id": person_id},
                {"$set": kwargs}
            )
            if result.modified_count > 0:
                print(f"✅ Updated person: {person_id}")
                return True
            else:
                print(f"❌ No changes made to person: {person_id}")
                return False
        except Exception as e:
            print(f"❌ Error updating person: {str(e)}")
            return False
    
    def add_scan_history(self, person_id, scan_data):
        """Add a scan record to person's history"""
        try:
            scan_record = {
                "timestamp": datetime.now(),
                "extracted_data": scan_data,
                "source": scan_data.get("source", "unknown")  # upload or webcam
            }
            
            result = self.collection.update_one(
                {"_id": person_id},
                {
                    "$push": {"scan_history": scan_record},
                    "$set": {"updated_at": datetime.now()}
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Added scan history for person: {person_id}")
                return True
            else:
                print(f"❌ Failed to add scan history for person: {person_id}")
                return False
        except Exception as e:
            print(f"❌ Error adding scan history: {str(e)}")
            return False
    
    def get_all_persons(self):
        """Get all persons in the database"""
        try:
            persons = list(self.collection.find({}))
            print(f"✅ Retrieved {len(persons)} persons from database")
            return persons
        except Exception as e:
            print(f"❌ Error retrieving persons: {str(e)}")
            return []
    
    def setup_sample_data(self):
        """Set up some sample data for testing"""
        sample_persons = [
            {
                "name": "John Doe",
                "roll_number": "CS2021001",
                "branch": "Computer Science",
                "email": "john.doe@university.edu",
                "phone": "+1234567890"
            },
            {
                "name": "Jane Smith", 
                "roll_number": "EE2021002",
                "branch": "Electrical Engineering",
                "email": "jane.smith@university.edu",
                "phone": "+1234567891"
            },
            {
                "name": "Alice Johnson",
                "roll_number": "ME2021003", 
                "branch": "Mechanical Engineering",
                "email": "alice.johnson@university.edu",
                "phone": "+1234567892"
            }
        ]
        
        for person in sample_persons:
            existing = self.find_person_by_name(person["name"])
            if not existing:
                self.create_person(**person)
            else:
                print(f"✅ Sample person already exists: {person['name']}")

# Global database instance
db_manager = DatabaseManager()
