import { App, Modal, Notice, Plugin, TFile, TFolder, TAbstractFile } from 'obsidian';

interface SubnotesMigratorSettings {
	maxDepth: number;
	verbose: boolean;
}

const DEFAULT_SETTINGS: SubnotesMigratorSettings = {
	maxDepth: 10,
	verbose: false
}

export default class SubnotesMigratorPlugin extends Plugin {
	settings: SubnotesMigratorSettings;

	async onload() {
		await this.loadSettings();

		// Befehl: Aktuelle Notiz mit Referenzen verschieben
		this.addCommand({
			id: 'migrate-current-note',
			name: 'Aktuelle Notiz mit Referenzen verschieben',
			callback: () => {
				this.migrateCurrentNote();
			}
		});

		// Kontextmenü für Datei-Explorer
		this.registerEvent(
			this.app.workspace.on('file-menu', (menu, file) => {
				if (file instanceof TFile && file.extension === 'md') {
					menu.addItem((item) => {
						item
							.setTitle('Mit Referenzen verschieben')
							.setIcon('folders')
							.onClick(() => {
								this.migrateNote(file);
							});
					});
				}
			})
		);
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	migrateCurrentNote() {
		const activeFile = this.app.workspace.getActiveFile();

		if (!activeFile) {
			new Notice('Keine aktive Notiz gefunden!');
			return;
		}

		this.migrateNote(activeFile);
	}

	migrateNote(file: TFile) {
		new FolderSelectModal(this.app, async (targetFolder: string) => {
			try {
				await this.performMigration(file, targetFolder);
			} catch (error) {
				new Notice(`Fehler: ${error.message}`);
				console.error(error);
			}
		}).open();
	}

	async performMigration(sourceFile: TFile, targetFolderPath: string) {
		// Sammle alle referenzierten Notizen
		const notesToMigrate = new Set<TFile>();
		notesToMigrate.add(sourceFile);

		const visited = new Set<string>();
		await this.findAllReferences(sourceFile, notesToMigrate, visited, 0);

		// Erstelle Zielordner falls nicht vorhanden
		const targetFolder = await this.ensureFolderExists(targetFolderPath);

		// Verschiebe alle Notizen
		let successCount = 0;
		const totalCount = notesToMigrate.size;

		new Notice(`Verschiebe ${totalCount} Notiz(en)...`);

		for (const note of notesToMigrate) {
			// Überspringe wenn bereits im Zielordner
			if (note.parent?.path === targetFolder.path) {
				if (this.settings.verbose) {
					console.log(`Überspringe ${note.name} (bereits im Zielordner)`);
				}
				successCount++;
				continue;
			}

			try {
				const newPath = `${targetFolder.path}/${note.name}`;

				// Prüfe ob Datei bereits existiert
				let finalPath = newPath;
				let counter = 1;
				while (this.app.vault.getAbstractFileByPath(finalPath)) {
					const baseName = note.basename;
					finalPath = `${targetFolder.path}/${baseName}_${counter}.md`;
					counter++;
				}

				await this.app.fileManager.renameFile(note, finalPath);
				successCount++;

				if (this.settings.verbose) {
					console.log(`✓ Verschoben: ${note.name}`);
				}
			} catch (error) {
				console.error(`Fehler beim Verschieben von ${note.name}:`, error);
			}
		}

		new Notice(`Erfolgreich: ${successCount}/${totalCount} Notizen verschoben`);
	}

	async findAllReferences(
		file: TFile,
		allNotes: Set<TFile>,
		visited: Set<string>,
		depth: number
	) {
		if (depth > this.settings.maxDepth) {
			if (this.settings.verbose) {
				console.log(`Maximale Tiefe erreicht bei ${file.name}`);
			}
			return;
		}

		if (visited.has(file.path)) {
			return;
		}
		visited.add(file.path);

		// Lese Dateiinhalt
		const content = await this.app.vault.read(file);

		// Finde alle [[...]]-Referenzen
		const linkPattern = /\[\[([^\]|]+)(?:\|[^\]]+)?\]\]/g;
		const matches = content.matchAll(linkPattern);

