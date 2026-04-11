@echo off
echo ============================================
echo    RetailOS v2 - Starting up...
echo ============================================

if not exist venv (
  echo [1/3] Creating virtual environment...
  python -m venv venv
)

echo [2/3] Installing dependencies...
call venv\Scripts\activate
pip install -q -r requirements.txt

echo [3/3] Starting RetailOS...
echo.
echo   Open browser : http://127.0.0.1:5000
echo   First time?  : http://127.0.0.1:5000/register
echo   Stop         : Ctrl+C
echo.
python app.py
pause
