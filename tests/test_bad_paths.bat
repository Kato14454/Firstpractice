@echo off
cd /d "%~dp0.."

python File.py --vfs .\bad_vfs --script .\scripts\bad_script.txt

pause
