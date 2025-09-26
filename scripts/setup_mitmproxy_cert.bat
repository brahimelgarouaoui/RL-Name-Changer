@echo off
REM Mitmproxy Certificate Setup for Windows
REM This script downloads, installs, and configures mitmproxy certificates

title Mitmproxy Certificate Setup
echo =====================================================
echo Mitmproxy Certificate Setup for Windows
echo =====================================================
echo.

REM Check if script is running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click this script and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [INFO] Administrator privileges confirmed.
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found.

REM Check if mitmproxy is installed
python -c "import mitmproxy" >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] mitmproxy not found, installing...
    pip install mitmproxy
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install mitmproxy
        pause
        exit /b 1
    )
    echo [INFO] mitmproxy installed successfully.
) else (
    echo [INFO] mitmproxy is already installed.
)

echo.
echo =====================================================
echo Starting mitmproxy to generate certificates...
echo =====================================================
echo.
echo [INFO] This will start mitmproxy on port 8080
echo [INFO] After it starts, press Ctrl+C to stop it
echo [INFO] The certificates will be generated automatically
echo.
echo Press any key to continue...
pause >nul

REM Start mitmproxy briefly to generate certificates
echo [INFO] Starting mitmproxy (press Ctrl+C after it starts)...
timeout /t 2 >nul
start /wait python -m mitmproxy.tools.mitmdump --listen-port 8080 --set confdir=%USERPROFILE%\.mitmproxy
echo.

REM Check if certificates were created
set CERT_DIR=%USERPROFILE%\.mitmproxy
if not exist "%CERT_DIR%\mitmproxy-ca-cert.pem" (
    echo ERROR: Certificate not found. Trying to generate manually...
    python -c "from mitmproxy.certs import CertStore; import os; store = CertStore.from_store(os.path.expanduser('~/.mitmproxy'), 'mitmproxy', 2048)"
    if not exist "%CERT_DIR%\mitmproxy-ca-cert.pem" (
        echo ERROR: Failed to generate certificates
        pause
        exit /b 1
    )
)

echo [INFO] Certificate found at: %CERT_DIR%\mitmproxy-ca-cert.pem
echo.

REM Convert PEM to CRT for Windows
echo [INFO] Converting certificate for Windows...
copy "%CERT_DIR%\mitmproxy-ca-cert.pem" "%CERT_DIR%\mitmproxy-ca-cert.crt" >nul
if %errorLevel% neq 0 (
    echo ERROR: Failed to copy certificate
    pause
    exit /b 1
)

echo [INFO] Certificate converted successfully.
echo.

REM Install certificate to Windows certificate store
echo =====================================================
echo Installing certificate to Windows certificate store...
echo =====================================================
echo.

certutil -addstore -f "ROOT" "%CERT_DIR%\mitmproxy-ca-cert.crt"
if %errorLevel% neq 0 (
    echo ERROR: Failed to install certificate to ROOT store
    echo Trying to install to current user store...
    certutil -addstore -user -f "ROOT" "%CERT_DIR%\mitmproxy-ca-cert.crt"
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install certificate
        pause
        exit /b 1
    )
)

echo [INFO] Certificate installed successfully!
echo.

REM Verify installation
echo =====================================================
echo Verifying certificate installation...
echo =====================================================
echo.

certutil -store ROOT | findstr /i "mitmproxy" >nul
if %errorLevel% equ 0 (
    echo [SUCCESS] Certificate is installed in ROOT store
) else (
    certutil -store -user ROOT | findstr /i "mitmproxy" >nul
    if %errorLevel% equ 0 (
        echo [SUCCESS] Certificate is installed in user ROOT store
    ) else (
        echo [WARNING] Certificate verification failed, but installation may have succeeded
    )
)

echo.
echo =====================================================
echo Setup Complete!
echo =====================================================
echo.
echo The mitmproxy certificate has been installed.
echo Certificate location: %CERT_DIR%\mitmproxy-ca-cert.crt
echo.
echo You can now use the RL Name Changer application.
echo.
echo NOTE: If you encounter any SSL/TLS issues:
echo 1. Restart your browser/applications
echo 2. Check Windows certificate store (certmgr.msc)
echo 3. Re-run this script if needed
echo.
pause