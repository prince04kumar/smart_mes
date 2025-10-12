from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import base64
import time
import io
from PIL import Image
import numpy as np
import cv2
from supabase_manager import SupabaseManager
from supabase_user_manager import SupabaseUserManager
from messaging import message_service
from supabase_auth_middleware import require_auth, optional_auth, get_current_user
import os
from datetime import datetime
import io
from PIL import Image

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Supabase database manager
db_manager = SupabaseManager()

# Initialize Supabase user manager
user_manager = SupabaseUserManager()

# Initialize AWS Textract client
textract = boto3.client("textract", region_name="us-east-1")

def convert_to_jpeg(image_bytes):
    """Convert image bytes to JPEG format"""
    try:
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background for transparent images
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save as JPEG to BytesIO with high quality
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=95, optimize=True)
        jpeg_bytes = output.getvalue()
        
        print(f"✅ Image converted to JPEG. Original: {len(image_bytes)} bytes, JPEG: {len(jpeg_bytes)} bytes")
        return jpeg_bytes
        
    except Exception as e:
        print(f"⚠️ Could not convert to JPEG: {e}. Using original bytes.")
        return image_bytes

@app.route('/health', methods=['GET'])
def health_check():
    print("Health check endpoint called")
    # Check database connection
    try:
        db_status = "connected" if db_manager.test_connection() else "disconnected"
    except:
        db_status = "disconnected"
    return jsonify({
        "status": "healthy", 
        "message": "Flask server is running",
        "database": db_status,
        "database_type": "Supabase"
    })

