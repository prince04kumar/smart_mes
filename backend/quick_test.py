"""
Quick Test: Extract Text from NIT Raipur Document
Usage: python quick_test.py <image_file>
"""

import boto3
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

def analyze_nit_document(image_path):
    """
    Analyze NIT Raipur approval document
    """
    print("\n" + "="*70)
    print("🎓 NIT RAIPUR DOCUMENT ANALYZER")
    print("="*70 + "\n")
    
    # Initialize Textract
    textract = boto3.client(
        'textract',
        region_name='us-east-1',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    
    print(f"📄 Reading document: {image_path}")
    
    # Read image
    with open(image_path, 'rb') as img:
        image_bytes = img.read()
    
    print("☁️  Sending to AWS Textract...")
    
    # Call Textract
    response = textract.detect_document_text(
        Document={'Bytes': image_bytes}
    )
    
    print("✅ Text extraction complete!\n")
    print("="*70)
    print("📝 EXTRACTED TEXT:")
    print("="*70 + "\n")
    
    # Extract and display all text
    lines = []
    for block in response.get('Blocks', []):
        if block['BlockType'] == 'LINE':
            text = block.get('Text', '')
            conf = block.get('Confidence', 0)
            lines.append(text)
            print(f"• {text}")
            print(f"  Confidence: {conf:.1f}%\n")
    
    # Analysis
    print("\n" + "="*70)
    print("🔍 DOCUMENT ANALYSIS:")
    print("="*70 + "\n")
    
    # Check for key information
    full_text = ' '.join(lines).upper()
    
    # Institute
    if 'NIT' in full_text or 'RAIPUR' in full_text:
        print("🏢 Institution: National Institute of Technology Raipur")
    
    # File number
    for line in lines:
        if 'FILE' in line.upper() or 'NO' in line.upper():
            print(f"📋 File Number: {line}")
            break
    
    # Subject
    for line in lines:
        if 'SUBJECT' in line.upper() or 'APPROVAL' in line.upper():
            print(f"📄 Subject: {line}")
            break
    
    # Look for names/signatures
    print("\n👤 People/Signatures:")
    keywords = ['DR', 'PROF', 'HOD', 'LAB', 'INCHARGE', 'FACULTY']
    for line in lines:
        line_upper = line.upper()
        if any(keyword in line_upper for keyword in keywords):
            print(f"   • {line}")
    
    # Look for dates
    print("\n📅 Dates Found:")
    import re
    date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'
    for line in lines:
        dates = re.findall(date_pattern, line)
        if dates:
            print(f"   • {line}")
    
    print("\n" + "="*70)
    print("✨ Analysis Complete!")
    print("="*70 + "\n")
    
    return lines

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n❌ Error: Please provide image path")
        print("\nUsage:")
        print("  python quick_test.py document.jpg")
        print("  python quick_test.py path/to/image.png")
        print("\nExample:")
        print("  python quick_test.py nit_document.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"\n❌ Error: File not found: {image_path}")
        sys.exit(1)
    
    try:
        lines = analyze_nit_document(image_path)
        
        # Save to file
        output_file = 'extracted_text.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("NIT RAIPUR DOCUMENT - EXTRACTED TEXT\n")
            f.write("="*70 + "\n\n")
            for line in lines:
                f.write(line + "\n")
        
        print(f"💾 Full text saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("  • Check AWS credentials in .env file")
        print("  • Ensure image file is valid (JPG, PNG)")
        print("  • Check AWS Textract permissions")
        sys.exit(1)
