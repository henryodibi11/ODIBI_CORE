@echo off
echo ================================================================
echo  LearnODIBI Studio - Launch Script
echo ================================================================
echo.
echo Starting LearnODIBI Studio...
echo.
echo The studio will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server when you're done.
echo.
echo ================================================================
echo.

python -m streamlit run odibi_core\learnodibi_ui\app.py

pause
