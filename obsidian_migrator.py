#!/usr/bin/env python3
"""
Obsidian Subnotes Migrator

Ein Tool zum Verschieben von Obsidian-Notizen zusammen mit allen referenzierten Notizen.
"""

import re
import os
import shutil
import argparse
from pathlib import Path
from typing import Set, List, Tuple


class ObsidianMigrator:
    """Hauptklasse für das Migrieren von Obsidian-Notizen mit Referenzen."""

    # Regex-Pattern für Obsidian-Links: [[Notizname]] oder [[Notizname|Alias]]
    LINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')

    def __init__(self, vault_path: str, verbose: bool = False):
        """
        Initialisiert den Migrator.

        Args:
            vault_path: Pfad zum Obsidian-Vault (Haupt-Notizen-Ordner)
            verbose: Detaillierte Ausgabe aktivieren
        """
        self.vault_path = Path(vault_path).resolve()
        self.verbose = verbose

        if not self.vault_path.exists():
            raise ValueError(f"Vault-Pfad existiert nicht: {vault_path}")

        if self.verbose:
            print(f"Vault-Pfad: {self.vault_path}")

    def find_note_file(self, note_name: str) -> Path | None:
        """
        Findet eine Notiz-Datei im Vault.

        Args:
            note_name: Name der Notiz (mit oder ohne .md-Endung)

        Returns:
            Pfad zur Notiz-Datei oder None wenn nicht gefunden
        """
        # Normalisiere den Notiz-Namen
        if not note_name.endswith('.md'):
            note_name_md = f"{note_name}.md"
        else:
            note_name_md = note_name
            note_name = note_name[:-3]

        # Suche im gesamten Vault
        for root, dirs, files in os.walk(self.vault_path):
            if note_name_md in files:
                return Path(root) / note_name_md
            # Auch ohne .md suchen für den Fall
            if note_name in files:
                return Path(root) / note_name

        return None

    def extract_references(self, note_path: Path) -> Set[str]:
        """
        Extrahiert alle Referenzen aus einer Notiz.

        Args:
            note_path: Pfad zur Notiz-Datei

        Returns:
            Set mit allen referenzierten Notiz-Namen
        """
        if not note_path.exists():
            return set()

        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            if self.verbose:
                print(f"Fehler beim Lesen von {note_path}: {e}")
            return set()

        # Finde alle [[...]]-Referenzen
        matches = self.LINK_PATTERN.findall(content)

        if self.verbose and matches:
            print(f"  Gefundene Referenzen in {note_path.name}: {matches}")

        return set(matches)

    def find_all_references(self, note_path: Path, recursive: bool = True,
                          max_depth: int = 10) -> Set[Path]:
        """
        Findet alle referenzierten Notizen (optional rekursiv).

        Args:
            note_path: Pfad zur Start-Notiz
            recursive: Rekursiv alle Sub-Referenzen finden
            max_depth: Maximale Rekursionstiefe

        Returns:
            Set mit Pfaden aller referenzierten Notizen
        """
        all_references = set()
        visited = set()

        def _find_recursive(current_path: Path, depth: int = 0):
            if depth > max_depth:
                if self.verbose:
                    print(f"  Maximale Tiefe erreicht bei {current_path.name}")
                return

            # Verhindere Schleifen
            if current_path in visited:
                return
            visited.add(current_path)

            # Extrahiere Referenzen aus aktueller Notiz
            ref_names = self.extract_references(current_path)

            for ref_name in ref_names:
                ref_path = self.find_note_file(ref_name)

                if ref_path and ref_path not in all_references:
                    all_references.add(ref_path)

                    if self.verbose:
                        print(f"  {'  ' * depth}└─ Gefunden: {ref_path.name}")

                    # Rekursiv weitergehen wenn gewünscht
                    if recursive and ref_path != note_path:
                        _find_recursive(ref_path, depth + 1)
                elif not ref_path and self.verbose:
                    print(f"  {'  ' * depth}└─ Nicht gefunden: {ref_name}")

        _find_recursive(note_path)
        return all_references

    def migrate_notes(self, source_note: str, target_dir: str,
                     include_references: bool = True,
                     recursive: bool = True,
                     copy_mode: bool = False,
                     max_depth: int = 10) -> Tuple[int, List[str]]:
        """
        Verschiebt oder kopiert eine Notiz mit optional allen Referenzen.

        Args:
            source_note: Name oder Pfad der Quell-Notiz
            target_dir: Ziel-Verzeichnis
            include_references: Referenzierte Notizen auch migrieren
            recursive: Rekursiv alle Sub-Referenzen einschließen
            copy_mode: Kopieren statt Verschieben
            max_depth: Maximale Rekursionstiefe

        Returns:
            Tuple (Anzahl migrierte Notizen, Liste der migrierten Dateinamen)
        """
        # Finde die Quell-Notiz
        if os.path.isfile(source_note):
            source_path = Path(source_note).resolve()
        else:
            source_path = self.find_note_file(source_note)

        if not source_path:
            raise ValueError(f"Notiz nicht gefunden: {source_note}")

        # Erstelle Ziel-Verzeichnis
        target_path = Path(target_dir).resolve()
        target_path.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            print(f"\n{'Kopiere' if copy_mode else 'Verschiebe'} Notiz: {source_path.name}")
            print(f"Nach: {target_path}")

        # Sammle alle zu migrierenden Notizen
        notes_to_migrate = {source_path}

        if include_references:
            if self.verbose:
                print(f"\nSuche referenzierte Notizen (rekursiv={recursive})...")
            references = self.find_all_references(source_path, recursive, max_depth)
            notes_to_migrate.update(references)

        # Migriere alle Notizen
        migrated = []
        operation = shutil.copy2 if copy_mode else shutil.move
        operation_name = "Kopiert" if copy_mode else "Verschoben"

        print(f"\n{operation_name.replace('t', 'e')} {len(notes_to_migrate)} Notiz(en):")

        for note_path in sorted(notes_to_migrate):
            target_file = target_path / note_path.name

            # Überspringe wenn Quelle = Ziel
            if note_path.parent == target_path:
                if self.verbose:
                    print(f"  ⊘ Überspringe {note_path.name} (bereits im Zielordner)")
                continue

            try:
                # Wenn Datei bereits existiert, umbenennen
                if target_file.exists():
                    base = target_file.stem
                    suffix = target_file.suffix
                    counter = 1
                    while target_file.exists():
                        target_file = target_path / f"{base}_{counter}{suffix}"
                        counter += 1
                    if self.verbose:
                        print(f"  ! Datei existiert bereits, umbenannt zu: {target_file.name}")

                operation(str(note_path), str(target_file))
                migrated.append(note_path.name)
                print(f"  ✓ {note_path.name}")

            except Exception as e:
                print(f"  ✗ Fehler bei {note_path.name}: {e}")

        print(f"\n{operation_name}: {len(migrated)}/{len(notes_to_migrate)} Notizen")
        return len(migrated), migrated


