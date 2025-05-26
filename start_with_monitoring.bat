@echo off
echo Starting Autonomous MCP Agent with Python Process Monitoring
echo ===========================================================

cd /d "D:\Development\Autonomous-MCP-Agent"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo.
echo Creating logs directory...
if not exist "logs" mkdir logs

echo.
echo Testing monitoring integration...
python test_python_monitoring.py
if errorlevel 1 (
    echo ERROR: Monitoring test failed
    pause
    exit /b 1
)

echo.
echo Starting main agent with monitoring...
python autonomous_agent_with_monitoring.py

pause
