import cv2
import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
import json

# Load environment variables from .env file
load_dotenv()

class TextractProcessor:
    def __init__(self):
        """Initialize AWS Textract client using environment variables"""
        try:
            # AWS Textract client - automatically uses environment variables
            self.textract_client = boto3.client(
                'textract',
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            print("✅ AWS Textract client initialized successfully")
        except NoCredentialsError:
            print("❌ AWS credentials not found. Please check your .env file.")
            raise
        except Exception as e:
            print(f"❌ Error initializing Textract: {str(e)}")
            raise

    def process_document(self, file_path):
        """Process document from file path"""
        try:
            with open(file_path, 'rb') as document:
                document_bytes = document.read()
            
            return self.process_document_bytes(document_bytes)
            
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            raise
        except Exception as e:
            print(f"❌ Error processing document: {str(e)}")
            raise

    def process_document_bytes(self, document_bytes):
        """Process document from bytes (for camera capture)"""
        try:
            # Check file size (max 10MB for synchronous processing)
            if len(document_bytes) > 10 * 1024 * 1024:
                raise ValueError("Document too large. Maximum size: 10MB")
            
            # Use analyze_document for better structure detection
            response = self.textract_client.analyze_document(
                Document={'Bytes': document_bytes},
                FeatureTypes=['QUERIES'],
                QueriesConfig={
                    "Queries": [
                        {"Text": "What is the student's name on the document?", "Alias": "StudentName"},
                        {"Text": "What is the roll number or ID number?", "Alias": "RollNumber"},
                        {"Text": "What is the branch or department?", "Alias": "Branch"},
                        {"Text": "What is the grade or GPA?", "Alias": "Grade"},
                        {"Text": "What is the year or semester?", "Alias": "Year"}
                    ]
                }
            )
            
            return self.extract_data_from_response(response)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidParameterException':
                print("❌ Invalid document format. Supported: PDF, PNG, JPEG")
            elif error_code == 'DocumentTooLargeException':
                print("❌ Document too large. Max size: 10MB")
            elif error_code == 'UnsupportedDocumentException':
                print("❌ Unsupported document type")
            else:
                print(f"❌ AWS Error: {e}")
            raise
        except Exception as e:
            print(f"❌ Textract processing error: {str(e)}")
            raise

    def extract_data_from_response(self, response):
        """Extract structured data from Textract response"""
        extracted_data = {
            'full_text': '',
            'query_results': {},
            'confidence_scores': [],
            'raw_lines': []
        }
        
        # Process all blocks
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
                text = block['Text']
                confidence = block.get('Confidence', 0)
                
                extracted_data['full_text'] += text + '\n'
                extracted_data['raw_lines'].append({
                    'text': text,
                    'confidence': confidence
                })
                extracted_data['confidence_scores'].append(confidence)
            
            elif block['BlockType'] == 'QUERY_RESULT':
                query_info = block.get('Query', {})
                alias = query_info.get('Alias', 'Unknown')
                text = block.get('Text', 'Not found')
                confidence = block.get('Confidence', 0)
                
                extracted_data['query_results'][alias] = {
                    'text': text,
                    'confidence': confidence
                }
        
        # Calculate average confidence
        if extracted_data['confidence_scores']:
            avg_confidence = sum(extracted_data['confidence_scores']) / len(extracted_data['confidence_scores'])
            extracted_data['average_confidence'] = avg_confidence
        else:
            extracted_data['average_confidence'] = 0
        
        return extracted_data

    def test_connection(self):
        """Test AWS Textract connection"""
        try:
            # Simple test to verify credentials
            response = self.textract_client.list_adapters(MaxResults=1)
            print("✅ AWS Textract connection successful!")
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {str(e)}")
            return False

# Camera scanning functionality
def start_camera_scanner():
    """Start camera-based document scanning"""
    try:
        processor = TextractProcessor()
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        print("📸 Camera Scanner Started!")
        print("Press 's' to scan document, 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Could not read frame")
                break
            
            # Display frame
            cv2.imshow("Smart Campus Scanner - Press 's' to scan", frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                print("📄 Scanning document...")
                
                # Convert frame to bytes
                _, buffer = cv2.imencode('.jpg', frame)
                image_bytes = buffer.tobytes()
                
                try:
                    # Process with Textract
                    result = processor.process_document_bytes(image_bytes)
                    
                    print("\n" + "="*50)
                    print("📊 SCAN RESULTS")
                    print("="*50)
                    
                    # Display query results
                    for alias, data in result['query_results'].items():
                        confidence = data['confidence']
                        text = data['text']
                        status = "✅" if confidence > 80 else "⚠️" if confidence > 50 else "❌"
                        print(f"{status} {alias}: {text} (Confidence: {confidence:.1f}%)")
                    
                    print(f"\n📈 Average Confidence: {result['average_confidence']:.1f}%")
                    print("="*50)
                    
                except Exception as e:
                    print(f"❌ Scan failed: {str(e)}")
            
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("📷 Camera scanner closed")
        
    except Exception as e:
        print(f"❌ Camera scanner error: {str(e)}")

# Test function
def test_textract_setup():
    """Test Textract setup and configuration"""
    print("🔍 Testing AWS Textract Setup...")
    
    # Check environment variables
    required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Please update your .env file with AWS credentials")
        return False
    
    try:
        processor = TextractProcessor()
        return processor.test_connection()
    except Exception as e:
        print(f"❌ Setup test failed: {str(e)}")
        return False

# Main execution
if __name__ == "__main__":
    # Test setup first
    if test_textract_setup():
        print("\n🚀 Starting camera scanner...")
        start_camera_scanner()
    else:
        print("\n💡 Please fix the setup issues above before running the scanner.")
