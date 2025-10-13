@echo off
echo.
echo ===================================
echo Testing Backend Connection
echo ===================================
echo.
echo Waiting for security group changes to propagate...
timeout /t 5 /nobreak > nul
echo.
echo Testing health endpoint...
echo.
curl http://100.26.22.38:5000/health
echo.
echo.
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS! Backend is now accessible!
    echo You can now start your frontend.
) else (
    echo FAILED! Still cannot reach backend.
    echo.
    echo Make sure you:
    echo 1. Added the security group rule correctly
    echo 2. Selected port 5000 ^(not 50 or 500^)
    echo 3. Source is 0.0.0.0/0
    echo 4. Saved the rules
)
echo.
pause
