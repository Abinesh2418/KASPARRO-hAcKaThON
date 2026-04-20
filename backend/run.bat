@echo off
REM Windows batch script to run the FastAPI backend

echo ========================================
echo Kasparo Backend API - Starting Server
echo ========================================

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt

REM Run the server
echo.
echo Starting FastAPI server on http://localhost:8000
echo Documentation available at http://localhost:8000/docs
echo.
python main.py

pause
