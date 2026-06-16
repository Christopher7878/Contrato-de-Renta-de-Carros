@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    py -m venv .venv
)

echo Verificando librerias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo Iniciando programa...
".venv\Scripts\python.exe" app.py

pause