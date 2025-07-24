@echo off
REM Speech to Speech Windows Starter Script
REM Dieses Script aktiviert das virtuelle Environment und startet die GUI

echo Speech to Speech - Windows Starter
echo ===================================

REM Wechsle zum Script-Verzeichnis
cd /d "%~dp0"

REM Prüfe ob das virtuelle Environment existiert
if not exist "pyvenv.cfg" (
    echo Fehler: Virtual Environment nicht gefunden!
    echo Bitte stelle sicher, dass du im venv-Verzeichnis bist.
    pause
    exit /b 1
)

REM Prüfe ob GUI.py existiert
if not exist "GUI.py" (
    echo Fehler: GUI.py nicht gefunden!
    pause
    exit /b 1
)

REM Aktiviere das virtuelle Environment
echo Aktiviere virtuelles Environment...
call Scripts\activate.bat

REM Prüfe ob req.txt existiert und installiere Dependencies
if exist "req.txt" (
    echo Pruefe Dependencies...
    pip install -r req.txt
)

REM Starte die GUI
echo Starte Speech to Speech GUI...
python GUI.py

echo Anwendung beendet.
pause
