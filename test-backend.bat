@echo off
color 0A
echo.
echo ========================================
echo   Smart Campus - Test Backend
echo ========================================
echo.
echo Testing backend at: http://100.26.22.38:5000
echo.
echo Checking health endpoint...
curl -s http://100.26.22.38:5000/health
echo.
echo.
echo ========================================
echo If you see JSON response above, 
echo backend is working! ✅
echo.
echo Otherwise, check:
echo 1. Backend running on EC2?
echo 2. Security Group allows port 5000?
echo ========================================
echo.
pause
