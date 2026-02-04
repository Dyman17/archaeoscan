@echo off
echo Installing ArchaeoScan Backend Dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% == 0 (
    echo.
    echo Installation completed successfully!
    echo.
    echo To start the backend, run: python main.py
    echo.
    echo The API documentation will be available at: http://localhost:8000/docs
) else (
    echo.
    echo Installation failed. Please check your Python and pip installation.
)
pause