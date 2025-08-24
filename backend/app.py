from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import base64
import time
import io
from PIL import Image
import numpy as np
import cv2
from database import db_manager
from messaging import message_service
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize AWS Textract client
textract = boto3.client("textract", region_name="us-east-1")

@app.route('/health', methods=['GET'])
def health_check():
    print("Health check endpoint called")
    # Check database connection
    db_status = "connected" if db_manager.client else "disconnected"
    return jsonify({
        "status": "healthy", 
        "message": "Flask server is running",
        "database": db_status
    })

@app.route('/analyze-id', methods=['POST'])
def analyze_id_card():
    print("=== Analyze ID Card Request Received ===")
    try:
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

        # Store image in Redis cache
        from cache_service import cache_service
        cache_key = f"scan:{file.filename}:{int(time.time())}"
        cache_service.set_document(cache_key, image_bytes)

        print("Sending to AWS Textract...")
        # Analyze document with AWS Textract - same as textract2.py
        response = textract.analyze_document(
            Document={"Bytes": image_bytes},
            FeatureTypes=["QUERIES"],
            QueriesConfig={
                "Queries": [
                    {"Text": "What is the student's name on the ID card?", "Alias": "StudentName"},
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

        # Send notification if person is identified
        if person_identified and person_data:
            print(f"🎯 FINAL PERSON IDENTIFIED: {person_data['name']}")
            # Add scan history
            scan_data = {
                "source": "upload",
                "extracted_data": results,
                "file_name": file.filename
            }
            db_manager.add_scan_history(person_data['_id'], scan_data)
            # Send notification - use email if configured, fallback to console
            smtp_enabled = all([
                os.getenv('SMTP_ENABLED', 'false').lower() == 'true',
                os.getenv('SMTP_HOST'),
                os.getenv('SMTP_EMAIL'),
                os.getenv('SMTP_PASSWORD')
            ])
            # Retrieve image from Redis for attachment
            attachment_bytes = cache_service.get_document(cache_key)
            notification_sent = message_service.send_identification_message(
                person_data,
                results,
                method="email" if smtp_enabled else "console",
                attachment_bytes=attachment_bytes,
                attachment_filename=file.filename
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
                "branch": person_data.get('branch') if person_data else None
            } if person_data else None,
            "notification_sent": notification_sent,
            "message": "ID card analyzed successfully"
        })
    except Exception as e:
        print(f"Error in analyze_id_card: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error analyzing ID card"
        }), 500

    except Exception as e:
        print(f"Error in analyze_id_card: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error analyzing ID card"
        }), 500

@app.route('/analyze-webcam', methods=['POST'])
def analyze_webcam():
    print("=== Analyze Webcam Request Received ===")
    try:
        # Get base64 image from request
        data = request.get_json()
        try:
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

            # Store webcam image in Redis cache
            from cache_service import cache_service
            cache_key = f"scan:webcam:{int(time.time())}.jpg"
            cache_service.set_document(cache_key, image_bytes)

            print("Sending to AWS Textract...")
            # Analyze document with AWS Textract - same as textract2.py
            response = textract.analyze_document(
                Document={"Bytes": image_bytes},
                FeatureTypes=["QUERIES"],
                QueriesConfig={
                    "Queries": [
                        {"Text": "What is the student's name on the ID card?", "Alias": "StudentName"},
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

            # Send notification if person is identified
            if person_identified and person_data:
                print(f"🎯 FINAL PERSON IDENTIFIED: {person_data['name']}" )
                # Add scan history
                scan_data = {
                    "source": "webcam",
                    "extracted_data": results
                }
                db_manager.add_scan_history(person_data['_id'], scan_data)
                # Send notification - use email if configured, fallback to console
                smtp_enabled = all([
                    os.getenv('SMTP_ENABLED', 'false').lower() == 'true',
                    os.getenv('SMTP_HOST'),
                    os.getenv('SMTP_EMAIL'),
                    os.getenv('SMTP_PASSWORD')
                ])
                # Retrieve image from Redis for attachment
                attachment_bytes = cache_service.get_document(cache_key)
                notification_sent = message_service.send_identification_message(
                    person_data,
                    results,
                    method="email" if smtp_enabled else "console",
                    attachment_bytes=attachment_bytes,
                    attachment_filename=f"webcam_scan_{int(time.time())}.jpg"
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
                    "branch": person_data.get('branch') if person_data else None
                } if person_data else None,
                "notification_sent": notification_sent,
                "message": "Webcam image analyzed successfully"
            })
        except Exception as e:
            print(f"Error in analyze_webcam: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "Error analyzing webcam image"
            }), 500

    except Exception as e:
        print(f"Error in analyze_webcam: {str(e)}")
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
        # Convert ObjectId to string for JSON serialization
        for person in persons:
            person['_id'] = str(person['_id'])
        
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
                "data": {"person_id": str(person_id)},
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
        db_manager.setup_sample_data()
        return jsonify({
            "success": True,
            "message": "Sample data setup completed"
        })
    except Exception as e:
        print(f"Error setting up sample data: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error setting up sample data"
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

if __name__ == '__main__':
    # Initialize database connection
    if db_manager.connect():
        print("🚀 Setting up sample data...")
        db_manager.setup_sample_data()
    else:
        print("⚠️ Running without database connection")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
