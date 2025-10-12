"""
Setup script for Supabase database tables
This script creates the required tables for Smart Campus application
"""

from supabase_manager import SupabaseManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_supabase_tables():
    """Create tables in Supabase using SQL commands"""
    
    print("🚀 Setting up Supabase database for Smart Campus...")
    
    try:
        db = SupabaseManager()
        
        # Table creation SQL
        create_persons_table = """
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
        """
        
        create_scan_history_table = """
        CREATE TABLE IF NOT EXISTS scan_history (
            id SERIAL PRIMARY KEY,
            person_id INTEGER REFERENCES persons(id) ON DELETE CASCADE,
            scanned_text TEXT,
            confidence_score FLOAT,
            document_type VARCHAR(100),
            scan_timestamp TIMESTAMP DEFAULT NOW(),
            extracted_data JSONB
        );
        """
        
        create_indexes = """
        CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);
        CREATE INDEX IF NOT EXISTS idx_persons_roll_number ON persons(roll_number);
        CREATE INDEX IF NOT EXISTS idx_scan_history_person_id ON scan_history(person_id);
        """
        
        # Execute SQL using Supabase RPC (if available) or provide manual instructions
        print("\n📋 Please run these SQL commands in your Supabase SQL Editor:")
        print("=" * 70)
        print("1. Go to your Supabase dashboard: https://app.supabase.com")
        print("2. Select your project")
        print("3. Go to SQL Editor")
        print("4. Copy and paste the following SQL commands:")
        print("=" * 70)
        
        print("\n-- Create persons table")
        print(create_persons_table)
        
        print("\n-- Create scan_history table")
        print(create_scan_history_table)
        
        print("\n-- Create indexes for better performance")
        print(create_indexes)
        
        print("\n-- Enable Row Level Security (Optional)")
        print("""
        ALTER TABLE persons ENABLE ROW LEVEL SECURITY;
        ALTER TABLE scan_history ENABLE ROW LEVEL SECURITY;

        -- Create policies for public access (adjust as needed)
        CREATE POLICY "Enable all operations for anon users" ON persons
            FOR ALL USING (true);

        CREATE POLICY "Enable all operations for anon users" ON scan_history
            FOR ALL USING (true);
        """)
        
        print("=" * 70)
        print("5. Click 'Run' to execute the SQL")
        print("6. After running the SQL, test the connection again")
        print("=" * 70)
        
        # Try to create a test record to verify setup
        print("\n🧪 After creating tables, run this command to test:")
        print("python test_supabase_full.py")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")

def test_table_creation():
    """Test if tables are created and working"""
    try:
        db = SupabaseManager()
        
        # Test creating a person
        person_id = db.create_person(
            name="Test Student",
            roll_number="TEST001",
            branch="Computer Science",
            email="test@example.com"
        )
        
        if person_id:
            print("✅ Successfully created test person!")
            
            # Test finding the person
            found_person = db.find_person_by_name("Test Student")
            if found_person:
                print("✅ Successfully found test person!")
                
                # Test adding scan history
                scan_id = db.add_scan_history(
                    person_id=person_id,
                    scanned_text="Test document scan",
                    confidence_score=95.5,
                    document_type="ID Card"
                )
                
                if scan_id:
                    print("✅ Successfully added scan history!")
                    print("\n🎉 Supabase database is fully functional!")
                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔧 Supabase Database Setup")
    print("=" * 50)
    
    create_supabase_tables()
    
    print("\n" + "=" * 50)
    print("💡 After running the SQL commands in Supabase dashboard,")
    print("   run 'python test_supabase_full.py' to verify everything works!")