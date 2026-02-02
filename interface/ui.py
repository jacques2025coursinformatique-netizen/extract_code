import os
from tkinter import (
    Tk,
    Frame,
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

from data.queries_manager import QueriesManager
from src.queries_logic import QueriesLogic
from interface.ui_queries import QueriesUI


class ApplicationUI:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title("Gestion de contexte projet")

        # --- Thème moderne ---
        style = ttk.Style()
        style.theme_use("clam")

        self.client = ClientLogic()

        # Manager / logique pour les requêtes type
        self._init_queries_module()

        # Widgets principaux
        self.preview_text = None
        self.list_versions = None
        self.list_files = None

        self.memo_query = None
        self.memo_version = None
        self.queries_logic.ui = self

        self._build_layout()




    # -------------------------------------------------------------------------
    #  INITIALISATION MODULE REQUÊTES TYPE
    # -------------------------------------------------------------------------
    def _init_queries_module(self):
        self.queries_manager = QueriesManager()

        def copy_to_clipboard(text: str):
            self.root.clipboard_clear()
            self.root.clipboard_append(text)

        def get_selected_files():
            return self.get_selected_files()

        self.queries_logic = QueriesLogic(
            manager=self.queries_manager,
            copy_to_clipboard=copy_to_clipboard,
            get_selected_files=get_selected_files,
        )

        self.queries_ui = None  # sera créé dans le layout

    # -------------------------------------------------------------------------
    #  LAYOUT GLOBAL : PANEDWINDOW + NOTEBOOK + COLONNE DROITE
    # -------------------------------------------------------------------------
    def _build_layout(self):
        # PanedWindow horizontal : gauche = Notebook, droite = fichiers/preview
        paned = ttk.PanedWindow(self.root, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Frame gauche : Notebook
        frame_left = Frame(paned)
        paned.add(frame_left, weight=1)

        # Frame droite : fichiers + preview
        frame_right = Frame(paned)
        paned.add(frame_right, weight=2)

        # ---------------------------------------------------------------------
        # NOTEBOOK À GAUCHE : Onglet Projet + Onglet Requêtes type
        # ---------------------------------------------------------------------
        self.notebook = ttk.Notebook(frame_left)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Onglet Projet
        self.tab_project = Frame(self.notebook)
        self.notebook.add(self.tab_project, text="Projet")

        # Onglet Requêtes type
        self.tab_queries = Frame(self.notebook)
        self.notebook.add(self.tab_queries, text="Requêtes type")

        # Construire le contenu de l’onglet Projet
        self._build_project_tab(self.tab_project)

        # Construire le contenu de l’onglet Requêtes type
        self._build_queries_tab(self.tab_queries)

        # ---------------------------------------------------------------------
        # COLONNE DROITE : Fichiers + Prévisualisation + Actions
        # ---------------------------------------------------------------------
        self._build_right_column(frame_right)

    # -------------------------------------------------------------------------
    #  ONGLET PROJET
    # -------------------------------------------------------------------------
    def _build_project_tab(self, parent: Frame):
        Label(parent, text="Projet", font=("Segoe UI", 11, "bold")).pack(pady=5)
        ttk.Button(parent, text="Sélectionner un dossier", command=self.on_select_project).pack(pady=5)
        ttk.Button(parent, text="Ouvrir le dossier sélectionné", command=self.on_open_folder).pack(pady=5)

        Label(parent, text="Extraction complète", font=("Segoe UI", 11, "bold")).pack(pady=5)
        ttk.Button(parent, text="Extraire l'ensemble du projet", command=self.on_extract_full).pack(pady=5)

        Label(parent, text="Versions disponibles", font=("Segoe UI", 11, "bold")).pack(pady=5)

        frame_versions = Frame(parent)
        frame_versions.pack(fill="both", expand=True)

        self.list_versions = Listbox(frame_versions, selectmode=SINGLE, height=10)
        self.list_versions.pack(side=LEFT, fill=BOTH, expand=True)

        scroll_versions = Scrollbar(frame_versions, orient="vertical", command=self.list_versions.yview)
        scroll_versions.pack(side=RIGHT, fill=Y)

        self.list_versions.config(yscrollcommand=scroll_versions.set)
        self.list_versions.bind("<<ListboxSelect>>", self.on_select_version)

        ttk.Button(parent, text="Restaurer la version sélectionnée", command=self.on_restore_full).pack(pady=5)
        ttk.Button(parent, text="Supprimer la version sélectionnée", command=self.on_delete_version).pack(pady=5)

    # -------------------------------------------------------------------------
    #  ONGLET REQUÊTES TYPE
    # -------------------------------------------------------------------------
    def _build_queries_tab(self, parent: Frame):
        # On insère directement QueriesUI dans cet onglet
        self.queries_ui = QueriesUI(
            parent,
            manager=self.queries_manager,
            logic=self.queries_logic,
        )
        self.queries_ui.pack(fill="both", expand=True, padx=5, pady=5)

    # -------------------------------------------------------------------------
    #  COLONNE DROITE : FICHIERS + PRÉVISUALISATION + ACTIONS
    # -------------------------------------------------------------------------
    def _build_right_column(self, parent: Frame):
        Label(parent, text="Fichiers de la version sélectionnée", font=("Segoe UI", 11, "bold")).pack(pady=5)

        frame_files = Frame(parent)
        frame_files.pack(fill="both", expand=False, padx=10, pady=5)

        self.list_files = Listbox(frame_files, selectmode=MULTIPLE, height=12)
        self.list_files.pack(side=LEFT, fill=BOTH, expand=True)

        scroll_files = Scrollbar(frame_files, orient="vertical", command=self.list_files.yview)
        scroll_files.pack(side=RIGHT, fill=Y)

        self.list_files.config(yscrollcommand=scroll_files.set)
        self.list_files.bind("<<ListboxSelect>>", self.on_file_selected)

        Label(parent, text="Prévisualisation du fichier", font=("Segoe UI", 11, "bold")).pack(pady=5)

        frame_preview = Frame(parent)
        frame_preview.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview_text = Text(frame_preview, wrap="word", height=20)
        self.preview_text.pack(side=LEFT, fill=BOTH, expand=True)

        scroll_preview = Scrollbar(frame_preview, orient="vertical", command=self.preview_text.yview)
        scroll_preview.pack(side=RIGHT, fill=Y)

        self.preview_text.config(yscrollcommand=scroll_preview.set)

        ttk.Button(parent, text="Créer selected_context.md & .html", command=self.on_export_selected).pack(pady=5)
        ttk.Button(parent, text="Restaurer les fichiers sélectionnés", command=self.on_restore_selected).pack(pady=5)


    # -------------------------------------------------------------------------
    #  ACTIONS ONGLET PROJET
    # -------------------------------------------------------------------------
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
        if self.list_versions is None:
            return
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
        if self.list_files is not None:
            self.list_files.delete(0, END)
        if self.preview_text is not None:
            self.preview_text.delete(1.0, END)

    # -------------------------------------------------------------------------
    #  ACTIONS COLONNE DROITE
    # -------------------------------------------------------------------------
    def refresh_files(self):
        if self.list_files is None:
            return
        self.list_files.delete(0, END)
        files = self.client.get_files_from_selected_version()
        for f in files:
            self.list_files.insert(END, f)
        if self.preview_text is not None:
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

    # -------------------------------------------------------------------------
    #  HELPERS
    # -------------------------------------------------------------------------
    def get_selected_files(self):
        """
        Utilisé par QueriesLogic pour récupérer les fichiers sélectionnés
        dans la colonne droite.
        """
        if self.list_files is None:
            return []
        selected_indices = self.list_files.curselection()
        return [self.list_files.get(i) for i in selected_indices]

    def select_version_in_list(self, version: str):
        if self.list_versions is None:
            return
        for i in range(self.list_versions.size()):
            if self.list_versions.get(i) == version:
                self.list_versions.selection_clear(0, END)
                self.list_versions.selection_set(i)
                self.list_versions.activate(i)
                self.on_select_version()
                break