		for (const match of matches) {
			const linkText = match[1].trim();

			// Finde die referenzierte Datei
			const linkedFile = this.app.metadataCache.getFirstLinkpathDest(linkText, file.path);

			if (linkedFile instanceof TFile && linkedFile.extension === 'md') {
				if (!allNotes.has(linkedFile)) {
					allNotes.add(linkedFile);

					if (this.settings.verbose) {
						console.log(`${'  '.repeat(depth)}└─ Gefunden: ${linkedFile.name}`);
					}

					// Rekursiv weitergehen
					await this.findAllReferences(linkedFile, allNotes, visited, depth + 1);
				}
			} else if (this.settings.verbose && !linkedFile) {
				console.log(`${'  '.repeat(depth)}└─ Nicht gefunden: ${linkText}`);
			}
		}
	}

	async ensureFolderExists(folderPath: string): Promise<TFolder> {
		const folder = this.app.vault.getAbstractFileByPath(folderPath);

		if (folder instanceof TFolder) {
			return folder;
		}

		// Erstelle Ordner rekursiv
		await this.app.vault.createFolder(folderPath);
		const newFolder = this.app.vault.getAbstractFileByPath(folderPath);

		if (newFolder instanceof TFolder) {
			return newFolder;
		}

		throw new Error(`Konnte Ordner nicht erstellen: ${folderPath}`);
	}
}

class FolderSelectModal extends Modal {
	private onSubmit: (folder: string) => void;
	private inputEl: HTMLInputElement;
	private folders: string[];

	constructor(app: App, onSubmit: (folder: string) => void) {
		super(app);
		this.onSubmit = onSubmit;
		this.folders = this.getAllFolders();
	}

	getAllFolders(): string[] {
		const folders: string[] = ['/']; // Root-Ordner

		this.app.vault.getAllLoadedFiles().forEach((file: TAbstractFile) => {
			if (file instanceof TFolder) {
				folders.push(file.path);
			}
		});

		return folders.sort();
	}

	onOpen() {
		const { contentEl } = this;
		contentEl.empty();

		contentEl.createEl('h2', { text: 'Zielordner auswählen' });

		// Input-Feld mit Autocomplete
		const inputContainer = contentEl.createDiv({ cls: 'folder-input-container' });

		inputContainer.createEl('label', {
			text: 'Zielordner:',
			cls: 'folder-label'
		});

		this.inputEl = inputContainer.createEl('input', {
			type: 'text',
			placeholder: 'z.B. Archive/Projects',
			cls: 'folder-input'
		});

		// Autocomplete-Liste
		const suggestionsEl = contentEl.createDiv({ cls: 'folder-suggestions' });

		this.inputEl.addEventListener('input', () => {
			const value = this.inputEl.value.toLowerCase();
			suggestionsEl.empty();

			if (value.length > 0) {
				const matches = this.folders.filter(f =>
					f.toLowerCase().includes(value)
				).slice(0, 10);

				matches.forEach(folder => {
					const suggestionEl = suggestionsEl.createDiv({
						cls: 'folder-suggestion',
						text: folder
					});

					suggestionEl.addEventListener('click', () => {
						this.inputEl.value = folder;
						suggestionsEl.empty();
					});
				});
			}
		});

		// Buttons
		const buttonContainer = contentEl.createDiv({ cls: 'modal-button-container' });

		const submitBtn = buttonContainer.createEl('button', {
			text: 'OK',
			cls: 'mod-cta'
		});

		submitBtn.addEventListener('click', () => {
			const folder = this.inputEl.value.trim();

			if (folder) {
				this.close();
				this.onSubmit(folder);
			} else {
				new Notice('Bitte einen Ordner eingeben!');
			}
		});

		const cancelBtn = buttonContainer.createEl('button', {
			text: 'Abbrechen'
		});

		cancelBtn.addEventListener('click', () => {
			this.close();
		});

		// Enter-Taste für Submit
		this.inputEl.addEventListener('keydown', (e) => {
			if (e.key === 'Enter') {
				submitBtn.click();
			}
		});

		// Fokus auf Input
		this.inputEl.focus();
	}

	onClose() {
		const { contentEl } = this;
		contentEl.empty();
	}
}
