# SMTP Configuration Guide

## How to Set Up Email Notifications

### 1. Gmail Setup (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Copy the 16-character password

3. **Update your .env file**:
   ```env
   EMAIL_ENABLED=true
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-character-app-password
   FROM_EMAIL=your-email@gmail.com
   FROM_NAME=Doc Scanning System
   ```

### 2. Outlook/Hotmail Setup

1. **Update your .env file**:
   ```env
   EMAIL_ENABLED=true
   SMTP_SERVER=smtp-mail.outlook.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@outlook.com
   SMTP_PASSWORD=your-password
   FROM_EMAIL=your-email@outlook.com
   FROM_NAME=Doc Scanning System
   ```

### 3. Yahoo Mail Setup

1. **Update your .env file**:
   ```env
   EMAIL_ENABLED=true
   SMTP_SERVER=smtp.mail.yahoo.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@yahoo.com
   SMTP_PASSWORD=your-password
   FROM_EMAIL=your-email@yahoo.com
   FROM_NAME=Doc Scanning System
   ```

### 4. Testing Your Configuration

After updating your .env file:

1. **Restart the Flask server**
2. **Test via API**:
   ```bash
   curl -X POST http://localhost:5000/test-email \
   -H "Content-Type: application/json" \
   -d '{"email": "test@example.com"}'
   ```

3. **Check email status**:
   ```bash
   curl http://localhost:5000/email-status
   ```

### 5. Security Notes

- ⚠️ **Never commit your .env file to Git**
- 🔒 **Use App Passwords instead of account passwords**
- 🛡️ **Keep your credentials secure**

### 6. Troubleshooting

**Common Issues:**
- "Authentication failed" → Check username/password
- "Connection refused" → Check SMTP server and port
- "TLS error" → Ensure SMTP_PORT is correct (usually 587)

**Debug Steps:**
1. Check your .env file syntax
2. Verify email credentials
3. Test with curl commands
4. Check Flask server logs
