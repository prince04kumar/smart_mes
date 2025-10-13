# Smart Campus - Start Frontend
# This script starts the frontend development server

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Smart Campus - Frontend Launcher   " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if in correct directory
$frontendPath = "C:\Users\ASUS\Desktop\aws\frontend"

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend directory not found!" -ForegroundColor Red
    Write-Host "Expected: $frontendPath" -ForegroundColor Yellow
    pause
    exit
}

# Change to frontend directory
Set-Location $frontendPath
Write-Host "📂 Current directory: $frontendPath" -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

# Display configuration
Write-Host "🔧 Configuration:" -ForegroundColor Cyan
Write-Host "   Backend URL: http://100.26.22.38:5000" -ForegroundColor White
Write-Host "   Frontend URL: http://localhost:5173" -ForegroundColor White
Write-Host ""

# Test backend connection
Write-Host "🔍 Testing backend connection..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://100.26.22.38:5000/health" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend is reachable!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Warning: Cannot reach backend!" -ForegroundColor Red
    Write-Host "   Backend URL: http://100.26.22.38:5000" -ForegroundColor Yellow
    Write-Host "   Please ensure:" -ForegroundColor Yellow
    Write-Host "   1. Backend is running on EC2" -ForegroundColor Yellow
    Write-Host "   2. EC2 Security Group allows port 5000" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit
    }
}

Write-Host ""
Write-Host "🚀 Starting frontend development server..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Press Ctrl+C to stop the server    " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Start the dev server
npm run dev
