@echo off
rem CLEANUP SCRIPT - Remove all fake and misleading files
echo CLEANING UP FAKE/MISLEADING FILES...
echo =====================================

cd /d "D:\Development\Autonomous-MCP-Agent"

echo Removing fake completion files...
if exist "PHASE_10_FINAL_COMPLETION.md" del "PHASE_10_FINAL_COMPLETION.md"
if exist "PROJECT_SUMMARY.md" del "PROJECT_SUMMARY.md"
if exist "FINAL_STATUS.md" del "FINAL_STATUS.md"
if exist "CHANGELOG.md" del "CHANGELOG.md"

echo Removing fake demos and tests...
if exist "phase_10_demo.py" del "phase_10_demo.py"
if exist "honest_test.py" del "honest_test.py"
if exist "real_test.py" del "real_test.py"

echo Removing fake documentation...
if exist "USAGE.md" del "USAGE.md"
if exist "STRUCTURE.md" del "STRUCTURE.md"
if exist "INSTALL.md" del "INSTALL.md"

echo Removing fake autonomous implementation...
if exist "autonomous_mcp\autonomous_orchestrator.py" del "autonomous_mcp\autonomous_orchestrator.py"
if exist "autonomous_mcp\execution_engine.py" del "autonomous_mcp\execution_engine.py"
if exist "autonomous_mcp\__init__.py" del "autonomous_mcp\__init__.py"

echo Removing fake tests directory...
if exist "tests" rmdir /s /q "tests"

echo Removing other fake/outdated content...
if exist "archive" rmdir /s /q "archive"
if exist "deploy" rmdir /s /q "deploy"
if exist "deployment" rmdir /s /q "deployment"
if exist "enterprise" rmdir /s /q "enterprise"
if exist "interfaces" rmdir /s /q "interfaces"
if exist "autonomous_agent_with_monitoring.py" del "autonomous_agent_with_monitoring.py"
if exist "start_with_monitoring.bat" del "start_with_monitoring.bat"
if exist "monitoring_config.json" del "monitoring_config.json"

echo.
echo CLEANUP COMPLETE!
echo.
echo Files kept (real/useful):
echo - minimal_mcp_server.py
echo - mcp_server.py
echo - autonomous_mcp\real_mcp_client.py
echo - requirements.txt
echo - PROJECT_DIRECTORY_PROTOCOL.md
echo - .git\
echo - LICENSE
echo.
echo Ready for clean restart...
