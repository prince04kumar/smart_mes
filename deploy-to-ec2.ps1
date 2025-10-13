# Smart Campus - Deploy Backend to EC2
# This script helps you update the backend on EC2

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Deploy Backend to EC2               " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

$EC2_IP = "100.26.22.38"
$LOCAL_FILE = "C:\Users\ASUS\Desktop\aws\backend\app.py"
$KEY_FILE = Read-Host "Enter path to your EC2 key file (.pem)"

if (-not (Test-Path $LOCAL_FILE)) {
    Write-Host "ERROR: app.py not found at $LOCAL_FILE" -ForegroundColor Red
    pause
    exit
}

if (-not (Test-Path $KEY_FILE)) {
    Write-Host "ERROR: Key file not found at $KEY_FILE" -ForegroundColor Red
    pause
    exit
}

Write-Host "Step 1: Uploading updated app.py to EC2..." -ForegroundColor Cyan
Write-Host ""

$scpCommand = "scp -i `"$KEY_FILE`" `"$LOCAL_FILE`" ubuntu@${EC2_IP}:~/smart_mes/backend/app.py"
Write-Host "Running: $scpCommand" -ForegroundColor Gray
Invoke-Expression $scpCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS: File uploaded!" -ForegroundColor Green
} else {
    Write-Host "ERROR: Upload failed!" -ForegroundColor Red
    pause
    exit
}

Write-Host ""
Write-Host "Step 2: Now you need to restart the backend on EC2" -ForegroundColor Yellow
Write-Host ""
Write-Host "SSH into EC2:" -ForegroundColor White
Write-Host "  ssh -i `"$KEY_FILE`" ubuntu@$EC2_IP" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then run these commands:" -ForegroundColor White
Write-Host "  cd ~/smart_mes/backend" -ForegroundColor Cyan
Write-Host "  source venv/bin/activate" -ForegroundColor Cyan
Write-Host ""
Write-Host "If using screen:" -ForegroundColor White
Write-Host "  screen -r backend" -ForegroundColor Cyan
Write-Host "  # Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "  python app.py" -ForegroundColor Cyan
Write-Host "  # Press Ctrl+A then D to detach" -ForegroundColor Gray
Write-Host ""
Write-Host "Or run directly:" -ForegroundColor White
Write-Host "  python app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Step 3: Test the deployment" -ForegroundColor Yellow
Write-Host "  curl http://$EC2_IP:5000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Step 4: Open your Vercel app and test" -ForegroundColor Yellow
Write-Host "  https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app/" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
pause
