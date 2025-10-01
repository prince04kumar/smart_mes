#!/usr/bin/env python3
"""Script to add Prince Kumar to the database"""

import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def add_prince_kumar():
    """Add Prince Kumar to the database"""
    
    # Connect to database
    if not db_manager.connect():
        print("❌ Failed to connect to database")
        return False
    
    # Check if Prince Kumar already exists
    existing_person = db_manager.find_person_by_name("Prince Kumar")
    if existing_person:
        print(f"⚠️ Prince Kumar already exists in database with ID: {existing_person['_id']}")
        print(f"📋 Current details: {existing_person}")
        return True
    
    # Create Prince Kumar with provided details
    person_id = db_manager.create_person(
        name="Prince Kumar",
        roll_number="23116076", 
        branch="ECE",
        email="princesocial04@gmail.com",
        phone="7307567443"
    )
    
    if person_id:
        print(f"✅ Successfully added Prince Kumar to database!")
        print(f"📋 Details:")
        print(f"   Name: Prince Kumar")
        print(f"   Roll Number: 23116076")
        print(f"   Branch: ECE")
        print(f"   Email: princesocial04@gmail.com")
        print(f"   Phone: 7307567443")
        print(f"   Database ID: {person_id}")
        return True
    else:
        print("❌ Failed to add Prince Kumar to database")
        return False

if __name__ == "__main__":
    add_prince_kumar()
    db_manager.disconnect()