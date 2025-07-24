# Speech to Speech Application

Eine Speech-to-Speech Anwendung mit GUI, die Audio-Aufnahmen transkribiert, durch KI verarbeitet und als Sprache ausgibt.

## Installation und Start

### Voraussetzungen

- Python 3.11+
- Virtuelles Environment (bereits konfiguriert)
- Alle Dependencies aus `req.txt`

### Automatischer Start

Für einen einfachen Start der Anwendung stehen plattformspezifische Starter-Scripts zur Verfügung:

#### Linux/macOS

```bash
# Script ausführbar machen (einmalig)
chmod +x start_linux.sh

# Anwendung starten
./start_linux.sh
```

#### Windows

```cmd
# Anwendung starten
start_windows.bat
```

**Oder per Doppelklick auf die `start_windows.bat` Datei**

### Manueller Start

Falls die automatischen Starter nicht funktionieren:

#### Linux/macOS

```bash
# Virtual Environment aktivieren
source bin/activate

# Dependencies installieren (falls nötig)
pip install -r req.txt

# GUI starten
python GUI.py
```

#### Windows

```cmd
# Virtual Environment aktivieren
Scripts\activate.bat

# Dependencies installieren (falls nötig)
pip install -r req.txt

# GUI starten
python GUI.py
```

## Features

- **Audio-Aufnahme**: Direktes Aufnehmen über das Mikrofon
- **Audio-Import**: Unterstützung für verschiedene Audio-Formate (.wav, .mp3, .ogg, .flac, .m4a)
- **Spracherkennung**: Mehrsprachige Transkription (Deutsch, Englisch, Französisch, Spanisch, Italienisch)
- **KI-Integration**: Verarbeitung durch Ollama AI
- **Text-to-Speech**: Deutsche Sprachausgabe
- **Automatischer Modus**: Vollautomatischer Workflow von Aufnahme bis Sprachausgabe

## Bedienung

1. **Normale Nutzung**:
   - Audio-Datei auswählen oder direkt aufnehmen
   - Sprache auswählen
   - "Transcribe Audio" klicken
   - "Prompt A.I" für KI-Antwort
   - "Make TTS file" für Sprachausgabe

2. **Automatischer Modus**:
   - "Automatic" Checkbox aktivieren
   - "Start recording" für Aufnahme
   - "Stop recording" - danach läuft alles automatisch

## Technische Details

- **GUI Framework**: Tkinter
- **Spracherkennung**: Custom transcribe module
- **KI**:  qwen3:4b
- **TTS**: Piper TTS mit deutschem Voice Model
- **Audio-Verarbeitung**: Various audio libraries

## Dateien

- `GUI.py` - Hauptanwendung mit grafischer Benutzeroberfläche
- `transcribe.py` - Audio-Transkription
- `audioHandler.py` - Audio-Aufnahme und -verarbeitung
- `OllamaResponse.py` - KI-Integration
- `tts.py` - Text-to-Speech Funktionalität
- `req.txt` - Python Dependencies
- `start_linux.sh` - Linux/macOS Starter
- `start_windows.bat` - Windows Starter