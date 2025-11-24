# Clockify Converter: Setup-Anleitung für CachyOS

Diese Anleitung führt Sie durch die komplette Einrichtung des Clockify Converters auf einem frischen CachyOS-System. Der Prozess ist einfach und benötigt nur wenige Schritte.

---

## Ziel

Automatisches Auslesen von XLSX-Zeiterfassungsdateien, Generierung einer Clockify-Importtabelle und Erstellung einer fertigen CSV-Datei für den Upload.

---

## Schritt 1: Ordnerstruktur einrichten

Zuerst erstellen Sie die benötigte Ordnerstruktur. Öffnen Sie ein Terminal und führen Sie folgende Befehle aus:

```bash
# Erstellen Sie das Hauptverzeichnis
mkdir -p ~/Dokumente/vsCode/clockify_suite_arch/clockify_convert

# Erstellen Sie die Daten-Ordner
mkdir ~/Dokumente/vsCode/clockify_suite_arch/ods
mkdir ~/Dokumente/vsCode/clockify_suite_arch/csv_clockify
```

Anschließend entpacken Sie die ZIP-Datei (`clockify_xlsx_only.zip`) und kopieren die beiden Skript-Dateien in den `clockify_convert`-Ordner.

Ihre finale Struktur sollte so aussehen:

```
clockify_suite_arch/
├── clockify_convert/              # Skripte hier
│   ├── batch_clockify_xlsx.sh
│   └── generate_clockify_xlsx_only.py
├── ods/                           # Ihre XLSX-Dateien hier
└── csv_clockify/                  # CSV-Output hier
```

---

## Schritt 2: Paket-Installation

CachyOS ist eine Arch-basierte Distribution, daher verwenden wir den Paketmanager `pacman`, um die notwendigen Python-Bibliotheken zu installieren. Diese Version benötigt nur zwei Pakete.

```bash
# Installieren Sie pandas und openpyxl für die Excel-Verarbeitung
sudo pacman -S python-pandas python-openpyxl
```

Das ist alles! Es werden keine weiteren Abhängigkeiten oder AUR-Pakete benötigt.

---

## Schritt 3: Skript ausführbar machen

Sie müssen dem Batch-Skript einmalig Ausführungsrechte geben.

```bash
cd ~/Dokumente/vsCode/clockify_suite_arch/clockify_convert
chmod +x batch_clockify_xlsx.sh
```

---

## Schritt 4: Anwendung & Workflow

Der Prozess ist nun vollständig automatisiert.

1.  **Legen Sie Ihre XLSX-Dateien** (z.B. `25-KW48.xlsx`) in den Ordner `~/Dokumente/vsCode/clockify_suite_arch/ods`.

2.  **Führen Sie das Skript aus**:

    ```bash
    # Wechseln Sie in das Skript-Verzeichnis
    cd ~/Dokumente/vsCode/clockify_suite_arch/clockify_convert

    # Führen Sie das Batch-Skript mit Ihrer E-Mail-Adresse aus
    ./batch_clockify_xlsx.sh "ihre.email@domain.de"
    ```

3.  **Fertig!** Die fertigen CSV-Dateien für den Clockify-Import finden Sie im Ordner `~/Dokumente/vsCode/clockify_suite_arch/csv_clockify`.

---

## Schritt 5 (Optional): Alias für Bequemlichkeit

Um den Prozess weiter zu vereinfachen, können Sie einen Alias erstellen. Fügen Sie die folgende Zeile zu Ihrer `~/.zshrc` (für Zsh) oder `~/.bashrc` (für Bash) hinzu.

```bash
alias clockify=\'cd ~/Dokumente/vsCode/clockify_suite_arch/clockify_convert && ./batch_clockify_xlsx.sh "ihre.email@domain.de"\'
```

Nachdem Sie die Datei gespeichert haben, laden Sie die Konfiguration neu (`source ~/.zshrc` oder `source ~/.bashrc`). Danach können Sie von überall im System einfach den Befehl `clockify` ausführen, um den gesamten Prozess zu starten.

---

## Zusammenfassung

| Schritt                      | Befehl                                                                   |
| :--------------------------- | :----------------------------------------------------------------------- |
| 1. Ordner erstellen          | `mkdir -p ~/Dokumente/vsCode/clockify_suite_arch/{clockify_convert,ods,csv_clockify}` |
| 2. Pakete installieren       | `sudo pacman -S python-pandas python-openpyxl`                           |
| 3. Skript ausführbar machen  | `chmod +x batch_clockify_xlsx.sh`                                        |
| 4. Skript ausführen          | `./batch_clockify_xlsx.sh "ihre.email@domain.de"`                        |
| 5. (Optional) Alias setzen   | `echo "alias clockify=..." >> ~/.zshrc`                                  |

Viel Erfolg bei der Einrichtung auf CachyOS! 🚀
