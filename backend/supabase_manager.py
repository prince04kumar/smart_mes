import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import json
from typing import Dict, List, Optional

# Load environment variables
load_dotenv()

class SupabaseManager:
    def __init__(self):
        """Initialize Supabase client with retry logic"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("❌ Supabase URL and Key must be set in environment variables")
        
        self.supabase = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize Supabase client with error handling"""
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            print("✅ Supabase client initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Supabase: {str(e)}")
            raise
    
    def _ensure_connection(self):
        """Ensure Supabase client is connected, reinitialize if needed"""
        try:
            if not self.supabase:
                self._initialize_client()
            # Test connection with a simple query
            self.supabase.table('persons').select('id').limit(1).execute()
        except Exception as e:
            print(f"⚠️ Supabase connection lost, reinitializing: {e}")
            try:
                self._initialize_client()
            except Exception as init_error:
                print(f"❌ Failed to reinitialize Supabase: {init_error}")
                raise
    
    def test_connection(self):
        """Test Supabase connection with retry"""
        try:
            self._ensure_connection()
            print("✅ Supabase connection successful!")
            return True
        except Exception as e:
            print(f"❌ Supabase connection test failed: {str(e)}")
            print("💡 Make sure your tables are created in Supabase dashboard")
            return False
    
    def create_tables(self):
        """
        Note: Tables should be created in Supabase Dashboard
        This method provides the SQL commands to run manually
        """
        sql_commands = """
        -- Create persons table
        CREATE TABLE IF NOT EXISTS persons (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            roll_number VARCHAR(100),
            branch VARCHAR(100),
            email VARCHAR(255),
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Create scan_history table
        CREATE TABLE IF NOT EXISTS scan_history (
            id SERIAL PRIMARY KEY,
            person_id INTEGER REFERENCES persons(id),
            scanned_text TEXT,
            confidence_score FLOAT,
            document_type VARCHAR(100),
            scan_timestamp TIMESTAMP DEFAULT NOW(),
            extracted_data JSONB
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);
        CREATE INDEX IF NOT EXISTS idx_persons_roll_number ON persons(roll_number);
        CREATE INDEX IF NOT EXISTS idx_scan_history_person_id ON scan_history(person_id);

        -- Enable Row Level Security (RLS)
        ALTER TABLE persons ENABLE ROW LEVEL SECURITY;
        ALTER TABLE scan_history ENABLE ROW LEVEL SECURITY;

        -- Create policies (adjust as needed)
        CREATE POLICY "Enable all operations for authenticated users" ON persons
            FOR ALL USING (true);

        CREATE POLICY "Enable all operations for authenticated users" ON scan_history
            FOR ALL USING (true);
        """
        
        print("📋 SQL Commands to create tables in Supabase:")
        print(sql_commands)
        return sql_commands
    
    def create_person(self, name: str, roll_number: str = None, branch: str = None, 
                     email: str = None, phone: str = None) -> Optional[int]:
        """Create a new person in the database"""
        try:
            person_data = {
                "name": name,
                "roll_number": roll_number,
                "branch": branch,
                "email": email,
                "phone": phone,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.supabase.table('persons').insert(person_data).execute()
            
            if result.data and len(result.data) > 0:
                person_id = result.data[0]['id']
                print(f"✅ Created person: {name} with ID: {person_id}")
                return person_id
            else:
                print(f"❌ Failed to create person: {name}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating person: {str(e)}")
            return None
    
    def find_person_by_name(self, name: str) -> Optional[Dict]:
        """Find a person by name with flexible matching"""
        try:
            if not name or name.strip() == "":
                return None
                
            name = name.strip()
            print(f"🔍 Searching for person: '{name}'")
            
            # Strategy 1: Exact case-insensitive match
            result = self.supabase.table('persons').select('*').ilike('name', name).execute()
            
            if result.data and len(result.data) > 0:
                person = result.data[0]
                print(f"✅ Found person (exact match): {person['name']}")
                return person
            
            # Strategy 2: Partial match using ilike with wildcards
            result = self.supabase.table('persons').select('*').ilike('name', f'%{name}%').execute()
            
            if result.data and len(result.data) > 0:
                person = result.data[0]
                print(f"✅ Found person (partial match): {person['name']}")
                return person
            
            # Strategy 3: Try matching individual name parts
            name_parts = name.lower().split()
            for name_part in name_parts:
                if len(name_part) >= 3:  # Only search for meaningful name parts
                    result = self.supabase.table('persons').select('*').ilike('name', f'%{name_part}%').execute()
                    
                    if result.data and len(result.data) > 0:
                        person = result.data[0]
                        print(f"✅ Found person (name part match): {person['name']} for part: '{name_part}'")
                        return person
            
            print(f"❌ Person not found: '{name}'")
            return None
            
        except Exception as e:
            print(f"❌ Error searching person: {str(e)}")
            return None
    
    def find_person_by_roll_number(self, roll_number: str) -> Optional[Dict]:
        """Find a person by roll number"""
        try:
            result = self.supabase.table('persons').select('*').eq('roll_number', roll_number).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Error searching by roll number: {str(e)}")
            return None
    
    def update_person(self, person_id: int, **updates) -> bool:
        """Update person information"""
        try:
            if not updates:
                return False
            
            # Add updated timestamp
            updates['updated_at'] = datetime.now().isoformat()
            
            # Filter only allowed fields
            allowed_fields = ['name', 'roll_number', 'branch', 'email', 'phone', 'updated_at']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            result = self.supabase.table('persons').update(filtered_updates).eq('id', person_id).execute()
            
            if result.data:
                print(f"✅ Updated person ID: {person_id}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error updating person: {str(e)}")
            return False
    
    def add_scan_history(self, person_id: int, scanned_text: str, confidence_score: float = None,
                        document_type: str = None, extracted_data: Dict = None) -> Optional[int]:
        """Add scan history entry"""
        try:
            scan_data = {
                "person_id": person_id,
                "scanned_text": scanned_text,
                "confidence_score": confidence_score,
                "document_type": document_type,
                "scan_timestamp": datetime.now().isoformat(),
                "extracted_data": extracted_data
            }
            
            result = self.supabase.table('scan_history').insert(scan_data).execute()
            
            if result.data and len(result.data) > 0:
                scan_id = result.data[0]['id']
                print(f"✅ Added scan history with ID: {scan_id}")
                return scan_id
            return None
            
        except Exception as e:
            print(f"❌ Error adding scan history: {str(e)}")
            return None
    
    def get_all_persons(self) -> List[Dict]:
        """Get all persons from database"""
        try:
            result = self.supabase.table('persons').select('*').order('created_at', desc=True).execute()
            
            if result.data:
                return result.data
            return []
            
        except Exception as e:
            print(f"❌ Error fetching persons: {str(e)}")
            return []
    
    def get_person_scan_history(self, person_id: int) -> List[Dict]:
        """Get scan history for a specific person"""
        try:
            result = self.supabase.table('scan_history').select('*').eq('person_id', person_id).order('scan_timestamp', desc=True).execute()
            
            if result.data:
                return result.data
            return []
            
        except Exception as e:
            print(f"❌ Error fetching scan history: {str(e)}")
            return []
    
    def search_persons(self, query: str) -> List[Dict]:
        """Search persons by name, roll number, or branch"""
        try:
            results = []
            
            # Search by name
            name_results = self.supabase.table('persons').select('*').ilike('name', f'%{query}%').execute()
            if name_results.data:
                results.extend(name_results.data)
            
            # Search by roll number
            roll_results = self.supabase.table('persons').select('*').ilike('roll_number', f'%{query}%').execute()
            if roll_results.data:
                results.extend(roll_results.data)
            
            # Search by branch
            branch_results = self.supabase.table('persons').select('*').ilike('branch', f'%{query}%').execute()
            if branch_results.data:
                results.extend(branch_results.data)
            
            # Remove duplicates based on ID
            unique_results = []
            seen_ids = set()
            for person in results:
                if person['id'] not in seen_ids:
                    unique_results.append(person)
                    seen_ids.add(person['id'])
            
            return unique_results
            
        except Exception as e:
            print(f"❌ Error searching persons: {str(e)}")
            return []
    
    def delete_person(self, person_id: int) -> bool:
        """Delete a person and their scan history"""
        try:
            # Delete scan history first (foreign key constraint)
            self.supabase.table('scan_history').delete().eq('person_id', person_id).execute()
            
            # Delete person
            result = self.supabase.table('persons').delete().eq('id', person_id).execute()
            
            print(f"✅ Deleted person ID: {person_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting person: {str(e)}")
            return False

# Test function
def test_supabase_connection():
    """Test Supabase connection"""
    try:
        db = SupabaseManager()
        if db.test_connection():
            print("🎉 Supabase is ready!")
            return True
        return False
    except Exception as e:
        print(f"❌ Supabase test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Test connection
    if test_supabase_connection():
        print("\n📋 Don't forget to create tables in Supabase dashboard!")
        db = SupabaseManager()
        print(db.create_tables())
    else:
        print("\n💡 Please check your Supabase credentials in .env file")