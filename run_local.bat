@echo off
echo Attempting to start Real Estate Dashboard...
echo.

:: Try running with python -m streamlit (more robust for PATH issues)
python -m streamlit run app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ----------------------------------------------------
    echo ERROR: Streamlit failed to start. 
    echo Please make sure you have run: pip install -r requirements.txt
    echo ----------------------------------------------------
)

pause