# Authentication Routes
@app.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        organization = data.get('organization', '').strip()
        
        if not email or not password or not name:
            return jsonify({"error": "Email, password, and name are required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters long"}), 400
        
        result = user_manager.create_user(email, password, name, organization)
        
        if result['success']:
            return jsonify({
                "success": True,
                "message": result['message'],
                "user_id": result['user_id']
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": result['message']
            }), 400
            
    except Exception as e:
        print(f"Error in register: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        result = user_manager.authenticate_user(email, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify({
                "success": False,
                "error": result['message']
            }), 401
            
    except Exception as e:
        print(f"Error in login: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        result = user_manager.get_user_by_id(user_id)
        
        if result['success']:
            return jsonify({
                "success": True,
                "user": result['user']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['message']
            }), 404
            
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/update-email-settings', methods=['POST'])
@require_auth
def update_email_settings():
    """Update user's email settings"""
    try:
        data = request.get_json()
        current_user = get_current_user()
        user_id = current_user['user_id']
        
        smtp_settings = {
            "smtp_host": data.get('smtp_host'),
            "smtp_port": data.get('smtp_port', 587),
            "smtp_email": data.get('smtp_email'),
            "smtp_password": data.get('smtp_password'),
            "smtp_enabled": data.get('smtp_enabled', False)
        }
        
        result = user_manager.update_email_settings(user_id, smtp_settings)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error updating email settings: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/analyze-id', methods=['POST'])
@optional_auth  # Make it optional for backward compatibility, but track user if logged in
def analyze_id_card():
    print("=== Analyze Doc Request Received ===")
    try:
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user['user_id'] if current_user else None
        
        # Increment user's scan count if authenticated
        if user_id:
            user_manager.increment_scan_count(user_id)
        # Get the uploaded file
        if 'image' not in request.files:
            print("Error: No image file in request")
            return jsonify({"error": "No image file provided"}), 400
        file = request.files['image']
        if file.filename == '':
            print("Error: No file selected")
            return jsonify({"error": "No file selected"}), 400

        print(f"Processing file: {file.filename}")
        # Read image file
        image_bytes = file.read()
        print(f"Image size: {len(image_bytes)} bytes")
        
        # Convert to JPEG format for email compatibility
        jpeg_bytes = convert_to_jpeg(image_bytes)

        # Store JPEG image in Redis cache
        from cache_service import cache_service
        # Ensure cache key has .jpg extension
        base_filename = file.filename.rsplit('.', 1)[0] if '.' in file.filename else file.filename
        cache_key = f"scan:{base_filename}.jpg:{int(time.time())}"
        cache_service.set_document(cache_key, jpeg_bytes)

        print("Sending to AWS Textract...")
        # Analyze document with AWS Textract - same as textract2.py
        response = textract.analyze_document(
            Document={"Bytes": jpeg_bytes},
            FeatureTypes=["QUERIES"],
            QueriesConfig={
                "Queries": [
                    {"Text": "What is the student's name on the Doc?", "Alias": "StudentName"},
                    # {"Text": "What is the roll number?", "Alias": "RollNumber"},
                    # {"Text": "What is the branch?", "Alias": "Branch"},
                ]
            }
        )

        print("AWS Textract response received")

        # Print results exactly like textract2.py
        print("----- Scan Result -----")
        results = {}
        for block in response["Blocks"]:
            if block["BlockType"] == "QUERY_RESULT":
                query_info = block.get("Query", {})
                alias = query_info.get("Alias", "Unknown")
                text = block.get("Text", "")
                print(f"{alias}: {text}")
                # Also prepare for JSON response
                results[alias] = {
                    "value": text,
                    "confidence": round(block.get("Confidence", 0), 2)
                }
        print("-----------------------")

        print("Upload Results:", results)

        # 🔍 IMPROVED PERSON IDENTIFICATION AND NOTIFICATION
        person_identified = False
        person_data = None
        notification_sent = False

        # Extract all possible names from results (including Unknown alias)
        possible_names = []

        # Check StudentName alias
        student_name = results.get('StudentName', {}).get('value', '').strip()
        if student_name and student_name.lower() not in ['not found', '', 'none']:
            possible_names.append(student_name)

        # Check Unknown alias (sometimes Textract puts names here)
        unknown_value = results.get('Unknown', {}).get('value', '').strip()
        if unknown_value and unknown_value.lower() not in ['not found', '', 'none']:
            possible_names.append(unknown_value)

        # Try to find person by any possible name
        print(f"🔍 Trying to identify person from possible names: {possible_names}")
        for name in possible_names:
            person_data = db_manager.find_person_by_name(name)
            if person_data:
                person_identified = True
                print(f"🎯 Successfully identified by name: '{name}' -> {person_data['name']}")
                break

        # If not found by name, try by roll number
        if not person_identified:
            roll_number = results.get('RollNumber', {}).get('value', '').strip()
            if roll_number and roll_number.lower() not in ['not found', '', 'none']:
                person_data = db_manager.find_person_by_roll_number(roll_number)
                if person_data:
                    person_identified = True
                    print(f"🎯 Successfully identified by roll number: {roll_number}")

        # Check if email is configured (initialize before conditional blocks)
        smtp_enabled = all([
            os.getenv('SMTP_ENABLED', 'false').lower() == 'true',
            os.getenv('SMTP_HOST'),
            os.getenv('SMTP_EMAIL'),
            os.getenv('SMTP_PASSWORD')
        ])

        # Send notification if person is identified
        if person_identified and person_data:
            print(f"🎯 FINAL PERSON IDENTIFIED: {person_data['name']}")
            # Add scan history with user context
            scan_data = {
                "source": "upload",
                "extracted_data": results,
                "file_name": file.filename,
                "scanned_by_user": user_id,
                "scanned_at": datetime.now().isoformat()
            }
            db_manager.add_scan_history(
                person_id=person_data['id'], 
                scanned_text=f"Upload scan: {file.filename}",
                confidence_score=results.get('StudentName', {}).get('confidence', 0),
                document_type="Upload",
                extracted_data=scan_data
            )
            
            # Only send console notification for now - email will be sent via separate endpoint
            notification_sent = message_service.send_identification_message(
                person_data,
                results,
                method="console"
            )
        else:
            print(f"❓ PERSON NOT FOUND in database. Tried names: {possible_names}")

        return jsonify({
            "success": True,
            "data": results,
            "person_identified": person_identified,
            "person_data": {
                "name": person_data.get('name') if person_data else None,
                "email": person_data.get('email') if person_data else None,
                "roll_number": person_data.get('roll_number') if person_data else None,
                "branch": person_data.get('branch') if person_data else None,
                "person_id": person_data.get('id') if person_data else None
            } if person_data else None,
            "notification_sent": notification_sent,
            "message": "Doc analyzed successfully",
            "cache_key": cache_key if person_identified else None,
            "smtp_enabled": smtp_enabled,
            "scanned_by": {
                "user_id": user_id,
                "email": current_user['email'] if current_user else None,
                "name": current_user['name'] if current_user else None
            } if current_user else None
        })
    except Exception as e:
        print(f"Error in analyze_id_card: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error analyzing Doc"
        }), 500

