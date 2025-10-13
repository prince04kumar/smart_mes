# 🚀 Frontend-Backend Connection Guide

## ✅ **Changes Made**

### 1. **API Configuration File Created**
- **File**: `frontend/src/config/api.js`
- **Purpose**: Centralized API endpoint management
- **Backend URL**: `http://100.26.22.38:5000`

### 2. **Frontend Files Updated**
All API calls now point to EC2 backend:

#### **AuthContext.jsx**
- ✅ `/profile` → `http://100.26.22.38:5000/profile`
- ✅ `/login` → `http://100.26.22.38:5000/login`
- ✅ `/register` → `http://100.26.22.38:5000/register`

#### **ScannerPage.jsx**
- ✅ `/analyze-id` → `http://100.26.22.38:5000/analyze-id`
- ✅ `/send-notification-email` → `http://100.26.22.38:5000/send-notification-email`

#### **DatabasePage.jsx**
- ✅ `/persons` → `http://100.26.22.38:5000/persons`
- ✅ `/create-person` → `http://100.26.22.38:5000/create-person`

### 3. **Backend CORS Updated**
- **File**: `backend/app.py`
- **Change**: Enhanced CORS to accept requests from any origin
- **Headers**: Content-Type, Authorization
- **Methods**: GET, POST, PUT, DELETE, OPTIONS

---

## 🔧 **Testing Steps**

### **Step 1: Verify Backend is Running on EC2**
```bash
# SSH into EC2
ssh -i "your-key.pem" ubuntu@100.26.22.38

# Check if backend is running
ps aux | grep python

# If not running, start it
cd ~/smart_mes/backend
source venv/bin/activate
python app.py
```

### **Step 2: Check EC2 Security Group**
1. Go to **AWS Console** → **EC2** → **Security Groups**
2. Find your instance's security group
3. **Inbound Rules** must include:
   ```
   Type: Custom TCP
   Port: 5000
   Source: 0.0.0.0/0 (Anywhere IPv4)
   ```
4. If not present, click **Edit Inbound Rules** → **Add Rule**

### **Step 3: Test Backend Health**
Open browser or use curl:
```bash
# Health check
curl http://100.26.22.38:5000/health

# Expected response:
# {"status": "healthy", "database": "connected"}
```

### **Step 4: Start Frontend Locally**
```bash
cd frontend
npm install  # If not already installed
npm run dev
```

### **Step 5: Test Authentication**
1. Go to `http://localhost:5173`
2. Try to **Register** a new user
3. Try to **Login** with created credentials
4. Check browser console (F12) for any errors

### **Step 6: Test Scanner**
1. Login to the app
2. Go to **Scanner** page
3. Upload an ID card image
4. Check if analysis results appear
5. Try sending notification email

### **Step 7: Test Database**
1. Go to **Database** page
2. Try adding a new person
3. Verify person appears in the list

---

## 🐛 **Troubleshooting**

### **Issue 1: "Failed to fetch" or Network Error**

**Possible Causes:**
- Backend not running on EC2
- EC2 Security Group blocking port 5000
- CORS issues

**Solutions:**
```bash
# 1. Check if backend is running
ssh -i "your-key.pem" ubuntu@100.26.22.38
ps aux | grep python

# 2. Restart backend if needed
cd ~/smart_mes/backend
source venv/bin/activate
python app.py

# 3. Check security group allows port 5000
# Go to AWS Console → EC2 → Security Groups → Edit Inbound Rules
```

### **Issue 2: CORS Error in Browser Console**

**Error Message:**
```
Access to fetch at 'http://100.26.22.38:5000/...' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Solution:**
The CORS configuration in `app.py` is already updated. If still seeing this:
1. Restart backend on EC2
2. Clear browser cache (Ctrl+Shift+Delete)
3. Try in incognito mode

### **Issue 3: 401 Unauthorized**

**Cause:** JWT token expired or invalid

**Solution:**
1. Logout from frontend
2. Login again to get fresh token
3. Check browser console for token issues

### **Issue 4: Timeout or Slow Response**

**Causes:**
- AWS Textract processing large images
- Network latency

**Solutions:**
1. Use smaller image sizes (< 2MB)
2. Increase fetch timeout in frontend
3. Check EC2 instance CPU usage (shouldn't exceed 80%)

---

## 📱 **Deploy Frontend to Vercel**

### **Step 1: Create Vercel Account**
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub

### **Step 2: Import GitHub Repository**
1. Push your frontend code to GitHub
2. In Vercel dashboard, click **"New Project"**
3. Import your GitHub repository

### **Step 3: Configure Build Settings**
```
Framework Preset: Vite
Build Command: npm run build
Output Directory: dist
Root Directory: frontend
```

### **Step 4: Set Environment Variable**
In Vercel project settings:
```
Name: VITE_API_URL
Value: http://100.26.22.38:5000
```

### **Step 5: Deploy**
Click **Deploy** and wait for build to complete.

### **Step 6: Update CORS (Optional)**
If you want to restrict CORS to only your Vercel domain:

Edit `backend/app.py`:
```python
CORS(app, resources={
    r"/*": {
        "origins": ["https://your-app.vercel.app", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

Then restart backend on EC2.

---

## 🌐 **Optional: Setup Nginx Reverse Proxy**

This allows using port 80 instead of 5000:

### **Install Nginx on EC2**
```bash
sudo apt update
sudo apt install nginx -y
```

### **Create Nginx Config**
```bash
sudo nano /etc/nginx/sites-available/smart_mes
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name 100.26.22.38;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Enable and Restart**
```bash
sudo ln -s /etc/nginx/sites-available/smart_mes /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **Update EC2 Security Group**
Add inbound rule for **port 80** (HTTP)

### **Update Frontend API Config**
Change `frontend/src/config/api.js`:
```javascript
const API_BASE_URL = 'http://100.26.22.38';  // No port 5000 needed!
```

---

## 📊 **Backend Status Check Commands**

```bash
# Check if backend process is running
ps aux | grep python

# Check port 5000 is listening
netstat -tuln | grep 5000

# View backend logs
cd ~/smart_mes/backend
tail -f nohup.out  # If running with nohup

# Restart backend (if needed)
pkill -f "python app.py"
cd ~/smart_mes/backend
source venv/bin/activate
python app.py
```

---

## ✅ **Success Checklist**

- [ ] Backend running on EC2 (100.26.22.38:5000)
- [ ] EC2 Security Group allows port 5000
- [ ] Frontend API config updated
- [ ] CORS enabled in backend
- [ ] Health endpoint responds: `http://100.26.22.38:5000/health`
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can upload and analyze ID cards
- [ ] Can view database records
- [ ] Email notifications working

---

## 🎯 **Next Steps**

1. **Test all features** thoroughly
2. **Deploy frontend to Vercel** for production
3. **Setup custom domain** (optional)
4. **Add HTTPS with SSL certificate** (recommended for production)
5. **Monitor EC2 usage** to stay within free tier limits
6. **Setup CloudWatch alarms** for EC2 monitoring

---

## 🔐 **Security Recommendations**

1. **Restrict CORS** to specific origins in production
2. **Setup API rate limiting** to prevent abuse
3. **Use environment variables** for sensitive data
4. **Enable HTTPS** for secure communication
5. **Regular security updates** on EC2 instance
6. **Rotate AWS credentials** periodically

---

## 📞 **Support**

If you encounter issues:
1. Check browser console (F12) for errors
2. Check EC2 backend logs
3. Verify EC2 security group settings
4. Test backend endpoints directly with curl/Postman

Good luck with your deployment! 🚀
