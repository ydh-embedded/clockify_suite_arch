#!/bin/bash
# XLSX-Only Clockify Batch Generator
# Benötigt nur: pandas, openpyxl (kein odfpy!)
#
# Verwendung: ./batch_clockify_xlsx.sh [User-Email]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATOR="$SCRIPT_DIR/generate_clockify_xlsx_only.py"

# Prüfe ob Python-Script existiert
if [ ! -f "$GENERATOR" ]; then
    echo "❌ Fehler: $GENERATOR nicht gefunden!"
    exit 1
fi

# Prüfe Python-Abhängigkeiten (nur pandas und openpyxl!)
python3 -c "import pandas, openpyxl" 2>/dev/null
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Fehlende Python-Pakete!"
    echo ""
    echo "Installiere mit:"
    echo "  sudo pacman -S python-pandas python-openpyxl"
    echo ""
    echo "Oder mit pip:"
    echo "  pip install pandas openpyxl"
    echo ""
    exit 1
fi

# Parameter
USER_EMAIL="${1:-ydh-embedded@posteo.de}"

# Bestimme Verzeichnisse
INPUT_DIR="$SCRIPT_DIR/../ods"
OUTPUT_DIR="$SCRIPT_DIR/../csv clockify"

# Prüfe ob Input-Verzeichnis existiert
if [ ! -d "$INPUT_DIR" ]; then
    echo "❌ Fehler: Input-Verzeichnis nicht gefunden: $INPUT_DIR"
    echo "💡 Erstelle einen 'ods' Ordner auf der gleichen Ebene wie 'clockify_convert'."
    exit 1
fi

# Erstelle Output-Verzeichnis
mkdir -p "$OUTPUT_DIR"

echo ""
echo "🕐 Clockify XLSX Batch-Generator"
echo "═══════════════════════════════════"
echo "📥 Input: $INPUT_DIR"
echo "📤 Output: $OUTPUT_DIR"
echo "📧 Email: $USER_EMAIL"
echo ""
echo "🔍 Suche nach XLSX-Dateien (Schema: JJKWWW)..."
echo ""

# Zähler
count=0
success=0
failed=0
total_entries=0

# Durchlaufe alle XLSX-Dateien
for file in "$INPUT_DIR"/*.xlsx; do
    if [ ! -f "$file" ]; then
        continue
    fi
    
    basename=$(basename "$file")
    filename="${basename%.*}"
    
    # Überspringe Vorlagen und Temp-Dateien
    if [[ "$basename" == *"Vorlage"* ]] || [[ "$basename" == *"Template"* ]] || [[ "$basename" == *"_temp"* ]] || [[ "$basename" == *"_complete"* ]]; then
        echo "⏭️  Überspringe: $basename"
        continue
    fi
    
    # Prüfe Namensschema
    if [[ ! "$filename" =~ [0-9]{2}[-_]?KW[0-9]{2} ]]; then
        echo "⏭️  Überspringe (kein JJKWWW-Schema): $basename"
        continue
    fi
    
    count=$((count + 1))
    
    echo "📋 Verarbeite: $basename"
    
    # Führe Generator aus (schreibt direkt in die Datei)
    result=$(python3 "$GENERATOR" "$file" "$USER_EMAIL" 2>&1)
    
    if [ $? -ne 0 ]; then
        failed=$((failed + 1))
        echo "  ❌ Fehler bei Generierung"
        echo "$result" | head -5
        echo ""
        continue
    fi
    
    # Extrahiere Anzahl der Einträge
    entries=$(echo "$result" | grep -oP '✅ \K\d+(?= Einträge gefunden)')
    if [ -n "$entries" ]; then
        total_entries=$((total_entries + entries))
        echo "  ✅ $entries Einträge generiert"
    fi
    
    # Exportiere clockify-Sheet als CSV
    kw_match=$(echo "$filename" | grep -oP '[0-9]{2}[-_]?KW[0-9]{2}')
    output_csv="$OUTPUT_DIR/${kw_match}_clockify.csv"
    
    echo "  📤 Exportiere nach CSV..."
    python3 -c "
import pandas as pd
try:
    df = pd.read_excel('$file', sheet_name='clockify')
    df.to_csv('$output_csv', index=False)
    print('CSV erfolgreich exportiert')
except Exception as e:
    print(f'Fehler: {e}')
    exit(1)
" 2>&1
    
    if [ $? -eq 0 ]; then
        success=$((success + 1))
        echo "  ✅ CSV erstellt → $(basename "$output_csv")"
    else
        failed=$((failed + 1))
        echo "  ❌ Fehler beim CSV-Export"
    fi
    
    echo ""
done

# Prüfe ob Dateien gefunden wurden
if [ $count -eq 0 ]; then
    echo "⚠️  Keine XLSX-Dateien gefunden in $INPUT_DIR"
    echo ""
    echo "💡 Tipp: Lege deine Timesheets (*.xlsx) in den ods/ Ordner"
fi

# Zusammenfassung
echo "═══════════════════════════════════"
echo "📊 Zusammenfassung"
echo "═══════════════════════════════════"
echo "Dateien verarbeitet: $count"
echo "Erfolgreich: $success"
echo "Fehlgeschlagen: $failed"
echo "Gesamt Einträge: $total_entries"
echo ""
echo "📂 Dateien gespeichert in: $OUTPUT_DIR"
echo ""

if [ $success -gt 0 ]; then
    echo "✨ Konvertierung abgeschlossen!"
    echo ""
    echo "📤 Nächste Schritte:"
    echo "   1. Gehe zu Clockify → Reports → Detailed Report"
    echo "   2. Klicke 'Import' → 'CSV'"
    echo "   3. Wähle die *_clockify.csv Dateien aus:"
    echo "      $OUTPUT_DIR"
    echo ""
fi