@app.route('/analyze-webcam', methods=['POST'])
@optional_auth
def analyze_webcam():
    print("=== Analyze Webcam Request Received ===")
    try:
        # Get current user if authenticated
        current_user = get_current_user()
        user_id = current_user['user_id'] if current_user else None
        
        # Increment user's scan count if authenticated
        if user_id:
            user_manager.increment_scan_count(user_id)
        # Get base64 image from request
        data = request.get_json()
        if 'image' not in data:
            print("Error: No image data in request")
            return jsonify({"error": "No image data provided"}), 400

        print("Processing webcam image...")
        # Decode base64 image
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        print(f"Decoded image size: {len(image_bytes)} bytes")
        
        # Convert to JPEG format for email compatibility
        jpeg_bytes = convert_to_jpeg(image_bytes)

        # Store JPEG webcam image in Redis cache
        from cache_service import cache_service
        cache_key = f"scan:webcam:{int(time.time())}.jpg"
        cache_service.set_document(cache_key, jpeg_bytes)

        print("Sending to AWS Textract...")
        # Analyze document with AWS Textract - same as textract2.py
        response = textract.analyze_document(
            Document={"Bytes": jpeg_bytes},
            FeatureTypes=["QUERIES"],
            QueriesConfig={
                "Queries": [
                    {"Text": "What is the student's name on the Doc?", "Alias": "StudentName"},
                    {"Text": "What is the roll number?", "Alias": "RollNumber"},
                    {"Text": "What is the branch?", "Alias": "Branch"},
                ]
            }
        )

        print("AWS Textract response received")

        # Print results exactly like textract2.py
        print("----- Scan Result -----")
        results = {}
        for block in response["Blocks"]:
            if block["BlockType"] == "QUERY_RESULT":
                query_info = block.get("Query", {})
                alias = query_info.get("Alias", "Unknown")
                text = block.get("Text", "")
                print(f"{alias}: {text}")
                # Also prepare for JSON response
                results[alias] = {
                    "value": text,
                    "confidence": round(block.get("Confidence", 0), 2)
                }
        print("-----------------------")

        print("Webcam Results:", results)

        # 🔍 IMPROVED PERSON IDENTIFICATION AND NOTIFICATION
        person_identified = False
        person_data = None
        notification_sent = False

        # Extract all possible names from results (including Unknown alias)
        possible_names = []

        # Check StudentName alias
        student_name = results.get('StudentName', {}).get('value', '').strip()
        if student_name and student_name.lower() not in ['not found', '', 'none']:
            possible_names.append(student_name)

        # Check Unknown alias (sometimes Textract puts names here)
        unknown_value = results.get('Unknown', {}).get('value', '').strip()
        if unknown_value and unknown_value.lower() not in ['not found', '', 'none']:
            possible_names.append(unknown_value)

        # Try to find person by any possible name
        print(f"🔍 Trying to identify person from possible names: {possible_names}")
        for name in possible_names:
            person_data = db_manager.find_person_by_name(name)
            if person_data:
                person_identified = True
                print(f"🎯 Successfully identified by name: '{name}' -> {person_data['name']}")
                break

        # If not found by name, try by roll number
        if not person_identified:
            roll_number = results.get('RollNumber', {}).get('value', '').strip()
            if roll_number and roll_number.lower() not in ['not found', '', 'none']:
                person_data = db_manager.find_person_by_roll_number(roll_number)
                if person_data:
                    person_identified = True
                    print(f"🎯 Successfully identified by roll number: {roll_number}")

        # Check if email is configured
        smtp_enabled = all([
            os.getenv('SMTP_ENABLED', 'false').lower() == 'true',
            os.getenv('SMTP_HOST'),
            os.getenv('SMTP_EMAIL'),
            os.getenv('SMTP_PASSWORD')
        ])

        # Send notification if person is identified
        if person_identified and person_data:
            print(f"🎯 FINAL PERSON IDENTIFIED: {person_data['name']}" )
            # Add scan history
            scan_data = {
                "source": "webcam",
                "extracted_data": results,
                "scanned_at": datetime.now().isoformat()
            }
            db_manager.add_scan_history(
                person_id=person_data['id'], 
                scanned_text="Webcam scan",
                confidence_score=results.get('StudentName', {}).get('confidence', 0),
                document_type="Webcam",
                extracted_data=scan_data
            )
            
            # Only send console notification for now - email will be sent via separate endpoint
            notification_sent = message_service.send_identification_message(
                person_data,
                results,
                method="console"
            )
        else:
            print(f"❓ PERSON NOT FOUND in database. Tried names: {possible_names}")

        return jsonify({
            "success": True,
            "data": results,
            "person_identified": person_identified,
            "person_data": {
                "name": person_data.get('name') if person_data else None,
                "email": person_data.get('email') if person_data else None,
                "roll_number": person_data.get('roll_number') if person_data else None,
                "branch": person_data.get('branch') if person_data else None,
                "person_id": person_data.get('id') if person_data else None
            } if person_data else None,
            "notification_sent": notification_sent,
            "message": "Webcam image analyzed successfully",
            "cache_key": cache_key if person_identified else None,
            "smtp_enabled": smtp_enabled
        })

    except Exception as e:
        print(f"Error in analyze_webcam: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error analyzing webcam image"
        }), 500

