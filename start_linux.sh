#!/bin/bash

# Speech to Speech Linux Starter Script
# Dieses Script aktiviert das virtuelle Environment und startet die GUI

echo "Speech to Speech - Linux Starter"
echo "================================="

# Prüfe ob wir im richtigen Verzeichnis sind
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Prüfe ob das virtuelle Environment existiert
if [ ! -f "pyvenv.cfg" ]; then
    echo "Fehler: Virtual Environment nicht gefunden!"
    echo "Bitte stelle sicher, dass du im venv-Verzeichnis bist."
    exit 1
fi

# Prüfe ob GUI.py existiert
if [ ! -f "GUI.py" ]; then
    echo "Fehler: GUI.py nicht gefunden!"
    exit 1
fi

# Aktiviere das virtuelle Environment
echo "Aktiviere virtuelles Environment..."
source bin/activate

# Prüfe ob die Aktivierung erfolgreich war
if [ "$VIRTUAL_ENV" = "" ]; then
    echo "Fehler: Konnte virtuelles Environment nicht aktivieren!"
    exit 1
fi

echo "Virtual Environment aktiviert: $VIRTUAL_ENV"

# Installiere Dependencies falls nötig
if [ -f "req.txt" ]; then
    echo "Prüfe Dependencies..."
    pip install -r req.txt
fi

# Starte die GUI
echo "Starte Speech to Speech GUI..."
python GUI.py

echo "Anwendung beendet."
