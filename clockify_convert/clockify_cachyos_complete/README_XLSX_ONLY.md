# Clockify XLSX Converter - Einfache Lösung ohne odfpy

## Das Problem gelöst!

Diese Version benötigt **kein odfpy** mehr! Sie funktioniert nur mit **pandas** und **openpyxl**, die beide problemlos auf Manjaro/Arch Linux installierbar sind.

## Installation

```bash
# Mit pacman (empfohlen):
sudo pacman -S python-pandas python-openpyxl

# Oder mit pip:
pip install pandas openpyxl
```

## Verwendung

### Einzelne Datei verarbeiten

```bash
python3 generate_clockify_xlsx_only.py 25-KW47.xlsx "ihre.email@domain.com"
```

Das Skript:
1. Liest das **KW-Sheet**
2. Extrahiert alle Tätigkeiten (auch mit 0 Stunden!)
3. Schreibt sie in das **clockify-Sheet** der gleichen Datei

### Batch-Verarbeitung

```bash
cd ~/Dokumente/vsCode/clockify_suite_arch/clockify_convert
./batch_clockify_xlsx.sh "ihre.email@domain.com"
```

Das Batch-Skript:
1. Findet alle XLSX-Dateien im `../ods/`-Ordner
2. Verarbeitet sie automatisch
3. Erstellt CSV-Dateien im `../csv clockify/`-Ordner

## Ordnerstruktur

```
clockify_suite_arch/
├── clockify_convert/
│   ├── batch_clockify_xlsx.sh
│   └── generate_clockify_xlsx_only.py
├── ods/                          # Ihre XLSX-Dateien hier
│   └── 25-KW47.xlsx
└── csv clockify/                 # CSV-Output hier
    └── 25-KW47_clockify.csv
```

## Was ist neu?

✅ **Keine odfpy-Abhängigkeit** - Funktioniert mit Standard-Paketen  
✅ **Auch leere Einträge** - Tätigkeiten ohne Stunden werden mit 00:00:00 exportiert  
✅ **Einfache Installation** - Nur 2 Pakete nötig  
✅ **Nur XLSX** - Verwenden Sie Excel-Vorlagen statt ODS  

## Beispiel

```bash
# Pakete installieren
sudo pacman -S python-pandas python-openpyxl

# Datei verarbeiten
python3 generate_clockify_xlsx_only.py 25-KW47.xlsx "ydh-embedded@posteo.de"

# Ergebnis:
# - clockify-Sheet in 25-KW47.xlsx aktualisiert
# - Bereit für CSV-Export
```

## Alias (optional)

Fügen Sie zu `~/.zshrc` hinzu:

```bash
alias clockify='cd ~/Dokumente/vsCode/clockify_suite_arch/clockify_convert && ./batch_clockify_xlsx.sh "ydh-embedded@posteo.de"'
```

Dann einfach `clockify` eingeben!

## Vorteile gegenüber der ODS-Version

- ✅ Keine Probleme mit odfpy auf Manjaro
- ✅ Schnellere Installation
- ✅ Excel-Vorlagen sind weit verbreitet
- ✅ Bessere Kompatibilität

Viel Erfolg! 🚀