@app.route('/persons', methods=['GET'])
def get_all_persons():
    """Get all persons in the database"""
    try:
        persons = db_manager.get_all_persons()
        # No need to convert IDs - Supabase returns standard integers
        
        return jsonify({
            "success": True,
            "data": persons,
            "count": len(persons),
            "message": "Persons retrieved successfully"
        })
    except Exception as e:
        print(f"Error getting persons: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving persons"
        }), 500

@app.route('/persons', methods=['POST'])
def create_person():
    """Create a new person in the database"""
    try:
        data = request.get_json()
        
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}",
                    "message": "Invalid input data"
                }), 400
        
        person_id = db_manager.create_person(
            name=data['name'],
            roll_number=data.get('roll_number'),
            branch=data.get('branch'),
            email=data.get('email'),
            phone=data.get('phone')
        )
        
        if person_id:
            return jsonify({
                "success": True,
                "data": {"person_id": person_id},
                "message": "Person created successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Failed to create person",
                "message": "Database error"
            }), 500
            
    except Exception as e:
        print(f"Error creating person: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error creating person"
        }), 500

@app.route('/setup-sample-data', methods=['POST'])
def setup_sample_data():
    """Setup sample data in the database"""
    try:
        # Create sample students
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
            person_id = db_manager.create_person(**student)
            if person_id:
                created_count += 1
        
        return jsonify({
            "success": True,
            "message": f"Sample data setup completed. Created {created_count} students."
        })
    except Exception as e:
        print(f"Error setting up sample data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error setting up sample data"
        }), 500

