#!/bin/bash
# Test-Skript für den Obsidian Migrator

echo "=== Obsidian Subnotes Migrator Test ==="
echo ""

# Stelle sicher, dass das Skript ausführbar ist
chmod +x obsidian_migrator.py

# Zeige alle Notizen im Vault
echo "Notizen im Vault:"
ls -1 example_vault/notes/
echo ""

# Test 1: Verschiebe Hauptnotiz mit allen Referenzen (kopieren)
echo "--- Test 1: Kopiere Hauptnotiz mit allen Referenzen ---"
python3 obsidian_migrator.py \
    -v example_vault/notes \
    -n "Hauptnotiz" \
    -t example_vault/export \
    --copy \
    --verbose

echo ""
echo "Ergebnis im Export-Ordner:"
ls -1 example_vault/export/
echo ""

# Aufräumen
echo "Räume auf..."
rm -rf example_vault/export/*.md

echo ""
echo "=== Test abgeschlossen ==="
