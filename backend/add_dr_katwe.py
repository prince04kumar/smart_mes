"""
Add Dr. M.V. Katwe to the database
"""
from supabase_manager import SupabaseManager

def add_dr_katwe():
    """Add Dr. M.V. Katwe to persons table"""
    db = SupabaseManager()
    
    # Connect to database
    if not db.test_connection():
        print("❌ Failed to connect to database")
        return
    
    print("✅ Connected to Supabase database")
    
    # Check if Dr. Katwe already exists
    existing = db.supabase.table('persons').select('*').ilike('name', '%katwe%').execute()
    if existing.data:
        print(f"⚠️ Dr. Katwe already exists in database:")
        for person in existing.data:
            print(f"   ID: {person['id']}, Name: {person['name']}")
        return
    
    # Add Dr. M.V. Katwe
    person_id = db.create_person(
        name="Dr. M.V. Katwe",
        roll_number=None,
        branch="ECE",
        email="mv.katwe@nitrr.ac.in",
        phone=None
    )
    
    if person_id:
        print(f"✅ Successfully added Dr. M.V. Katwe to database (ID: {person_id})")
        print(f"   Branch: ECE")
        print(f"   Email: mv.katwe@nitrr.ac.in")
    else:
        print("❌ Failed to add Dr. M.V. Katwe")

if __name__ == "__main__":
    add_dr_katwe()
