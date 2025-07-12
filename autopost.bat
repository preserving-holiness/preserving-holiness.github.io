@echo off
rem Change directory to the script's location to ensure invoke runs correctly
cd /d "%~dp0"

echo Running autopost command...
invoke autopost
echo.
echo Autopost command finished.
pause 