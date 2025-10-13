# 🚀 Vercel Deployment - Complete Setup Guide

## ✅ Changes Made

### 1. **Updated Backend CORS Configuration**
- **File**: `backend/app.py`
- **Change**: Added your Vercel URL to allowed origins
- **URLs Allowed**:
  - ✅ http://localhost:5173 (local dev)
  - ✅ https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app (Vercel)

### 2. **Added Dynamic CORS Headers**
- Added `@app.after_request` decorator
- Automatically sets correct CORS headers for each request
- Supports credentials (cookies, auth headers)

---

## 📋 Next Steps to Complete Deployment

### **Step 1: Update Backend on EC2** ⚡ (DO THIS NOW)

You need to upload the updated `app.py` to your EC2 instance:

#### **Option A: Using SCP (Recommended)**

```powershell
# From your local machine (Windows PowerShell)
scp -i "your-key.pem" C:\Users\ASUS\Desktop\aws\backend\app.py ubuntu@100.26.22.38:~/smart_mes/backend/app.py
```

#### **Option B: Using Git**

```bash
# On your local machine
cd C:\Users\ASUS\Desktop\aws
git add backend/app.py
git commit -m "Update CORS for Vercel deployment"
git push origin new

# Then SSH into EC2
ssh -i "your-key.pem" ubuntu@100.26.22.38

# On EC2
cd ~/smart_mes
git pull origin new
```

#### **Option C: Manual Copy-Paste**

```bash
# SSH into EC2
ssh -i "your-key.pem" ubuntu@100.26.22.38

# Edit the file
nano ~/smart_mes/backend/app.py

# Find the CORS section (around line 19-45) and replace it with the new code
# Save: Ctrl+X, Y, Enter
```

---

### **Step 2: Restart Backend on EC2** 🔄

After updating the file:

```bash
# SSH into EC2 (if not already)
ssh -i "your-key.pem" ubuntu@100.26.22.38

# Navigate to backend
cd ~/smart_mes/backend

# If backend is running in foreground, stop it (Ctrl+C)

# Activate virtual environment
source venv/bin/activate

# Restart backend
python app.py
```

**Better: Run in background with screen**

```bash
# Check if screen session exists
screen -ls

# If backend screen exists, reattach
screen -r backend

# Stop running app (Ctrl+C)
python app.py

# Detach from screen (Ctrl+A then D)

# If no screen session, create one
screen -S backend
cd ~/smart_mes/backend
source venv/bin/activate
python app.py
# Detach: Ctrl+A then D
```

---

### **Step 3: Test CORS from PowerShell** 🧪

```powershell
# Test from Vercel origin
curl -H "Origin: https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app" `
     -H "Content-Type: application/json" `
     http://100.26.22.38:5000/health

# Expected response:
# {
#   "status": "healthy",
#   "message": "Flask server is running",
#   "database": "connected"
# }
```

---

### **Step 4: Update Frontend API Config (If Needed)** 📝

Check if your frontend is using the correct backend URL:

**On Vercel, your frontend should point to:**
```javascript
// frontend/src/config/api.js
const API_BASE_URL = 'http://100.26.22.38:5000';
```

**This is already correct!** ✅

---

### **Step 5: Test on Vercel** 🌐

1. **Open your Vercel app**:
   ```
   https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app/
   ```

2. **Open Browser Console** (F12)

3. **Try to Register/Login**:
   - If you see CORS errors → Backend not updated yet
   - If requests work → Success! ✅

4. **Test Features**:
   - ✅ Login/Register
   - ✅ Upload document
   - ✅ View database
   - ✅ Send email

---

## 🔒 Security Considerations

### **Current Setup (Development)**
- ✅ Backend on HTTP (port 5000)
- ✅ Frontend on HTTPS (Vercel)
- ⚠️ Mixed content warning might appear

### **Production Setup (Recommended)**

#### **Option 1: Use Nginx with SSL** (Best)

```bash
# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Get a domain name (e.g., from Freenom, Cloudflare)
# Point domain to your EC2 IP

# Setup SSL
sudo certbot --nginx -d yourdomain.com
```

#### **Option 2: Use Cloudflare Tunnel** (Free SSL)

```bash
# Install Cloudflare Tunnel
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create tunnel
cloudflared tunnel create smart-campus

# Route traffic
cloudflared tunnel route dns smart-campus yourdomain.com
```

#### **Option 3: Use Vercel Serverless Functions** (No EC2 needed)

Move your Flask backend to Vercel serverless functions.

---

## 🐛 Troubleshooting

### **Issue 1: "CORS policy blocked"**

**Symptoms:**
```
Access to fetch at 'http://100.26.22.38:5000/...' from origin 
'https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app' 
has been blocked by CORS policy
```

