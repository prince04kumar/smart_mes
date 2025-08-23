from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
import base64
import io
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize AWS Textract client
textract = boto3.client("textract", region_name="us-east-1")

@app.route('/health', methods=['GET'])
def health_check():
    print("Health check endpoint called")
    return jsonify({"status": "healthy", "message": "Flask server is running"})

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
        
        print("Sending to AWS Textract...")
        # Analyze document with AWS Textract
        response = textract.analyze_document(
            Document={"Bytes": image_bytes},
            FeatureTypes=["QUERIES", "FORMS", "TABLES"],
            QueriesConfig={
                "Queries": [
                    {"Text": "What is the name?", "Alias": "StudentName"},
                    {"Text": "What is the student name?", "Alias": "StudentName2"},
                    {"Text": "What is the roll number?", "Alias": "RollNumber"},
                    {"Text": "What is the enrollment number?", "Alias": "EnrollmentNumber"},
                    {"Text": "What is the department?", "Alias": "Branch"},
                    {"Text": "What is the branch?", "Alias": "Branch2"},
                    {"Text": "What is the contact number?", "Alias": "ContactNumber"},
                    {"Text": "What is the phone number?", "Alias": "Phone"},
                    {"Text": "What is the date of birth?", "Alias": "DateOfBirth"},
                    {"Text": "What is the blood group?", "Alias": "BloodGroup"},
                ]
            }
        )

        print("AWS Textract response received")
        print(f"Total blocks found: {len(response.get('Blocks', []))}")
        
        # Debug: Print all blocks to understand what Textract found
        print("=== All Textract Blocks ===")
        for i, block in enumerate(response.get("Blocks", [])):
            if block["BlockType"] in ["QUERY", "QUERY_RESULT"]:
                print(f"Block {i}: {block['BlockType']} - {block.get('Text', 'No text')} - Query: {block.get('Query', {})}")

        # Extract results
        results = {}
        all_text = []
        
        # First, let's see all the text Textract found
        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                all_text.append(block.get("Text", ""))
        
        print("=== All Text Found by Textract ===")
        for i, text in enumerate(all_text):
            print(f"Line {i}: {text}")
        print("================================")
        
        # Now extract query results
        for block in response["Blocks"]:
            if block["BlockType"] == "QUERY_RESULT":
                query_info = block.get("Query", {})
                alias = query_info.get("Alias", "Unknown")
                text = block.get("Text", "Not found")
                confidence = block.get("Confidence", 0)
                results[alias] = {
                    "value": text,
                    "confidence": round(confidence, 2)
                }

        print("Upload Results:", results)
        return jsonify({
            "success": True,
            "data": results,
            "all_text": all_text,
            "total_lines": len(all_text),
            "message": "ID card analyzed successfully"
        })

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
        if 'image' not in data:
            print("Error: No image data in request")
            return jsonify({"error": "No image data provided"}), 400

        print("Processing webcam image...")
        # Decode base64 image
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64, prefix
        image_bytes = base64.b64decode(image_data)
        print(f"Decoded image size: {len(image_bytes)} bytes")
        
        print("Sending to AWS Textract...")
        # Analyze document with AWS Textract
        response = textract.analyze_document(
            Document={"Bytes": image_bytes},
            FeatureTypes=["QUERIES", "FORMS", "TABLES"],
            QueriesConfig={
                "Queries": [
                    {"Text": "What is the name?", "Alias": "StudentName"},
                    {"Text": "What is the student name?", "Alias": "StudentName2"},
                    {"Text": "What is the roll number?", "Alias": "RollNumber"},
                    {"Text": "What is the enrollment number?", "Alias": "EnrollmentNumber"},
                    {"Text": "What is the department?", "Alias": "Branch"},
                    {"Text": "What is the branch?", "Alias": "Branch2"},
                    {"Text": "What is the contact number?", "Alias": "ContactNumber"},
                    {"Text": "What is the phone number?", "Alias": "Phone"},
                    {"Text": "What is the date of birth?", "Alias": "DateOfBirth"},
                    {"Text": "What is the blood group?", "Alias": "BloodGroup"},
                ]
            }
        )

        print("AWS Textract response received")
        
        # Extract results
        results = {}
        all_text = []
        
        # First, let's see all the text Textract found
        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                all_text.append(block.get("Text", ""))
        
        print("=== All Text Found by Textract (Webcam) ===")
        for i, text in enumerate(all_text):
            print(f"Line {i}: {text}")
        print("==========================================")
        
        # Now extract query results
        for block in response["Blocks"]:
            if block["BlockType"] == "QUERY_RESULT":
                query_info = block.get("Query", {})
                alias = query_info.get("Alias", "Unknown")
                text = block.get("Text", "Not found")
                confidence = block.get("Confidence", 0)
                results[alias] = {
                    "value": text,
                    "confidence": round(confidence, 2)
                }
        print("Webcam Results:", results)
        return jsonify({
            "success": True,
            "data": results,
            "all_text": all_text,
            "total_lines": len(all_text),
            "message": "Webcam image analyzed successfully"
        })

    except Exception as e:
        print(f"Error in analyze_webcam: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Error analyzing webcam image"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
