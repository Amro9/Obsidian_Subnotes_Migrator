# Obsidian Subnotes Migrator

Ein Python-Tool zum Verschieben oder Kopieren von Obsidian-Notizen zusammen mit allen referenzierten Notizen.

## Funktionen

- **Automatisches Erkennen von Referenzen**: Findet alle `[[Notizname]]` und `[[Notizname|Alias]]` Verlinkungen
- **Rekursive Suche**: Optional können alle Sub-Referenzen (Referenzen von Referenzen) eingeschlossen werden
- **Flexible Modi**: Verschieben oder Kopieren von Notizen
- **Tiefenkontrolle**: Maximale Rekursionstiefe konfigurierbar
- **Sichere Operation**: Automatisches Umbenennen bei Datei-Konflikten
- **Detaillierte Ausgabe**: Verbose-Modus für debugging

## Installation

Keine externe Abhängigkeiten erforderlich! Das Tool nutzt nur Python Standard-Bibliotheken.

```bash
# Repository klonen
git clone https://github.com/Amro9/Obsidian_Subnotes_Migrator.git
cd Obsidian_Subnotes_Migrator

# Skript ausführbar machen
chmod +x obsidian_migrator.py
```

## Verwendung

### Grundlegende Syntax

```bash
python3 obsidian_migrator.py -v <VAULT_PATH> -n <NOTE_NAME> -t <TARGET_DIR> [OPTIONEN]
```

### Parameter

- `-v, --vault`: Pfad zum Obsidian-Vault (Haupt-Notizen-Ordner) **[erforderlich]**
- `-n, --note`: Name oder Pfad der zu verschiebenden Notiz **[erforderlich]**
- `-t, --target`: Ziel-Verzeichnis **[erforderlich]**
- `--no-references`: Keine referenzierten Notizen einschließen
- `--no-recursive`: Nicht rekursiv (nur direkte Referenzen)
- `--copy`: Kopieren statt Verschieben
- `--max-depth`: Maximale Rekursionstiefe (Standard: 10)
- `--verbose`: Detaillierte Ausgabe

### Beispiele

#### 1. Notiz mit allen Referenzen verschieben (rekursiv)

```bash
python3 obsidian_migrator.py \
    -v ~/Obsidian/MeinVault \
    -n "Projektplanung" \
    -t ~/Obsidian/Archiv/Projekte
```

Dies verschiebt:
- Die Notiz "Projektplanung.md"
- Alle direkt referenzierten Notizen
- Alle indirekt referenzierten Notizen (rekursiv)

#### 2. Nur direkte Referenzen (nicht rekursiv)

```bash
python3 obsidian_migrator.py \
    -v ~/Obsidian/MeinVault \
    -n "Meeting Notes" \
    -t ~/Obsidian/Archiv \
    --no-recursive
```

#### 3. Nur eine einzelne Notiz (ohne Referenzen)

```bash
python3 obsidian_migrator.py \
    -v ~/Obsidian/MeinVault \
    -n "Standalone" \
    -t ~/Obsidian/Archiv \
    --no-references
```

#### 4. Kopieren statt Verschieben

```bash
python3 obsidian_migrator.py \
    -v ~/Obsidian/MeinVault \
    -n "Wichtige Notiz" \
    -t ~/Obsidian/Backup \
    --copy
```

#### 5. Mit detaillierter Ausgabe

```bash
python3 obsidian_migrator.py \
    -v ~/Obsidian/MeinVault \
    -n "Debug Test" \
    -t ~/Obsidian/Export \
    --verbose
```

## Test-Beispiel ausführen

Ein vollständiges Test-Beispiel ist enthalten:

```bash
# Test-Skript ausführen
chmod +x test_example.sh
./test_example.sh
```

Dies erstellt einen Beispiel-Vault mit mehreren vernetzten Notizen und demonstriert die Funktionalität.

## Beispiel-Szenario

Angenommen du hast folgende Notizen-Struktur:

```
Obsidian Vault/
├── Hauptnotiz.md          → referenziert [[Konzept]] und [[Implementation]]
├── Konzept.md             → referenziert [[Anforderungen]]
├── Implementation.md      → referenziert [[Konzept]] und [[Architektur]]
├── Architektur.md
├── Anforderungen.md
└── Unrelated.md           → keine Referenzen
```

Wenn du `Hauptnotiz.md` mit allen Referenzen verschiebst:

```bash
python3 obsidian_migrator.py \
    -v "Obsidian Vault" \
    -n "Hauptnotiz" \
    -t "Projekt Export"
```

Werden folgende Dateien verschoben:
- ✓ Hauptnotiz.md
- ✓ Konzept.md
- ✓ Implementation.md
- ✓ Architektur.md
- ✓ Anforderungen.md
- ✗ Unrelated.md (nicht referenziert, bleibt)

## Programmierdetails

### Klasse: `ObsidianMigrator`

#### Hauptmethoden

**`__init__(vault_path, verbose=False)`**
- Initialisiert den Migrator mit dem Vault-Pfad

**`find_note_file(note_name)`**
- Sucht eine Notiz im gesamten Vault
- Unterstützt Namen mit/ohne .md-Endung

**`extract_references(note_path)`**
- Extrahiert alle [[...]]-Referenzen aus einer Notiz
- Nutzt Regex: `\[\[([^\]|]+)(?:\|[^\]]+)?\]\]`

**`find_all_references(note_path, recursive=True, max_depth=10)`**
- Findet alle referenzierten Notizen
- Optional rekursiv mit Tiefenkontrolle
- Verhindert Endlosschleifen

**`migrate_notes(source_note, target_dir, ...)`**
- Hauptfunktion zum Verschieben/Kopieren
- Sammelt alle zu migrierenden Notizen
- Führt die Operation aus mit Fehlerbehandlung

## Hinweise

- **Verlinkungen**: Das Tool aktualisiert momentan keine Links in den verschobenen Notizen. Die Links bleiben im Format `[[Original]]` erhalten.
- **Datei-Konflikte**: Bei existierenden Dateien wird automatisch umbenannt (z.B. `Notiz_1.md`, `Notiz_2.md`)
- **Sicherheit**: Im Kopier-Modus bleiben die Originale unverändert
- **Performance**: Bei sehr großen Vaults kann die Suche etwas dauern

## Lizenz

MIT License - siehe LICENSE Datei für Details

## Autor

Entwickelt für die einfache Migration von Obsidian-Notizen mit ihren Abhängigkeiten.

## Beitragen

Pull Requests und Issues sind willkommen!

### Mögliche Erweiterungen

- Link-Aktualisierung nach dem Verschieben
- GUI-Interface
- Batch-Verarbeitung mehrerer Notizen
- Export-Format-Optionen (z.B. als ZIP)
- Dry-run Modus (zeigt was passieren würde, ohne es auszuführen)
- Unterstützung für Attachments (Bilder, PDFs, etc.)