**Solution:**
1. Verify `app.py` has updated CORS config
2. Restart backend on EC2
3. Clear browser cache (Ctrl+Shift+Delete)
4. Test in incognito mode

**Check CORS headers:**
```powershell
curl -I -H "Origin: https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app" `
     http://100.26.22.38:5000/health
```

Should show:
```
Access-Control-Allow-Origin: https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app
Access-Control-Allow-Credentials: true
```

---

### **Issue 2: "Mixed Content" Warning**

**Symptoms:**
```
Mixed Content: The page at 'https://...' was loaded over HTTPS, 
but requested an insecure resource 'http://100.26.22.38:5000/...'
```

**Temporary Solution:**
- Click on the shield icon in browser address bar
- Click "Load unsafe scripts"

**Permanent Solution:**
- Setup HTTPS on backend (see Security Considerations)

---

### **Issue 3: Backend Not Responding**

**Check if backend is running:**
```bash
ssh -i "your-key.pem" ubuntu@100.26.22.38
ps aux | grep python
netstat -tuln | grep 5000
```

**Restart backend:**
```bash
cd ~/smart_mes/backend
source venv/bin/activate
python app.py
```

---

### **Issue 4: 502 Bad Gateway (If using Nginx)**

**Check Nginx logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Common fix:**
```bash
sudo systemctl restart nginx
sudo systemctl restart smart-campus  # if using systemd
```

---

## 📊 Deployment Checklist

### **Backend (EC2)**
- [ ] ✅ Updated `app.py` with new CORS config
- [ ] ✅ Uploaded file to EC2
- [ ] ✅ Restarted backend service
- [ ] ✅ Backend running on port 5000
- [ ] ✅ Security Group allows port 5000
- [ ] ✅ Health endpoint responds

### **Frontend (Vercel)**
- [ ] ✅ Deployed to Vercel
- [ ] ✅ API URL points to EC2 (100.26.22.38:5000)
- [ ] ✅ Environment variables set (if any)
- [ ] ✅ Can access app at Vercel URL

### **Testing**
- [ ] ✅ CORS headers present in response
- [ ] ✅ Can register new user from Vercel
- [ ] ✅ Can login from Vercel
- [ ] ✅ Can upload documents from Vercel
- [ ] ✅ Can view database from Vercel
- [ ] ✅ No console errors in browser

---

## 🎯 Quick Test Commands

### **Test 1: Backend Health**
```powershell
curl http://100.26.22.38:5000/health
```

### **Test 2: CORS Headers**
```powershell
curl -I -H "Origin: https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app" `
     http://100.26.22.38:5000/health
```

### **Test 3: Register Endpoint**
```powershell
$body = @{
    name = "Test User"
    email = "test@example.com"
    password = "test123"
    organization = "Test Org"
} | ConvertTo-Json

curl -X POST http://100.26.22.38:5000/register `
     -H "Content-Type: application/json" `
     -H "Origin: https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app" `
     -d $body
```

---

## 📱 Additional Optimizations

### **1. Setup Custom Domain**
- Buy domain from Cloudflare/Namecheap ($1-10/year)
- Point to EC2 IP
- Setup SSL certificate
- Update CORS with custom domain

### **2. Setup CI/CD**
```yaml
# .github/workflows/deploy.yml
name: Deploy to EC2
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to EC2
        run: |
          ssh -i ${{ secrets.EC2_KEY }} ubuntu@100.26.22.38 '
            cd ~/smart_mes &&
            git pull &&
            cd backend &&
            source venv/bin/activate &&
            pip install -r requirements.txt &&
            screen -X -S backend quit || true &&
            screen -dmS backend python app.py
          '
```

### **3. Setup Monitoring**
- Use AWS CloudWatch for EC2 metrics
- Use Vercel Analytics for frontend
- Setup error tracking (Sentry)

### **4. Optimize Performance**
- Enable gzip compression in Flask
- Use Redis for caching (already implemented)
- Setup CDN for static assets

---

## 🎉 You're Almost Done!

**Current Status:**
- ✅ Frontend deployed on Vercel
- ✅ Backend CORS config updated (in local file)
- ⏳ Need to upload to EC2 and restart

**Next Action:**
1. Upload updated `app.py` to EC2 (see Step 1)
2. Restart backend (see Step 2)
3. Test on Vercel (see Step 5)

**After this, your app will be fully deployed and accessible to everyone! 🚀**

---

## 📞 Need Help?

If you encounter any issues:
1. Check browser console for errors (F12)
2. Check EC2 backend logs
3. Test CORS with curl commands above
4. Verify backend is running: `ps aux | grep python`

Good luck! 🎯
