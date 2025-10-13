# EC2 Backend Diagnostics Script
# Run this to check backend status

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   EC2 Backend Diagnostics Tool        " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendIP = "100.26.22.38"
$backendPort = 5000
$backendURL = "http://${backendIP}:${backendPort}"

# Test 1: Ping EC2 Instance
Write-Host "[1/5] Testing EC2 Instance Connectivity..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $backendIP -Count 2 -Quiet

if ($pingResult) {
    Write-Host "✅ EC2 instance is reachable (ping successful)" -ForegroundColor Green
} else {
    Write-Host "❌ EC2 instance is NOT reachable (ping failed)" -ForegroundColor Red
    Write-Host "   Possible reasons:" -ForegroundColor Yellow
    Write-Host "   - EC2 instance is stopped" -ForegroundColor Yellow
    Write-Host "   - IP address has changed" -ForegroundColor Yellow
    Write-Host "   - Network connectivity issue" -ForegroundColor Yellow
}
Write-Host ""

# Test 2: Check Port 5000
Write-Host "[2/5] Testing Port 5000 Connectivity..." -ForegroundColor Yellow
try {
    $portTest = Test-NetConnection -ComputerName $backendIP -Port $backendPort -WarningAction SilentlyContinue
    
    if ($portTest.TcpTestSucceeded) {
        Write-Host "✅ Port 5000 is open and accepting connections" -ForegroundColor Green
    } else {
        Write-Host "❌ Port 5000 is NOT accessible" -ForegroundColor Red
        Write-Host "   Possible reasons:" -ForegroundColor Yellow
        Write-Host "   - Backend not running on EC2" -ForegroundColor Yellow
        Write-Host "   - Security Group not allowing port 5000" -ForegroundColor Yellow
        Write-Host "   - Firewall blocking the port" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Cannot test port (network error)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Check Health Endpoint
Write-Host "[3/5] Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $healthURL = "$backendURL/health"
    $response = Invoke-WebRequest -Uri $healthURL -TimeoutSec 10 -ErrorAction Stop
    
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is responding!" -ForegroundColor Green
        Write-Host "   Response: $($response.Content)" -ForegroundColor White
    }
} catch {
    Write-Host "FAILED: Backend health check FAILED" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Most likely causes:" -ForegroundColor Yellow
    Write-Host "   1. Backend Python app is not running" -ForegroundColor White
    Write-Host "   2. EC2 Security Group blocking port 5000" -ForegroundColor White
    Write-Host "   3. Backend crashed or stopped" -ForegroundColor White
}
Write-Host ""

# Test 4: Check Windows Firewall
Write-Host "[4/5] Checking Windows Firewall..." -ForegroundColor Yellow
try {
    $firewallRules = Get-NetFirewallRule -Direction Outbound -Enabled True | 
        Where-Object { $_.DisplayName -like "*5000*" -or $_.DisplayName -like "*Python*" }
    
    if ($firewallRules) {
        Write-Host "⚠️  Found firewall rules that might affect connection:" -ForegroundColor Yellow
        $firewallRules | Select-Object DisplayName, Action | Format-Table
    } else {
        Write-Host "✅ No obvious firewall blocking rules found" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not check firewall (need admin)" -ForegroundColor Yellow
}
Write-Host ""

# Test 5: DNS Resolution
Write-Host "[5/5] Checking DNS/IP Resolution..." -ForegroundColor Yellow
try {
    $resolved = [System.Net.Dns]::GetHostEntry($backendIP)
    Write-Host "✅ IP address resolves correctly" -ForegroundColor Green
} catch {
    Write-Host "✅ IP is valid (direct IP, no DNS needed)" -ForegroundColor Green
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTIC SUMMARY                   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($pingResult -and $portTest.TcpTestSucceeded) {
    Write-Host "🎉 Network connectivity is GOOD!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If health check still failed, the backend app needs to be started:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "SSH into EC2:" -ForegroundColor White
    Write-Host "  ssh -i `"your-key.pem`" ubuntu@$backendIP" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Start backend:" -ForegroundColor White
    Write-Host "  cd ~/smart_mes/backend" -ForegroundColor Cyan
    Write-Host "  source venv/bin/activate" -ForegroundColor Cyan
    Write-Host "  python app.py" -ForegroundColor Cyan
} elseif ($pingResult) {
    Write-Host "⚠️  EC2 is reachable but port 5000 is blocked" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Fix Security Group:" -ForegroundColor White
    Write-Host "  1. AWS Console → EC2 → Security Groups" -ForegroundColor Cyan
    Write-Host "  2. Select your instance's security group" -ForegroundColor Cyan
    Write-Host "  3. Edit Inbound Rules" -ForegroundColor Cyan
    Write-Host "  4. Add rule: Type=Custom TCP, Port=5000, Source=0.0.0.0/0" -ForegroundColor Cyan
} else {
    Write-Host "❌ EC2 instance is NOT reachable" -ForegroundColor Red
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor White
    Write-Host "  1. Check if EC2 instance is Running (not Stopped)" -ForegroundColor Cyan
    Write-Host "     AWS Console → EC2 → Instances → Check Instance State" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Verify IP address hasn't changed" -ForegroundColor Cyan
    Write-Host "     AWS Console → EC2 → Instances → Check Public IPv4" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Check your internet connection" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed troubleshooting, see: TROUBLESHOOTING.md" -ForegroundColor White
Write-Host ""
pause
