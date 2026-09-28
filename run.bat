@echo off
echo ====================================================
echo             Starting PocketSmart AI Server
echo ====================================================
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Opening http://127.0.0.1:8000 ...
start http://127.0.0.1:8000

python -m uvicorn app:app --host 127.0.0.1 --port 8000
pause
