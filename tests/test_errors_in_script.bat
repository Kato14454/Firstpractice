@echo off
cd /d "%~dp0.."

python File.py --vfs .\vfs --script .\scripts\with_errors.txt

pause
