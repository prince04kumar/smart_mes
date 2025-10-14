"""
Test Script: Document Owner Detection using AWS Textract
This script extracts text from a document image and identifies the owner
"""

import boto3
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Initialize AWS Textract client
textract = boto3.client(
    'textract',
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def extract_text_from_image(image_path):
    """
    Extract text from image using AWS Textract
    """
    print(f"📄 Analyzing document: {image_path}")
    print("-" * 60)
    
    # Read image file
    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
    
    # Call Textract
    response = textract.detect_document_text(
        Document={'Bytes': image_bytes}
    )
    
    # Extract all text
    all_text = []
    blocks = response.get('Blocks', [])
    
    for block in blocks:
        if block['BlockType'] == 'LINE':
            text = block.get('Text', '')
            confidence = block.get('Confidence', 0)
            all_text.append({
                'text': text,
                'confidence': confidence
            })
    
    return all_text, blocks

def find_names(text_lines):
    """
    Find potential names in the extracted text
    Uses patterns and heuristics to identify names
    """
    names = []
    
    # Common patterns for names
    name_patterns = [
        r'Lab Incharge[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'HoD[,\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Prof\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Mr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'Ms\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for line_data in text_lines:
        text = line_data['text']
        
        # Check against patterns
        for pattern in name_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if match not in names:
                        names.append({
                            'name': match,
                            'found_in': text,
                            'confidence': line_data['confidence']
                        })
    
    return names

def find_organization(text_lines):
    """
    Find organization/institute name
    """
    org_patterns = [
        r'NATIONAL INSTITUTE OF TECHNOLOGY',
        r'NIT\s+\w+',
        r'INSTITUTE OF TECHNOLOGY',
        r'UNIVERSITY',
        r'COLLEGE'
    ]
    
    organizations = []
    
    for line_data in text_lines:
        text = line_data['text']
        for pattern in org_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                organizations.append({
                    'organization': text,
                    'confidence': line_data['confidence']
                })
                break
    
    return organizations

def find_file_number(text_lines):
    """
    Find file number or reference number
    """
    file_patterns = [
        r'File\s+No[:\s]+([A-Z0-9/.-]+)',
        r'Ref\s+No[:\s]+([A-Z0-9/.-]+)',
        r'Reference[:\s]+([A-Z0-9/.-]+)'
    ]
    
    for line_data in text_lines:
        text = line_data['text']
        for pattern in file_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'file_number': match.group(1),
                    'confidence': line_data['confidence']
                }
    return None

def find_date(text_lines):
    """
    Find dates in the document
    """
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
    ]
    
    dates = []
    for line_data in text_lines:
        text = line_data['text']
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append(match)
    
    return dates

def analyze_document(image_path):
    """
    Complete document analysis
    """
    print("\n" + "="*60)
    print("🔍 AWS TEXTRACT DOCUMENT ANALYSIS")
    print("="*60 + "\n")
    
    # Extract text
    text_lines, blocks = extract_text_from_image(image_path)
    
    if not text_lines:
        print("❌ No text found in the document!")
        return
    
    # Print all extracted text
    print("📝 EXTRACTED TEXT:")
    print("-" * 60)
    for i, line_data in enumerate(text_lines, 1):
        print(f"{i}. {line_data['text']} (Confidence: {line_data['confidence']:.1f}%)")
    
    print("\n" + "="*60)
    print("🎯 DOCUMENT ANALYSIS RESULTS")
    print("="*60 + "\n")
    
    # Find organization
    organizations = find_organization(text_lines)
    if organizations:
        print("🏢 ORGANIZATION:")
        for org in organizations[:3]:  # Top 3
            print(f"   • {org['organization']}")
            print(f"     Confidence: {org['confidence']:.1f}%")
        print()
    
    # Find file number
    file_num = find_file_number(text_lines)
    if file_num:
        print("📋 FILE NUMBER:")
        print(f"   • {file_num['file_number']}")
        print(f"     Confidence: {file_num['confidence']:.1f}%")
        print()
    
    # Find dates
    dates = find_date(text_lines)
    if dates:
        print("📅 DATES FOUND:")
        for date in set(dates):  # Remove duplicates
            print(f"   • {date}")
        print()
    
    # Find names
    names = find_names(text_lines)
    if names:
        print("👤 PEOPLE IDENTIFIED:")
        for name_data in names:
            print(f"   • Name: {name_data['name']}")
            print(f"     Context: {name_data['found_in']}")
            print(f"     Confidence: {name_data['confidence']:.1f}%")
            print()
    else:
        print("👤 PEOPLE IDENTIFIED:")
        print("   ⚠️  No names found with standard patterns")
        print("   💡 Tip: Names might be in handwriting or non-standard format")
        print()
    
    # Document Summary
    print("="*60)
    print("📊 DOCUMENT SUMMARY")
    print("="*60)
    
    print(f"\n📄 Document Type: Official Letter/Approval")
    print(f"🏢 Institution: {organizations[0]['organization'] if organizations else 'Not clearly identified'}")
    print(f"📋 File/Reference: {file_num['file_number'] if file_num else 'Not found'}")
    print(f"📅 Date(s): {', '.join(set(dates)) if dates else 'Not found'}")
    print(f"👥 People Mentioned: {len(names)} person(s) identified")
    
    # Ownership determination
    print("\n" + "="*60)
    print("🎯 DOCUMENT OWNERSHIP")
    print("="*60 + "\n")
    
    if names:
        print("✅ This document belongs to/involves:")
        for i, name_data in enumerate(names, 1):
            print(f"\n{i}. {name_data['name']}")
            print(f"   Role/Context: {name_data['found_in']}")
            print(f"   Confidence: {name_data['confidence']:.1f}%")
    else:
        print("⚠️  Unable to automatically determine owner from standard name patterns")
        print("💡 The document might contain handwritten names or signatures")
        print("💡 Manual review of extracted text recommended")
    
    print("\n" + "="*60)
    print("✨ Analysis Complete!")
    print("="*60 + "\n")
    
    return {
        'text_lines': text_lines,
        'organizations': organizations,
        'names': names,
        'file_number': file_num,
        'dates': dates
    }

if __name__ == "__main__":
    # Test with your document image
    # Replace this with the actual path to your document image
    
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        print("Usage: python test_document_owner.py <path_to_image>")
        print("\nExample:")
        print("  python test_document_owner.py document.jpg")
        print("  python test_document_owner.py path/to/your/image.png")
        sys.exit(1)
    
    if not os.path.exists(image_path):
        print(f"❌ Error: File not found: {image_path}")
        sys.exit(1)
    
    # Analyze the document
    results = analyze_document(image_path)
    
    # Save results to file
    output_file = 'document_analysis_results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("DOCUMENT ANALYSIS RESULTS\n")
        f.write("="*60 + "\n\n")
        
        f.write("EXTRACTED TEXT:\n")
        f.write("-"*60 + "\n")
        for line_data in results['text_lines']:
            f.write(f"{line_data['text']}\n")
        
        f.write("\n" + "="*60 + "\n")
        f.write("IDENTIFIED INFORMATION:\n")
        f.write("="*60 + "\n\n")
        
        if results['organizations']:
            f.write("Organizations:\n")
            for org in results['organizations']:
                f.write(f"  - {org['organization']}\n")
            f.write("\n")
        
        if results['names']:
            f.write("People:\n")
            for name_data in results['names']:
                f.write(f"  - {name_data['name']} ({name_data['found_in']})\n")
            f.write("\n")
        
        if results['file_number']:
            f.write(f"File Number: {results['file_number']['file_number']}\n\n")
        
        if results['dates']:
            f.write(f"Dates: {', '.join(set(results['dates']))}\n\n")
    
    print(f"📁 Results saved to: {output_file}")
