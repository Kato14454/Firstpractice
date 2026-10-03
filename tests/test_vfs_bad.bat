@echo off
cd /d "%~dp0.."
echo --- VFS не существует ---
python File.py --vfs vfs\nope.json
echo --- сломанный JSON ---
python File.py --vfs vfs\broken.json
echo --- корень не папка ---
python File.py --vfs vfs\wrong_root.json
echo --- без VFS, но со скриптом ---
python File.py --script scripts\all_commands.txt