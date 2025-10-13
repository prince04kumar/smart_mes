# Test CORS Configuration for Vercel Deployment

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Testing CORS for Vercel             " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BACKEND_URL = "http://100.26.22.38:5000"
$VERCEL_URL = "https://smart-mes-git-main-princekumar72131-8019s-projects.vercel.app"

# Test 1: Basic Health Check
Write-Host "[Test 1] Testing Backend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/health" -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "SUCCESS: Backend is running!" -ForegroundColor Green
        Write-Host "Response: $($response.Content)" -ForegroundColor White
    }
} catch {
    Write-Host "FAILED: Backend is not responding!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "1. Backend is running on EC2" -ForegroundColor White
    Write-Host "2. Port 5000 is open in Security Group" -ForegroundColor White
    pause
    exit
}

Write-Host ""

# Test 2: CORS Headers
Write-Host "[Test 2] Testing CORS Headers..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = $VERCEL_URL
        "Access-Control-Request-Method" = "GET"
    }
    
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/health" -Headers $headers -Method OPTIONS -ErrorAction Stop
    
    Write-Host "OPTIONS request successful" -ForegroundColor Green
    
    # Check for CORS headers
    if ($response.Headers["Access-Control-Allow-Origin"]) {
        Write-Host "SUCCESS: CORS headers are present!" -ForegroundColor Green
        Write-Host "Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor White
    } else {
        Write-Host "WARNING: CORS headers not found in response" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "OPTIONS request failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: Actual GET with Origin header
Write-Host "[Test 3] Testing GET request with Vercel Origin..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = $VERCEL_URL
    }
    
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/health" -Headers $headers -ErrorAction Stop
    
    Write-Host "SUCCESS: Request with Origin header works!" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
    
    # Check response headers
    Write-Host ""
    Write-Host "Response Headers:" -ForegroundColor Cyan
    if ($response.Headers["Access-Control-Allow-Origin"]) {
        Write-Host "  Access-Control-Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Green
    } else {
        Write-Host "  Access-Control-Allow-Origin: NOT PRESENT" -ForegroundColor Red
    }
    
    if ($response.Headers["Access-Control-Allow-Credentials"]) {
        Write-Host "  Access-Control-Allow-Credentials: $($response.Headers['Access-Control-Allow-Credentials'])" -ForegroundColor Green
    } else {
        Write-Host "  Access-Control-Allow-Credentials: NOT PRESENT" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "FAILED: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Test Summary                         " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "If all tests passed:" -ForegroundColor Green
Write-Host "  Your Vercel app should work!" -ForegroundColor White
Write-Host "  Open: $VERCEL_URL" -ForegroundColor Cyan
Write-Host ""

Write-Host "If CORS headers are missing:" -ForegroundColor Yellow
Write-Host "  1. Make sure you uploaded the updated app.py to EC2" -ForegroundColor White
Write-Host "  2. Make sure you restarted the backend" -ForegroundColor White
Write-Host "  3. Run the deploy-to-ec2.ps1 script" -ForegroundColor White
Write-Host ""

pause
