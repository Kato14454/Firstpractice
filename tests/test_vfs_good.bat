@echo off
cd /d "%~dp0.."
echo --- минимальная VFS ---
python File.py --vfs vfs\minimal.json
echo --- несколько файлов ---
python File.py --vfs vfs\several.json
echo --- 3+ уровня вложенности ---
python File.py --vfs vfs\deep.json
echo --- глубокая VFS + стартовый скрипт ---
python File.py --vfs vfs\deep.json --script scripts\all_commands.txt