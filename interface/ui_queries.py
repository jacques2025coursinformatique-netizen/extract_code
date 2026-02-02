from tkinter import (
    Frame, Label, Listbox, Scrollbar, SINGLE, END, BOTH, LEFT, RIGHT, Y,
    Text, StringVar
)
from tkinter import ttk, filedialog, messagebox

from data.queries_manager import QueriesManager


"""
QueriesUI is the Tkinter UI component for managing prompt queries and their versions.
Handles all widget layout, user input, and delegates logic to QueriesManager/QueriesLogic.
No business logic is implemented here; all actions are delegated to the appropriate logic classes.
"""

class QueriesUI(Frame):
    """
    UI component for managing prompt queries and their versions.
    Handles all widget layout, user input, and delegates logic to QueriesManager/QueriesLogic.
    """
    def __init__(self, parent, manager: QueriesManager, logic):
        """
        Initialize the QueriesUI component and build all widgets.
        Args:
            parent: The parent Tkinter widget.
            manager: The QueriesManager instance for data access.
            logic: The QueriesLogic instance for backend actions.
        """
        super().__init__(parent)
        self.manager = manager
        self.logic = logic

        # Sélections courantes
        self.current_query = None
        self.current_version = None

        # Flag pour éviter les callbacks parasites sur les versions
        self._lock_versions = False

        # Variables UI
        self.var_query_name = StringVar()
        self.var_category = StringVar()
        self.var_version = StringVar()
        self.var_context_files = StringVar()

        self._build_ui()

        # Tous les widgets existent maintenant → on peut rafraîchir
        self._refresh_categories()
        self._refresh_queries()
        self._refresh_versions()
        self._refresh_editor()

    # ------------------------------------------------------------------ #
    # CONSTRUCTION UI
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        """
        Build and layout all widgets for the queries management UI.
        """
        main = ttk.PanedWindow(self, orient="horizontal")
        main.pack(fill=BOTH, expand=True)

        left = Frame(main)
        right = Frame(main)
        main.add(left, weight=1)
        main.add(right, weight=2)

        # ============================
        #  FORMULAIRE COMPLET À DROITE
        # ============================
        Label(right, text="Nom de la requête", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.entry_query_name = ttk.Entry(right, textvariable=self.var_query_name)
        self.entry_query_name.pack(fill="x", padx=5, pady=2)

        Label(right, text="Catégorie", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.combo_category = ttk.Combobox(right, textvariable=self.var_category, state="normal")
        self.combo_category.pack(fill="x", padx=5, pady=2)

        Label(right, text="Description", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        frame_desc = Frame(right)
        frame_desc.pack(fill=BOTH, expand=False, padx=5, pady=2)
        self.text_description = Text(frame_desc, height=4, wrap="word")
        self.text_description.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_desc = Scrollbar(frame_desc, command=self.text_description.yview)
        scroll_desc.pack(side=RIGHT, fill=Y)
        self.text_description.config(yscrollcommand=scroll_desc.set)

        Label(right, text="Context files (@file1 @file2 ...)", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.entry_context_files = ttk.Entry(right, textvariable=self.var_context_files)
        self.entry_context_files.pack(fill="x", padx=5, pady=2)

        Label(right, text="Numéro de version", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        self.entry_version = ttk.Entry(right, textvariable=self.var_version)
        self.entry_version.pack(fill="x", padx=5, pady=2)

        Label(right, text="Before", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        frame_before = Frame(right)
        frame_before.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.text_before = Text(frame_before, height=8, wrap="word")
        self.text_before.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_before = Scrollbar(frame_before, command=self.text_before.yview)
        scroll_before.pack(side=RIGHT, fill=Y)
        self.text_before.config(yscrollcommand=scroll_before.set)

        Label(right, text="After", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=2)
        frame_after = Frame(right)
        frame_after.pack(fill=BOTH, expand=True, padx=5, pady=2)
        self.text_after = Text(frame_after, height=8, wrap="word")
        self.text_after.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_after = Scrollbar(frame_after, command=self.text_after.yview)
        scroll_after.pack(side=RIGHT, fill=Y)
        self.text_after.config(yscrollcommand=scroll_after.set)

        btn_save = Frame(right)
        btn_save.pack(fill="x", pady=4)
        ttk.Button(btn_save, text="Enregistrer requête + version", command=self._on_save_all).pack(side=LEFT, padx=2)

        btn_gen = Frame(right)
        btn_gen.pack(fill="x", pady=4)
        ttk.Button(btn_gen, text="Mémoriser la sélection de la requête", command=self._on_memorize_query).pack(side=LEFT, padx=2)
        ttk.Button(btn_gen, text="Copier requête GitHub", command=self._on_generate_github).pack(side=LEFT, padx=2)
        ttk.Button(btn_gen, text="Copier requête Edge", command=self._on_generate_edge).pack(side=LEFT, padx=2)

        # ============================
        #  SECTION CATÉGORIES
        # ============================
        frame_cat = Frame(left)
        frame_cat.pack(fill=BOTH, expand=False, padx=5, pady=5)

        Label(frame_cat, text="Catégories", font=("Segoe UI", 10, "bold")).pack()

        self.list_categories = Listbox(frame_cat, selectmode=SINGLE, height=5)
        self.list_categories.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_cat = Scrollbar(frame_cat, command=self.list_categories.yview)
        scroll_cat.pack(side=RIGHT, fill=Y)
        self.list_categories.config(yscrollcommand=scroll_cat.set)
        self.list_categories.bind("<<ListboxSelect>>", self._on_category_selected)

        btn_cat = Frame(left)
        btn_cat.pack(fill="x", padx=5)
        ttk.Button(btn_cat, text="Ajouter", command=self._on_add_category).pack(side=LEFT, padx=2)
        ttk.Button(btn_cat, text="Modifier", command=self._on_rename_category).pack(side=LEFT, padx=2)
        ttk.Button(btn_cat, text="Supprimer", command=self._on_delete_category).pack(side=LEFT, padx=2)
        ttk.Button(btn_cat, text="Import", command=self._on_import_categories).pack(side=LEFT, padx=2)
        ttk.Button(btn_cat, text="Export", command=self._on_export_categories).pack(side=LEFT, padx=2)

        # ============================
        #  SECTION REQUÊTES
        # ============================
        Label(left, text="Requêtes", font=("Segoe UI", 10, "bold")).pack(pady=4)

        frame_req = Frame(left)
        frame_req.pack(fill=BOTH, expand=True, padx=5)

        self.list_queries = Listbox(frame_req, selectmode=SINGLE, height=10)
        self.list_queries.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_req = Scrollbar(frame_req, command=self.list_queries.yview)
        scroll_req.pack(side=RIGHT, fill=Y)
        self.list_queries.config(yscrollcommand=scroll_req.set)
        self.list_queries.bind("<<ListboxSelect>>", self._on_query_selected)

        btn_req = Frame(left)
        btn_req.pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_req, text="Ajouter", command=self._on_add_query).pack(side=LEFT, padx=2)
        ttk.Button(btn_req, text="Modifier", command=self._on_rename_query).pack(side=LEFT, padx=2)
        ttk.Button(btn_req, text="Supprimer", command=self._on_delete_query).pack(side=LEFT, padx=2)
        ttk.Button(btn_req, text="Import", command=self._on_import_queries).pack(side=LEFT, padx=2)
        ttk.Button(btn_req, text="Export", command=self._on_export_queries).pack(side=LEFT, padx=2)

        # ============================
        #  SECTION VERSIONS
        # ============================
        Label(left, text="Versions", font=("Segoe UI", 10, "bold")).pack(pady=4)

        frame_ver = Frame(left)
        frame_ver.pack(fill=BOTH, expand=True, padx=5)

        self.list_versions = Listbox(frame_ver, selectmode=SINGLE, height=8)
        self.list_versions.pack(side=LEFT, fill=BOTH, expand=True)
        scroll_ver = Scrollbar(frame_ver, command=self.list_versions.yview)
        scroll_ver.pack(side=RIGHT, fill=Y)
        self.list_versions.config(yscrollcommand=scroll_ver.set)
        self.list_versions.bind("<<ListboxSelect>>", self._on_version_selected)

        btn_ver = Frame(left)
        btn_ver.pack(fill="x", padx=5, pady=2)
        ttk.Button(btn_ver, text="Ajouter", command=self._on_add_version).pack(side=LEFT, padx=2)
        ttk.Button(btn_ver, text="Modifier", command=self._on_rename_version).pack(side=LEFT, padx=2)
        ttk.Button(btn_ver, text="Supprimer", command=self._on_delete_version).pack(side=LEFT, padx=2)

    # ------------------------------------------------------------------ #
    # Rafraîchissements
    # ------------------------------------------------------------------ #

    def _refresh_categories(self):
        """
        Refresh the categories list and combobox from the manager.
        """
        self.list_categories.unbind("<<ListboxSelect>>")

        cats = self.manager.get_categories()
        selected = self.list_categories.curselection()

        self.list_categories.delete(0, END)
        for c in cats:
            self.list_categories.insert(END, c)

        self.combo_category["values"] = cats

        if selected:
            try:
                self.list_categories.selection_set(selected[0])
            except Exception:
                pass

        self.list_categories.bind("<<ListboxSelect>>", self._on_category_selected)
        self.list_queries.bind("<<ListboxSelect>>", self._on_query_selected)

    def _refresh_queries(self):
        """
        Refresh the queries list from the manager.
        """
        selected = self.current_query

        self.list_queries.delete(0, END)
        for name in self.manager.get_all_query_names():
            self.list_queries.insert(END, name)

        self._select_in_list(self.list_queries, selected)

    def _refresh_versions(self):
        """
        Refresh the versions list for the current query.
        """
        self._lock_versions = True

        selected = self.current_version

        self.list_versions.delete(0, END)
        if self.current_query:
            for v in self.manager.get_versions_for_query(self.current_query):
                self.list_versions.insert(END, v)

        self._select_in_list(self.list_versions, selected)

        self._lock_versions = False

    def _refresh_editor(self):
        """
        Refresh the editor fields for the selected query and version.
        """
        self._lock_versions = True

        # --- Requête sélectionnée ---
        if self.current_query:
            q = self.manager.get_query(self.current_query)
        else:
            q = None

        if q:
            self.var_query_name.set(q.get("name", ""))
            self.var_category.set(q.get("category", ""))
            self.var_context_files.set(q.get("context_files", ""))

            self.text_description.delete("1.0", END)
            self.text_description.insert("1.0", q.get("description", ""))
        else:
            self.var_query_name.set("")
            self.var_category.set("")
            self.var_context_files.set("")
            self.text_description.delete("1.0", END)

        # --- Version sélectionnée ---
        if q and self.current_version:
            v = self.manager.get_version(self.current_query, self.current_version)
        else:
            v = None

        if v:
            self.var_version.set(v.get("version", ""))
            self.text_before.delete("1.0", END)
            self.text_before.insert("1.0", v.get("before", ""))

            self.text_after.delete("1.0", END)
            self.text_after.insert("1.0", v.get("after", ""))
        else:
            self.var_version.set("")
            self.text_before.delete("1.0", END)
            self.text_after.delete("1.0", END)

        # Sélection visuelle
        self._select_in_list(self.list_queries, self.current_query)
        self._select_in_list(self.list_versions, self.current_version)

        self._lock_versions = False

    def _select_in_list(self, listbox, value):
        """
        Select the given value in the provided listbox, if present.
        """
        listbox.selection_clear(0, END)
        if not value:
            return
        for i in range(listbox.size()):
            if listbox.get(i) == value:
                listbox.selection_set(i)
                listbox.activate(i)
                break

    # ------------------------------------------------------------------ #
    # Sélections
    # ------------------------------------------------------------------ #

    def _on_query_selected(self, event=None):
        """
        Handler for selecting a query in the list. Updates version and editor.
        """
        if event and event.widget is not self.list_queries:
            return

        sel = self.list_queries.curselection()
        if not sel:
            return

        self.current_query = self.list_queries.get(sel[0])

        versions = self.manager.get_versions_for_query(self.current_query)
        self.current_version = versions[0] if versions else None

        self._refresh_versions()
        self._refresh_editor()

    def _on_version_selected(self, event=None):
        """
        Handler for selecting a version in the list. Updates editor fields.
        """
        if self._lock_versions:
            return
        if event and event.widget is not self.list_versions:
            return

        sel = self.list_versions.curselection()
        if not sel:
            self.current_version = None
        else:
            self.current_version = self.list_versions.get(sel[0])

        # Ici, on ne touche qu’aux champs de version, pas aux listes
        self._lock_versions = True

        if self.current_query and self.current_version:
            v = self.manager.get_version(self.current_query, self.current_version)
        else:
            v = None

        if v:
            self.var_version.set(v.get("version", ""))
            self.text_before.delete("1.0", END)
            self.text_before.insert("1.0", v.get("before", ""))
            self.text_after.delete("1.0", END)
            self.text_after.insert("1.0", v.get("after", ""))
        else:
            self.var_version.set("")
            self.text_before.delete("1.0", END)
            self.text_after.delete("1.0", END)

        self._lock_versions = False

    # ------------------------------------------------------------------ #
    # Actions Catégories
    # ------------------------------------------------------------------ #

    def _on_add_category(self):
        """
        Handler to add a new category via dialog.
        """
        name = self._ask_string("Nouvelle catégorie", "Nom :")
        if not name:
            return
        self.manager.add_category(name)
        self._refresh_categories()

    def _on_rename_category(self):
        """
        Handler to rename the selected category via dialog.
        """
        sel = self.list_categories.curselection()
        if not sel:
            return
        old = self.list_categories.get(sel[0])
        new = self._ask_string("Renommer catégorie", "Nouveau nom :", initial=old)
        if not new:
            return
        self.manager.rename_category(old, new)
        self._refresh_categories()

    def _on_delete_category(self):
        """
        Handler to delete the selected category after confirmation.
        """
        sel = self.list_categories.curselection()
        if not sel:
            return
        name = self.list_categories.get(sel[0])
        if not messagebox.askyesno("Supprimer", f"Supprimer la catégorie '{name}' ?"):
            return
        self.manager.delete_category(name)
        self._refresh_categories()

    def _on_import_categories(self):
        """
        Handler to import categories from a JSON file.
        """
        path = filedialog.askopenfilename(title="Importer catégories", filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.manager.import_categories(path)
        self._refresh_categories()

    def _on_export_categories(self):
        """
        Handler to export categories to a JSON file.
        """
        path = filedialog.asksaveasfilename(title="Exporter catégories", defaultextension=".json")
        if not path:
            return
        self.manager.export_categories(path)

    def _on_category_selected(self, event=None):
        """
        Handler for selecting a category in the list. Updates the category field.
        """
        if not self.current_query:
            return
        selection = self.list_categories.curselection()
        if not selection:
            return
        category = self.list_categories.get(selection[0])
        self.var_category.set(category)

    # ------------------------------------------------------------------ #
    # Actions Requêtes
    # ------------------------------------------------------------------ #

    def _on_add_query(self):
        """
        Handler to add a new query via dialog.
        """
        name = self._ask_string("Nouvelle requête", "Nom :")
        if not name:
            return
        self.manager.add_query(name)
        self.current_query = name
        self.current_version = None
        self._refresh_queries()
        self._refresh_versions()
        self._refresh_editor()

    def _on_rename_query(self):
        """
        Handler to rename the selected query via dialog.
        """
        if not self.current_query:
            return
        new = self._ask_string("Renommer requête", "Nouveau nom :", initial=self.current_query)
        if not new:
            return
        self.manager.update_query_fields(
            old_name=self.current_query,
            new_name=new,
            category=self.var_category.get(),
            description=self.text_description.get("1.0", END).strip(),
            context_files=self.var_context_files.get(),
        )
        self.current_query = new
        self._refresh_queries()
        self._refresh_editor()

    def _on_delete_query(self):
        """
        Handler to delete the selected query after confirmation.
        """
        if not self.current_query:
            return
        if not messagebox.askyesno("Supprimer", f"Supprimer la requête '{self.current_query}' ?"):
            return
        self.manager.delete_query(self.current_query)
        self.current_query = None
        self.current_version = None
        self._refresh_queries()
        self._refresh_versions()
        self._refresh_editor()

    def _on_import_queries(self):
        """
        Handler to import queries from a JSON file.
        """
        path = filedialog.askopenfilename(title="Importer requêtes", filetypes=[("JSON", "*.json")])
        if not path:
            return
        self.manager.import_queries(path)
        self._refresh_queries()
        self._refresh_versions()
        self._refresh_editor()

    def _on_export_queries(self):
        """
        Handler to export queries to a JSON file.
        """
        path = filedialog.asksaveasfilename(title="Exporter requêtes", defaultextension=".json")
        if not path:
            return
        self.manager.export_queries(path)

    def _on_memorize_query(self):
        """
        Handler to memorize the current query and version for Copilot actions.
        """
        # Récupérer la requête + version sélectionnées
        query, version = self.get_current_query_and_version()

        if not (query and version):
            messagebox.showerror("Erreur", "Sélectionnez d'abord une requête et une version.")
            return

        # Mémoriser dans ApplicationUI
        self.logic.ui.memo_query = query
        self.logic.ui.memo_version = version

        # Message clair pour guider l'utilisateur
        messagebox.showinfo(
            "Sélection mémorisée",
            "La requête et la version ont été mémorisées.\n\n"
            "➡️ Sélectionnez maintenant les fichiers de la version dans la colonne de droite.\n"
            "➡️ Puis cliquez sur l’un des boutons :\n"
            "   - Copier requête GitHub\n"
            "   - Copier requête Edge"
        )


    # ------------------------------------------------------------------ #
    # Actions Versions
    # ------------------------------------------------------------------ #

    def _on_add_version(self):
        """
        Handler to add a new version to the current query.
        """
        if not self.current_query:
            messagebox.showerror("Erreur", "Sélectionnez une requête.")
            return

        existing = self.manager.get_versions_for_query(self.current_query)

        suggested = "001"
        if existing:
            nums = []
            for v in existing:
                try:
                    nums.append(int(v))
                except ValueError:
                    pass
            if nums:
                suggested = f"{max(nums) + 1:03d}"

        version = self._ask_string("Nouvelle version", "Numéro :", initial=suggested)
        if not version:
            return

        self.manager.add_version(self.current_query, version)
        self.current_version = version
        self.var_version.set(version)

        self._refresh_versions()
        self._refresh_editor()

    def _on_rename_version(self):
        """
        Handler to rename the selected version via dialog.
        """
        if not (self.current_query and self.current_version):
            return
        new = self._ask_string("Renommer version", "Nouveau numéro :", initial=self.current_version)
        if not new:
            return
        before = self.text_before.get("1.0", END).strip()
        after = self.text_after.get("1.0", END).strip()
        self.manager.update_version(
            query_name=self.current_query,
            old_version=self.current_version,
            new_version=new,
            before=before,
            after=after,
        )
        self.current_version = new
        self._refresh_versions()
        self._refresh_editor()

    def _on_delete_version(self):
        """
        Handler to delete the selected version after confirmation.
        """
        if not (self.current_query and self.current_version):
            return
        if not messagebox.askyesno("Supprimer", f"Supprimer la version '{self.current_version}' ?"):
            return
        self.manager.delete_version(self.current_query, self.current_version)
        self.current_version = None
        self._refresh_versions()
        self._refresh_editor()

    # ------------------------------------------------------------------ #
    # ENREGISTREMENT GLOBAL
    # ------------------------------------------------------------------ #

    def _on_save_all(self):
        """
        Handler to save all changes to the current query and version.
        """
        if not self.current_query:
            messagebox.showerror("Erreur", "Sélectionnez ou créez une requête.")
            return

        old_name = self.current_query
        new_name = self.var_query_name.get().strip()
        category = self.var_category.get().strip()
        description = self.text_description.get("1.0", END).strip()
        context_files = self.var_context_files.get().strip()

        self.manager.update_query_fields(
            old_name=old_name,
            new_name=new_name or old_name,
            category=category,
            description=description,
            context_files=context_files,
        )
        self.current_query = new_name or old_name

        version_number = self.var_version.get().strip()
        before = self.text_before.get("1.0", END).strip()
        after = self.text_after.get("1.0", END).strip()

        if version_number:
            self.manager.update_version(
                query_name=self.current_query,
                old_version=self.current_version or version_number,
                new_version=version_number,
                before=before,
                after=after,
            )
            self.current_version = version_number
            self.var_version.set(version_number)

        self._refresh_queries()
        self._refresh_versions()
        self._refresh_editor()

    # ------------------------------------------------------------------ #
    # GÉNÉRATION
    # ------------------------------------------------------------------ #

    def get_current_query_and_version(self):
        """
        Return the currently selected query and version.
        """
        return self.current_query, self.current_version


    def _on_generate_github(self):
        """
        Handler to generate and copy the GitHub Copilot prompt for the memorized query/version.
        """
        # Utiliser la sélection mémorisée dans ApplicationUI
        memo_query = self.logic.ui.memo_query
        memo_version = self.logic.ui.memo_version

        if not (memo_query and memo_version):
            messagebox.showerror("Erreur", "Cliquez d'abord sur 'Mémoriser la sélection de la requête' avant de copier.")
            return

        saved_query = memo_query
        saved_version = memo_version


        # Appeler la génération (sans context_files)
        self.logic.generate_github_copilot()

        # Restaurer la sélection
        self.current_query = saved_query
        self.current_version = saved_version

        # Rafraîchir l’UI
        self._refresh_queries()
        self._refresh_versions()
        self._refresh_editor()


    def _on_generate_edge(self):
        """
        Handler to generate and copy the Edge Copilot prompt for the memorized query/version.
        """
        # Utiliser la sélection mémorisée dans ApplicationUI
        memo_query = self.logic.ui.memo_query
        memo_version = self.logic.ui.memo_version

        if not (memo_query and memo_version):
            messagebox.showerror("Erreur", "Cliquez d'abord sur 'Mémoriser la sélection de la requête' avant de copier.")
            return

        saved_query = memo_query
        saved_version = memo_version


        self.logic.generate_edge_copilot()

        self.current_query = saved_query
        self.current_version = saved_version

        self._refresh_queries()
        self._refresh_versions()
        self._refresh_editor()




    # ------------------------------------------------------------------ #
    # HELPERS
    # ------------------------------------------------------------------ #

    def _ask_string(self, title: str, prompt: str, initial: str = ""):
        """
        Helper to show a string input dialog and return the result.
        Args:
            title: Dialog title.
            prompt: Prompt message.
            initial: Initial value for the input.
        Returns:
            The string entered by the user, or None if cancelled.
        """
        from tkinter.simpledialog import askstring
        return askstring(title, prompt, initialvalue=initial)