def main():
    """CLI-Hauptfunktion."""
    parser = argparse.ArgumentParser(
        description='Obsidian Subnotes Migrator - Verschiebt Notizen mit allen Referenzen',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Notiz mit allen Referenzen verschieben
  %(prog)s -v /pfad/zum/vault -n "Meine Notiz" -t /pfad/zum/ziel

  # Nur die Hauptnotiz verschieben (ohne Referenzen)
  %(prog)s -v /vault -n "Notiz.md" -t /ziel --no-references

  # Kopieren statt Verschieben
  %(prog)s -v /vault -n "Notiz" -t /ziel --copy

  # Nicht-rekursiv (nur direkte Referenzen)
  %(prog)s -v /vault -n "Notiz" -t /ziel --no-recursive
        """
    )

    parser.add_argument('-v', '--vault', required=True,
                       help='Pfad zum Obsidian-Vault (Haupt-Notizen-Ordner)')
    parser.add_argument('-n', '--note', required=True,
                       help='Name oder Pfad der zu verschiebenden Notiz')
    parser.add_argument('-t', '--target', required=True,
                       help='Ziel-Verzeichnis')
    parser.add_argument('--no-references', action='store_true',
                       help='Keine referenzierten Notizen einschließen')
    parser.add_argument('--no-recursive', action='store_true',
                       help='Nicht rekursiv (nur direkte Referenzen)')
    parser.add_argument('--copy', action='store_true',
                       help='Kopieren statt Verschieben')
    parser.add_argument('--max-depth', type=int, default=10,
                       help='Maximale Rekursionstiefe (Standard: 10)')
    parser.add_argument('--verbose', action='store_true',
                       help='Detaillierte Ausgabe')

    args = parser.parse_args()

    try:
        migrator = ObsidianMigrator(args.vault, verbose=args.verbose)

        count, migrated = migrator.migrate_notes(
            source_note=args.note,
            target_dir=args.target,
            include_references=not args.no_references,
            recursive=not args.no_recursive,
            copy_mode=args.copy,
            max_depth=args.max_depth
        )

        print(f"\n✓ Erfolgreich abgeschlossen!")
        return 0

    except Exception as e:
        print(f"\n✗ Fehler: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
