@echo off
cd /d "%~dp0.."

python File.py --vfs vfs\minimal.json
python File.py --vfs vfs\minimal.json --script .\scripts\ok.txt

pause
