# 🚨 Backend Connection Troubleshooting

## Current Issue
**Error**: `http://100.26.22.38:5000/health` - Site can't be reached, took too long to respond

## Possible Causes & Solutions

---

### **1️⃣ Check EC2 Instance Status**

**Go to AWS Console:**
1. Login to [AWS Console](https://console.aws.amazon.com)
2. Navigate to **EC2** → **Instances**
3. Find your instance (ip-172-31-29-212 or public IP 100.26.22.38)
4. Check **Instance State**:
   - ✅ Should be: **Running** (green)
   - ❌ If **Stopped** (red): Click **Instance State** → **Start Instance**

**Wait 2-3 minutes after starting, then test again**

⚠️ **IMPORTANT**: If you stopped/restarted the instance, the PUBLIC IP may have changed!
- Check the new public IP in EC2 console
- Update `frontend/src/config/api.js` with new IP

---

### **2️⃣ Verify EC2 Security Group Rules**

**Check Inbound Rules:**
1. AWS Console → **EC2** → **Security Groups**
2. Find your instance's security group
3. Click **Inbound rules** tab
4. **Required Rule:**

```
Type:        Custom TCP
Protocol:    TCP
Port Range:  5000
Source:      0.0.0.0/0  (Anywhere IPv4)
Description: Flask Backend API
```

**If rule is missing:**
1. Click **Edit inbound rules**
2. Click **Add rule**
3. Set values as above
4. Click **Save rules**

---

### **3️⃣ Check Backend Process on EC2**

**SSH into EC2:**
```bash
ssh -i "your-key.pem" ubuntu@100.26.22.38
```

**If SSH doesn't work, the instance might be stopped or IP changed**

**Once connected, check if backend is running:**
```bash
# Check Python process
ps aux | grep python

# Check if port 5000 is listening
netstat -tuln | grep 5000

# Check backend logs
cd ~/smart_mes/backend
ls -la
```

**If backend is NOT running:**
```bash
cd ~/smart_mes/backend
source venv/bin/activate
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Running on http://172.31.29.212:5000
```

---

### **4️⃣ Test Backend from EC2 (Internal)**

**While SSH'd into EC2, test internally:**
```bash
# Test on localhost
curl http://127.0.0.1:5000/health

# Test on private IP
curl http://172.31.29.212:5000/health
```

**Expected response:**
```json
{"status":"healthy","database":"connected"}
```

**If this works but external doesn't, it's a Security Group issue**

---

### **5️⃣ Check if IP Address Changed**

**AWS Free Tier instances get NEW PUBLIC IP when stopped/started**

**To check current IP:**
1. AWS Console → EC2 → Instances
2. Select your instance
3. Look at **Public IPv4 address** field
4. If it's different from `100.26.22.38`, update frontend config

**Update frontend config:**
```javascript
// frontend/src/config/api.js
const API_BASE_URL = 'http://NEW_IP_HERE:5000';
```

---

### **6️⃣ Run Backend in Background (Persistent)**

**If backend stops when you close SSH, use nohup or screen:**

**Option A: Using nohup**
```bash
cd ~/smart_mes/backend
source venv/bin/activate
nohup python app.py > backend.log 2>&1 &

# Check if running
ps aux | grep python
```

**Option B: Using screen (recommended)**
```bash
# Install screen if not available
sudo apt install screen -y

# Start screen session
screen -S backend

# Inside screen, start backend
cd ~/smart_mes/backend
source venv/bin/activate
python app.py

# Detach from screen: Press Ctrl+A then D
# Backend keeps running even after logout!

# To reattach later:
screen -r backend
```

---

### **7️⃣ Alternative: Bind to 0.0.0.0**

**Make sure Flask binds to all interfaces:**

Edit `backend/app.py` (last line):
```python
# Instead of:
# app.run(debug=True)

# Use:
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Restart backend after this change**

---

### **8️⃣ Check Windows Firewall (Your Computer)**

**Windows might be blocking outbound connection:**

1. Windows Search → "Windows Defender Firewall"
2. Click **Advanced settings**
3. Click **Outbound Rules**
4. Look for any rule blocking port 5000
5. If found, disable or delete it

**Or temporarily disable firewall to test:**
```powershell
# Run PowerShell as Administrator
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Test connection
curl http://100.26.22.38:5000/health

# Re-enable firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True
```

---

## **🔧 Quick Fix Checklist**

Run through this checklist:

- [ ] **EC2 instance is Running** (not stopped)
- [ ] **Public IP hasn't changed** (check AWS console)
- [ ] **Security Group allows port 5000** (0.0.0.0/0)
- [ ] **Backend process is running** (ps aux | grep python)
- [ ] **Port 5000 is listening** (netstat -tuln | grep 5000)
- [ ] **Backend runs on 0.0.0.0:5000** (not just 127.0.0.1)
- [ ] **Can SSH into EC2** (ssh works)
- [ ] **Backend responds internally** (curl from within EC2)
- [ ] **No Windows firewall blocking** (outbound port 5000)

---

## **🚀 Most Common Fix**

**90% of the time, it's one of these:**

### **Fix 1: Backend Not Running**
```bash
ssh -i "your-key.pem" ubuntu@100.26.22.38
cd ~/smart_mes/backend
source venv/bin/activate
python app.py
```

### **Fix 2: Security Group Missing Rule**
- AWS Console → EC2 → Security Groups
- Add inbound rule: TCP port 5000 from 0.0.0.0/0

### **Fix 3: IP Address Changed**
- Check new IP in AWS Console
- Update `frontend/src/config/api.js`

---

## **📝 Testing Steps After Fix**

1. **Test from PowerShell:**
   ```powershell
   curl http://100.26.22.38:5000/health
   ```

2. **Test from Browser:**
   ```
   http://100.26.22.38:5000/health
   ```

3. **Test with HTML file:**
   ```
   Open: C:\Users\ASUS\Desktop\aws\frontend\test-backend.html
   ```

4. **Start frontend if tests pass:**
   ```powershell
   cd C:\Users\ASUS\Desktop\aws\frontend
   npm run dev
   ```

---

## **🆘 Still Not Working?**

**Gather diagnostic info:**

```bash
# On EC2 (SSH)
# 1. Instance info
curl http://169.254.169.254/latest/meta-data/public-ipv4
curl http://169.254.169.254/latest/meta-data/local-ipv4

# 2. Network info
ifconfig
netstat -tuln | grep 5000

# 3. Process info
ps aux | grep python

# 4. Backend logs
cd ~/smart_mes/backend
cat backend.log  # if using nohup
tail -100 backend.log
```

**On your Windows PC:**
```powershell
# Test connectivity
Test-NetConnection -ComputerName 100.26.22.38 -Port 5000

# Trace route
tracert 100.26.22.38

# Check firewall
Get-NetFirewallRule | Where-Object {$_.Direction -eq 'Outbound'} | Select-Object Name, Enabled, Action
```

---

## **💡 Pro Tips**

1. **Keep EC2 running** - Don't stop it, or IP changes
2. **Use Elastic IP** - AWS service to get permanent IP (free for running instances)
3. **Use systemd** - Auto-start backend on EC2 boot
4. **Monitor with CloudWatch** - Set alarms for EC2 down
5. **Use port 80 with Nginx** - More reliable than port 5000

---

## **🔗 Next Steps**

Once backend is accessible:
1. Update frontend config if IP changed
2. Run `npm run dev` to start frontend
3. Test all features (login, scanner, database)
4. Consider deploying frontend to Vercel

---

## **Need More Help?**

Check which specific step failed and focus on that section above.
Most likely: Backend not running OR Security Group issue.

Good luck! 🚀
