import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class MessageService:
    def __init__(self):
        self.email_enabled = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
        self.sms_enabled = os.getenv('SMS_ENABLED', 'false').lower() == 'true'
        
        # SMTP Configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        self.from_name = os.getenv('FROM_NAME', 'Doc Scanning System')
    
    def send_identification_message(self, person_data, scan_data, method="console", attachment_bytes=None, attachment_filename=None):
        """Send identification message to person"""
        
        # Prepare message content
        message_content = self._prepare_message_content(person_data, scan_data)
        
        if method == "email" and self.email_enabled and person_data.get('email'):
            return self._send_email(person_data['email'], "Doc Scan Notification", message_content, attachment_bytes, attachment_filename)
        elif method == "sms" and self.sms_enabled and person_data.get('phone'):
            return self._send_sms(person_data['phone'], message_content)
        else:
            # Default: Console notification
            return self._send_console_notification(person_data, message_content)
    
    def _prepare_message_content(self, person_data, scan_data):
        """Prepare the message content"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
🎯 Doc Scan Alert!

Hello {person_data.get('name', 'Unknown')}!

Your Doc was just scanned at {timestamp}.

📋 Detected Information:
• Name: {scan_data.get('StudentName', {}).get('value', 'Not detected')}
• Roll Number: {scan_data.get('RollNumber', {}).get('value', 'Not detected')}
• Branch: {scan_data.get('Branch', {}).get('value', 'Not detected')}

📧 Your registered details:
• Email: {person_data.get('email', 'Not provided')}
• Phone: {person_data.get('phone', 'Not provided')}
• Branch: {person_data.get('branch', 'Not provided')}

If this wasn't you, please contact security immediately.

--
Doc Scanning System
        """.strip()
        
        return message
    
    def _send_email(self, email, subject, message, attachment_bytes=None, attachment_filename=None):
        """Send email notification using SMTP"""
        try:
            if not self.smtp_username or not self.smtp_password:
                print("⚠️ SMTP credentials not configured. Showing email preview:")
                print(f"📧 TO: {email}")
                print(f"📧 FROM: {self.from_email}")
                print(f"📧 SUBJECT: {subject}")
                print(f"📧 MESSAGE:\n{message}")
                print("=" * 60)
                return True

            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = email

            # Create HTML version
            html_message = self._create_html_message(message)
            
            # Attach parts
            text_part = MIMEText(message, 'plain')
            html_part = MIMEText(html_message, 'html')
            msg.attach(text_part)
            msg.attach(html_part)

            # Attach scanned document if provided
            if attachment_bytes and attachment_filename:
                from email.mime.base import MIMEBase
                from email import encoders
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_bytes)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{attachment_filename}"')
                msg.attach(part)

            # Create secure connection and send email
            context = ssl.create_default_context()
            
            print(f"📧 Sending email to {email}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            print(f"📧 EMAIL PREVIEW (would be sent to {email}):")
            print(f"Subject: {subject}")
            print(f"Message:\n{message}")
            print("=" * 60)
            return False
    
    def _create_html_message(self, text_message):
        """Convert text message to HTML format"""
        # Replace newlines with <br> and style the message
        html_content = text_message.replace('\n', '<br>')
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
                .alert {{ background-color: #ff4444; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .info {{ background-color: #2196F3; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🎯 Doc Scan Alert!</h2>
                </div>
                <div class="content">
                    <pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">{html_content}</pre>
                </div>
                <div class="footer">
                    <p>This is an automated message from the Doc Scanning System</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_template
    
    def _send_sms(self, phone, message):
        """Send SMS notification (placeholder - requires SMS service)"""
        try:
            print(f"📱 SMS NOTIFICATION (would be sent to {phone}):")
            print(f"Message:\n{message}")
            print("=" * 50)
            return True
        except Exception as e:
            print(f"❌ SMS sending failed: {str(e)}")
            return False
    
    def _send_console_notification(self, person_data, message):
        """Send console notification"""
        try:
            print("\n" + "🔔" * 20 + " NOTIFICATION " + "🔔" * 20)
            print(message)
            print("🔔" * 52)
            print()
            return True
        except Exception as e:
            print(f"❌ Console notification failed: {str(e)}")
            return False
    
    def test_email_configuration(self, test_email=None):
        """Test email configuration"""
        try:
            test_email = test_email or self.smtp_username
            if not test_email:
                print("❌ No test email provided")
                return False
                
            test_subject = "Doc System - Email Test"
            test_message = f"""
🧪 Email Configuration Test

This is a test email from the Doc Scanning System.

Configuration:
• SMTP Server: {self.smtp_server}
• SMTP Port: {self.smtp_port}
• From Email: {self.from_email}
• Email Enabled: {self.email_enabled}

If you received this email, your SMTP configuration is working correctly!

--
Doc Scanning System
            """.strip()
            
            return self._send_email(test_email, test_subject, test_message)
            
        except Exception as e:
            print(f"❌ Email test failed: {str(e)}")
            return False
    
    def get_email_status(self):
        """Get current email configuration status"""
        status = {
            "email_enabled": self.email_enabled,
            "smtp_configured": bool(self.smtp_username and self.smtp_password),
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "from_email": self.from_email
        }
        return status

# Global message service instance
message_service = MessageService()
