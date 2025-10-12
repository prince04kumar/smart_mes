"""
Test script for AWS Textract setup
Run this to verify your AWS credentials and Textract configuration
"""

from textract2 import TextractProcessor, test_textract_setup
import os
from dotenv import load_dotenv

def main():
    print("🔧 AWS Textract Configuration Test")
    print("="*50)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    print("📋 Checking Environment Variables:")
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION')
    
    if aws_key:
        print(f"✅ AWS_ACCESS_KEY_ID: {aws_key[:8]}...")
    else:
        print("❌ AWS_ACCESS_KEY_ID: Not set")
    
    if aws_secret:
        print(f"✅ AWS_SECRET_ACCESS_KEY: {aws_secret[:8]}...")
    else:
        print("❌ AWS_SECRET_ACCESS_KEY: Not set")
    
    if aws_region:
        print(f"✅ AWS_DEFAULT_REGION: {aws_region}")
    else:
        print("❌ AWS_DEFAULT_REGION: Not set")
    
    print("\n" + "="*50)
    
    # Test Textract setup
    if test_textract_setup():
        print("\n🎉 SUCCESS! Your AWS Textract is ready to use!")
        print("\n📝 Next steps:")
        print("1. Update your .env file with real AWS credentials")
        print("2. Run 'python textract2.py' to start camera scanner")
        print("3. Or use TextractProcessor in your Flask app")
    else:
        print("\n❌ SETUP FAILED!")
        print("\n🔧 To fix:")
        print("1. Get AWS credentials from AWS IAM console")
        print("2. Update .env file:")
        print("   AWS_ACCESS_KEY_ID=your_access_key")
        print("   AWS_SECRET_ACCESS_KEY=your_secret_key")
        print("   AWS_DEFAULT_REGION=us-east-1")

if __name__ == "__main__":
    main()