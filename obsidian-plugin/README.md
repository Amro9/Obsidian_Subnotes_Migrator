# Obsidian Subnotes Migrator Plugin

Ein Obsidian Plugin zum Verschieben von Notizen zusammen mit allen referenzierten Notizen direkt in Obsidian.

## Features

- **Ein Klick genügt**: Verschiebe die aktuelle Notiz mit einem Befehl
- **Automatische Referenzen**: Findet rekursiv alle `[[verlinkten]]` Notizen
- **Ordnerauswahl-Dialog**: Einfache Auswahl des Zielordners mit Autocomplete
- **Intelligente Konfliktvermeidung**: Benennt Dateien automatisch um, wenn sie bereits existieren
- **Command Palette Integration**: Verfügbar über die Command Palette (`Ctrl/Cmd + P`)
- **Kontextmenü**: Rechtsklick auf Dateien im Explorer

## Installation

### Methode 1: Manuelle Installation (Entwicklung)

1. **Plugin-Ordner finden**
   - Öffne dein Obsidian Vault
   - Navigiere zu `.obsidian/plugins/` (versteckter Ordner!)
   - Falls der Ordner nicht existiert, erstelle ihn

2. **Plugin kopieren**
   ```bash
   # Im Projekt-Verzeichnis
   cd obsidian-plugin

   # Dependencies installieren
   npm install

   # Plugin bauen
   npm run build
   ```

3. **Dateien kopieren**
   Kopiere diese drei Dateien in `.obsidian/plugins/subnotes-migrator/`:
   - `main.js` (wird durch build erstellt)
   - `manifest.json`
   - `styles.css`

4. **Plugin aktivieren**
   - Öffne Obsidian
   - Gehe zu Einstellungen → Community Plugins
   - Deaktiviere "Safe Mode" falls nötig
   - Klicke "Reload Plugins"
   - Aktiviere "Subnotes Migrator"

### Methode 2: Schnellinstallation (ohne Build)

Wenn du TypeScript nicht kompilieren möchtest, kannst du auch direkt eine JavaScript-Version erstellen:

1. Erstelle den Ordner `.obsidian/plugins/subnotes-migrator/` in deinem Vault

2. Konvertiere `main.ts` zu `main.js` (entferne TypeScript-Typen):

```bash
# Automatisch mit npm (nachdem du npm install gemacht hast)
npm run build
```

3. Kopiere `main.js`, `manifest.json` und `styles.css` in den Plugin-Ordner

4. Aktiviere das Plugin in Obsidian

### Methode 3: Direktlink (für Entwicklung)

Für einfaches Entwickeln kannst du einen Symlink erstellen:

```bash
# Linux/Mac
ln -s /pfad/zum/repo/obsidian-plugin ~/.obsidian/plugins/subnotes-migrator

# Windows (als Administrator)
mklink /D "%USERPROFILE%\.obsidian\plugins\subnotes-migrator" "C:\pfad\zum\repo\obsidian-plugin"
```

## Verwendung

### Option 1: Command Palette

1. Öffne die Notiz, die du verschieben möchtest
2. Drücke `Ctrl/Cmd + P` für die Command Palette
3. Tippe "Aktuelle Notiz mit Referenzen verschieben"
4. Wähle den Zielordner aus
5. Klicke "OK"

### Option 2: Kontextmenü

1. Rechtsklick auf eine Notiz im Datei-Explorer
2. Wähle "Mit Referenzen verschieben"
3. Wähle den Zielordner aus
4. Klicke "OK"

## Wie es funktioniert

Das Plugin analysiert die aktuell ausgewählte Notiz und:

1. **Findet alle Referenzen**: Sucht nach `[[Notizname]]` und `[[Notizname|Alias]]` Links
2. **Rekursive Analyse**: Untersucht auch die referenzierten Notizen nach weiteren Links
3. **Vermeidet Duplikate**: Jede Notiz wird nur einmal verarbeitet
4. **Tiefenkontrolle**: Standardmäßig max. 10 Ebenen tief (konfigurierbar)
5. **Verschiebt alles**: Alle gefundenen Notizen werden in den Zielordner verschoben

### Beispiel

Wenn du diese Struktur hast:

```
Vault/
├── Hauptnotiz.md          → verlinkt [[Konzept]] und [[Implementation]]
├── Konzept.md             → verlinkt [[Anforderungen]]
├── Implementation.md      → verlinkt [[Konzept]] und [[Architektur]]
├── Architektur.md
└── Anforderungen.md
```

Und du verschiebst `Hauptnotiz.md` nach `Archive/Project/`, dann werden verschoben:
- ✓ Hauptnotiz.md
- ✓ Konzept.md
- ✓ Implementation.md
- ✓ Architektur.md
- ✓ Anforderungen.md

## Einstellungen

Die Einstellungen können in der `main.ts` angepasst werden:

```typescript
const DEFAULT_SETTINGS = {
	maxDepth: 10,      // Maximale Rekursionstiefe
	verbose: false     // Detaillierte Konsolen-Logs
}
```

## Entwicklung

### Voraussetzungen

- Node.js (v16 oder höher)
- npm

### Setup

```bash
# Dependencies installieren
npm install

# Development Mode (mit Hot Reload)
npm run dev

# Production Build
npm run build
```

### Projekt-Struktur

```
obsidian-plugin/
├── main.ts              # Haupt-Plugin-Code
├── manifest.json        # Plugin-Metadaten
├── styles.css           # Styling für Modal
├── package.json         # npm Dependencies
├── tsconfig.json        # TypeScript Config
├── esbuild.config.mjs   # Build Config
└── README.md            # Diese Datei
```

## Troubleshooting

### Plugin erscheint nicht in der Liste

- Stelle sicher, dass der Ordner `.obsidian/plugins/subnotes-migrator/` existiert
- Prüfe, ob alle drei Dateien vorhanden sind: `main.js`, `manifest.json`, `styles.css`
- Klicke "Reload Plugins" in den Einstellungen

### "Keine aktive Notiz gefunden"

- Stelle sicher, dass eine Markdown-Notiz geöffnet ist
- Klicke in die Notiz, um sie zu fokussieren

### Referenzen werden nicht gefunden

- Das Plugin sucht nur nach `[[Wikilinks]]`-Format
- Markdown-Links `[text](file.md)` werden nicht unterstützt
- Prüfe die Konsole (`Ctrl/Cmd + Shift + I`) für Debug-Informationen

## Bekannte Einschränkungen

- **Links werden nicht aktualisiert**: Nach dem Verschieben bleiben die Links im Format `[[Original]]` erhalten. Du musst Links manuell anpassen oder ein anderes Plugin verwenden.
- **Nur Markdown**: Aktuell werden nur `.md`-Dateien verschoben, keine Anhänge (Bilder, PDFs, etc.)
- **Nur Wikilinks**: Standard-Markdown-Links werden nicht erkannt

## Zukünftige Features

- [ ] Link-Aktualisierung nach dem Verschieben
- [ ] Support für Anhänge (Bilder, PDFs)
- [ ] Einstellungs-Tab in Obsidian
- [ ] Kopier-Modus (statt Verschieben)
- [ ] Dry-Run (Vorschau ohne Aktion)
- [ ] Batch-Verarbeitung mehrerer Notizen

## Lizenz

MIT License

## Support

Bei Problemen oder Feature-Requests erstelle bitte ein Issue auf GitHub.

## Credits

Basierend auf dem Python-Tool [Obsidian Subnotes Migrator](https://github.com/Amro9/Obsidian_Subnotes_Migrator)
