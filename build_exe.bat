@echo off
echo ====================================================
echo      PocketSmart AI - Standalone EXE Builder
echo ====================================================
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [INFO] Installing PyInstaller...
pip install pyinstaller

echo [INFO] Building standalone executable...
pyinstaller --noconfirm --onedir --windowed ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.lifespan" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --hidden-import "google.genai" ^
    --name "PocketSmartAI" app.py

echo.
echo ====================================================
echo Executable generated in dist\PocketSmartAI\
echo ====================================================
pause