@app.route('/send-notification-email', methods=['POST'])
def send_notification_email():
    """Send email notification to identified person with scanned document"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        person_id = data.get('person_id')
        cache_key = data.get('cache_key')
        scan_results = data.get('scan_results', {})
        
        if not person_id or not cache_key:
            return jsonify({"error": "Missing person_id or cache_key"}), 400
        
        # Get person data from database
        person_data = db_manager.supabase.table('persons').select('*').eq('id', person_id).execute()
        person_data = person_data.data[0] if person_data.data else None
        
        if not person_data:
            return jsonify({"error": "Person not found in database"}), 404
            
        if not person_data.get('email'):
            return jsonify({"error": f"No email address found for {person_data.get('name', 'Unknown')}"}), 400
        
        # Retrieve scanned document from Redis cache
        from cache_service import cache_service
        attachment_bytes = cache_service.get_document(cache_key)
        
        if not attachment_bytes:
            return jsonify({"error": "Scanned document not found in cache"}), 404
        
        # Determine filename based on cache key
        if 'webcam' in cache_key:
            filename = f"webcam_scan_{person_data.get('name', 'unknown').replace(' ', '_')}.jpg"
        else:
            filename = cache_key.split(':')[-1] if ':' in cache_key else "scanned_document.jpg"
        
        # Send email with attachment
        success = message_service.send_identification_message(
            person_data,
            scan_results,
            method="email",
            attachment_bytes=attachment_bytes,
            attachment_filename=filename
        )
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Email sent successfully to {person_data['name']} ({person_data['email']})"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to send email"
            }), 500
            
    except Exception as e:
        print(f"Error sending notification email: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error sending notification email"
        }), 500

@app.route('/test-email', methods=['POST'])
def test_email():
    """Test email configuration"""
    try:
        data = request.get_json() or {}
        test_email = data.get('email')
        
        result = message_service.test_email_configuration(test_email)
        
        return jsonify({
            "success": result,
            "message": "Email test completed" if result else "Email test failed",
            "email_status": message_service.get_email_status()
        })
    except Exception as e:
        print(f"Error testing email: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error testing email configuration"
        }), 500

@app.route('/email-status', methods=['GET'])
def get_email_status():
    """Get email configuration status"""
    try:
        return jsonify({
            "success": True,
            "data": message_service.get_email_status(),
            "message": "Email status retrieved successfully"
        })
    except Exception as e:
        print(f"Error getting email status: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving email status"
        }), 500

@app.route('/persons-list', methods=['GET'])
def get_persons_list():
    """Get all persons from database (alternative endpoint)"""
    try:
        persons = db_manager.get_all_persons()
        # No need to convert IDs - Supabase returns standard integers
        
        return jsonify({
            "success": True,
            "persons": persons,
            "count": len(persons)
        })
    except Exception as e:
        print(f"Error getting persons: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error retrieving persons"
        }), 500

@app.route('/create-person', methods=['POST'])
def create_person_endpoint():
    """Create a new person in the database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if not data.get('name', '').strip():
            return jsonify({"error": "Name is required"}), 400
        
        # Create person
        person_id = db_manager.create_person(
            name=data.get('name', '').strip(),
            roll_number=data.get('roll_number', '').strip() or None,
            branch=data.get('branch', '').strip() or None,
            email=data.get('email', '').strip() or None,
            phone=data.get('phone', '').strip() or None
        )
        
        if person_id:
            return jsonify({
                "success": True,
                "message": f"Person '{data['name']}' created successfully",
                "person_id": str(person_id)
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to create person"
            }), 500
            
    except Exception as e:
        print(f"Error creating person: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error creating person"
        }), 500

if __name__ == '__main__':
    # Test Supabase connection
    try:
        if db_manager.test_connection():
            print("🚀 Supabase database connected successfully!")
            # Initialize user manager
            user_manager.connect()
            print("👤 User management system initialized")
        else:
            print("⚠️ Running without database connection")
    except Exception as e:
        print(f"⚠️ Database connection error: {e}")
        print("⚠️ Running without database connection")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
