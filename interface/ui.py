import os
from tkinter import (
    Tk,
    Frame,
    Button,
    Label,
    Listbox,
    Scrollbar,
    SINGLE,
    MULTIPLE,
    END,
    filedialog,
    messagebox,
    RIGHT,
    LEFT,
    Y,
    BOTH,
    Text,
)
from tkinter import ttk
from src.client_logic import ClientLogic


class ApplicationUI:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Gestion de contexte projet")

        # --- Activation d'un thème moderne ---
        style = ttk.Style()
        style.theme_use("clam")

        self.client = ClientLogic()

        self.frame_left = Frame(root)
        self.frame_right = Frame(root)

        self.preview_text = None  # zone de prévisualisation

        self._build_layout()

    def _build_layout(self):
        self.frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # -------------------------
        # COLONNE GAUCHE
        # -------------------------
        Label(self.frame_left, text="Projet", font=("Segoe UI", 11, "bold")).pack(pady=5)
        ttk.Button(self.frame_left, text="Sélectionner un dossier", command=self.on_select_project).pack(pady=5)
        ttk.Button(self.frame_left, text="Ouvrir le dossier sélectionné", command=self.on_open_folder).pack(pady=5)

        Label(self.frame_left, text="Extraction complète", font=("Segoe UI", 11, "bold")).pack(pady=5)
        ttk.Button(self.frame_left, text="Extraire l'ensemble du projet", command=self.on_extract_full).pack(pady=5)

        Label(self.frame_left, text="Versions disponibles", font=("Segoe UI", 11, "bold")).pack(pady=5)

        # --- Frame versions + scrollbar ---
        frame_versions = Frame(self.frame_left)
        frame_versions.pack(fill="both", expand=True)

        self.list_versions = Listbox(frame_versions, selectmode=SINGLE, height=10)
        self.list_versions.pack(side=LEFT, fill=BOTH, expand=True)

        scroll_versions = Scrollbar(frame_versions, orient="vertical", command=self.list_versions.yview)
        scroll_versions.pack(side=RIGHT, fill=Y)

        self.list_versions.config(yscrollcommand=scroll_versions.set)
        self.list_versions.bind("<<ListboxSelect>>", self.on_select_version)

        ttk.Button(self.frame_left, text="Restaurer la version sélectionnée", command=self.on_restore_full).pack(pady=5)
        ttk.Button(self.frame_left, text="Supprimer la version sélectionnée", command=self.on_delete_version).pack(pady=5)

        # -------------------------
        # COLONNE DROITE
        # -------------------------
        Label(self.frame_right, text="Fichiers de la version sélectionnée", font=("Segoe UI", 11, "bold")).pack(pady=5)

        # --- Frame files + scrollbar ---
        frame_files = Frame(self.frame_right)
        frame_files.pack(fill="both", expand=False)

        self.list_files = Listbox(frame_files, selectmode=MULTIPLE, height=12)
        self.list_files.pack(side=LEFT, fill=BOTH, expand=True)

        scroll_files = Scrollbar(frame_files, orient="vertical", command=self.list_files.yview)
        scroll_files.pack(side=RIGHT, fill=Y)

        self.list_files.config(yscrollcommand=scroll_files.set)
        self.list_files.bind("<<ListboxSelect>>", self.on_file_selected)

        # -------------------------
        # PRÉVISUALISATION
        # -------------------------
        Label(self.frame_right, text="Prévisualisation du fichier", font=("Segoe UI", 11, "bold")).pack(pady=5)

        frame_preview = Frame(self.frame_right)
        frame_preview.pack(fill="both", expand=True)

        self.preview_text = Text(frame_preview, wrap="word", height=20)
        self.preview_text.pack(side=LEFT, fill=BOTH, expand=True)

        scroll_preview = Scrollbar(frame_preview, orient="vertical", command=self.preview_text.yview)
        scroll_preview.pack(side=RIGHT, fill=Y)

        self.preview_text.config(yscrollcommand=scroll_preview.set)

        # -------------------------
        # ACTIONS SUR LES FICHIERS
        # -------------------------
        ttk.Button(self.frame_right, text="Créer selected_context.md & .html", command=self.on_export_selected).pack(pady=5)
        ttk.Button(self.frame_right, text="Restaurer les fichiers sélectionnés", command=self.on_restore_selected).pack(pady=5)

    # -------------------------
    # ACTIONS COLONNE GAUCHE
    # -------------------------

    def on_select_project(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        self.client.select_project(folder)
        messagebox.showinfo("Projet sélectionné", f"Dossier : {folder}")
        self.refresh_versions()

    def on_open_folder(self):
        try:
            self.client.open_project_folder()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def on_extract_full(self):
        if not self.client.has_project():
            messagebox.showerror("Erreur", "Aucun projet sélectionné.")
            return
        version = self.client.extract_full_project()
        messagebox.showinfo("Extraction terminée", f"Version créée : {version}")
        self.refresh_versions()
        self.select_version_in_list(version)

    def refresh_versions(self):
        self.list_versions.delete(0, END)
        versions = self.client.get_available_versions()
        for v in versions:
            self.list_versions.insert(END, v)

    def on_select_version(self, event=None):
        selection = self.list_versions.curselection()
        if not selection:
            return
        index = selection[0]
        version = self.list_versions.get(index)
        self.client.select_version(version)
        self.refresh_files()

    def on_restore_full(self):
        try:
            self.client.restore_full_version()
            messagebox.showinfo("Restauration", "Restauration complète effectuée.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def on_delete_version(self):
        self.client.delete_selected_version()
        self.refresh_versions()
        self.list_files.delete(0, END)
        self.preview_text.delete(1.0, END)

    # -------------------------
    # ACTIONS COLONNE DROITE
    # -------------------------

    def refresh_files(self):
        self.list_files.delete(0, END)
        files = self.client.get_files_from_selected_version()
        for f in files:
            self.list_files.insert(END, f)
        self.preview_text.delete(1.0, END)

    def on_file_selected(self, event=None):
        selection = self.list_files.curselection()
        if not selection:
            self.preview_text.delete(1.0, END)
            return

        index = selection[0]
        filename = self.list_files.get(index)

        snapshot = self.client.server.load_snapshot(self.client.selected_version)
        content = snapshot.files_content.get(filename, "")

        self.preview_text.delete(1.0, END)
        self.preview_text.insert(END, content)

    def on_export_selected(self):
        selected_indices = self.list_files.curselection()
        files = [self.list_files.get(i) for i in selected_indices]
        self.client.set_selected_files(files)
        self.client.export_selected_markdown_and_html()
        messagebox.showinfo("Export", "selected_context.md et selected_context.html générés.")

    def on_restore_selected(self):
        selected_indices = self.list_files.curselection()
        files = [self.list_files.get(i) for i in selected_indices]
        self.client.set_selected_files(files)
        self.client.restore_selected_files()
        messagebox.showinfo("Restauration", "Fichiers sélectionnés restaurés.")

    # -------------------------
    # HELPERS
    # -------------------------

    def select_version_in_list(self, version: str):
        for i in range(self.list_versions.size()):
            if self.list_versions.get(i) == version:
                self.list_versions.selection_clear(0, END)
                self.list_versions.selection_set(i)
                self.list_versions.activate(i)
                self.on_select_version()
                break
