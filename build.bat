@echo off
setlocal enabledelayedexpansion

echo ====================================================
echo        PocketSmart AI - Build ^& Verification
echo ====================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: 2. Check Virtual Environment
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [OK] Activating virtual environment...
call venv\Scripts\activate.bat

:: 3. Install/Update Dependencies
echo [INFO] Installing required dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies are up to date.

:: 4. Verify Build and Endpoints
echo.
echo [INFO] Running build verification tests...
python test_build.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Build verification tests failed!
    pause
    exit /b 1
)

echo.
echo ====================================================
echo    BUILD SUCCESSFUL! PocketSmart AI is ready.
echo    You can now run: run.bat or uvicorn app:app --reload
echo ====================================================
pause
