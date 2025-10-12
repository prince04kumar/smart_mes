import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

class PostgreSQLManager:
    def __init__(self):
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = os.getenv('POSTGRES_PORT', '5432')
        self.database = os.getenv('POSTGRES_DB', 'smart_campus')
        self.username = os.getenv('POSTGRES_USER', 'postgres')
        self.password = os.getenv('POSTGRES_PASSWORD', 'password')
        
        # Alternative: Full connection URL
        self.database_url = os.getenv('DATABASE_URL')
        
        self.connection = None
        
    def connect(self):
        """Connect to PostgreSQL"""
        try:
            if self.database_url:
                # Use full connection URL (common in cloud deployments)
                self.connection = psycopg2.connect(
                    self.database_url,
                    cursor_factory=RealDictCursor
                )
            else:
                # Use individual parameters
                self.connection = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user=self.username,
                    password=self.password,
                    cursor_factory=RealDictCursor
                )
            
            self.connection.autocommit = True
            print(f"✅ Connected to PostgreSQL: {self.database}")
            self.create_tables()
            return True
        except Exception as e:
            print(f"❌ Failed to connect to PostgreSQL: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from PostgreSQL"""
        if self.connection:
            self.connection.close()
            print("📡 Disconnected from PostgreSQL")
    
    def create_tables(self):
        """Create necessary tables"""
        try:
            cursor = self.connection.cursor()
            
            # Create persons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persons (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    roll_number VARCHAR(100),
                    branch VARCHAR(100),
                    email VARCHAR(255),
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create scan_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scan_history (
                    id SERIAL PRIMARY KEY,
                    person_id INTEGER REFERENCES persons(id),
                    scanned_text TEXT,
                    confidence_score FLOAT,
                    document_type VARCHAR(100),
                    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    extracted_data JSONB
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_persons_name ON persons(name);
                CREATE INDEX IF NOT EXISTS idx_persons_roll_number ON persons(roll_number);
                CREATE INDEX IF NOT EXISTS idx_scan_history_person_id ON scan_history(person_id);
            """)
            
            print("✅ Database tables created/verified")
            
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
    
    def create_person(self, name, roll_number=None, branch=None, email=None, phone=None):
        """Create a new person in the database"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO persons (name, roll_number, branch, email, phone, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            now = datetime.now()
            cursor.execute(query, (name, roll_number, branch, email, phone, now, now))
            
            person_id = cursor.fetchone()['id']
            print(f"✅ Created person: {name} with ID: {person_id}")
            return person_id
            
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
            
            cursor = self.connection.cursor()
            
            # Strategy 1: Exact case-insensitive match
            cursor.execute(
                "SELECT * FROM persons WHERE LOWER(name) = LOWER(%s)",
                (name,)
            )
            person = cursor.fetchone()
            
            if person:
                print(f"✅ Found person (exact match): {person['name']}")
                return dict(person)
            
            # Strategy 2: Partial match using ILIKE
            cursor.execute(
                "SELECT * FROM persons WHERE name ILIKE %s",
                (f"%{name}%",)
            )
            person = cursor.fetchone()
            
            if person:
                print(f"✅ Found person (partial match): {person['name']}")
                return dict(person)
            
            print(f"❌ Person not found: '{name}'")
            return None
            
        except Exception as e:
            print(f"❌ Error searching person: {str(e)}")
            return None
    
    def find_person_by_roll_number(self, roll_number):
        """Find a person by roll number"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM persons WHERE roll_number = %s",
                (roll_number,)
            )
            person = cursor.fetchone()
            
            if person:
                return dict(person)
            return None
            
        except Exception as e:
            print(f"❌ Error searching by roll number: {str(e)}")
            return None
    
    def update_person(self, person_id, **updates):
        """Update person information"""
        try:
            if not updates:
                return False
                
            cursor = self.connection.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for field, value in updates.items():
                if field in ['name', 'roll_number', 'branch', 'email', 'phone']:
                    set_clauses.append(f"{field} = %s")
                    values.append(value)
            
            if not set_clauses:
                return False
            
            set_clauses.append("updated_at = %s")
            values.append(datetime.now())
            values.append(person_id)
            
            query = f"""
                UPDATE persons 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """
            
            cursor.execute(query, values)
            print(f"✅ Updated person ID: {person_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating person: {str(e)}")
            return False
    
    def add_scan_history(self, person_id, scanned_text, confidence_score=None, 
                        document_type=None, extracted_data=None):
        """Add scan history entry"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO scan_history 
                (person_id, scanned_text, confidence_score, document_type, 
                 scan_timestamp, extracted_data)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """
            
            cursor.execute(query, (
                person_id, scanned_text, confidence_score, document_type,
                datetime.now(), json.dumps(extracted_data) if extracted_data else None
            ))
            
            scan_id = cursor.fetchone()['id']
            print(f"✅ Added scan history with ID: {scan_id}")
            return scan_id
            
        except Exception as e:
            print(f"❌ Error adding scan history: {str(e)}")
            return None
    
    def get_all_persons(self):
        """Get all persons from database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM persons ORDER BY created_at DESC")
            persons = cursor.fetchall()
            return [dict(person) for person in persons]
            
        except Exception as e:
            print(f"❌ Error fetching persons: {str(e)}")
            return []

# Test function
def test_postgresql_connection():
    """Test PostgreSQL connection"""
    db = PostgreSQLManager()
    if db.connect():
        print("🎉 PostgreSQL is ready!")
        db.disconnect()
        return True
    return False

if __name__ == "__main__":
    test_postgresql_connection()