import os
import subprocess
from typing import List, Optional
from src.server_logic import ServerLogic


class ClientLogic:
    """
    Orchestrates all front-end logic for project selection, versioning, file selection, and export/restore actions.
    Delegates backend operations to ServerLogic. Maintains current project, version, and file selection state.
    """
    def __init__(self,logic):
        """
        Initialize the client logic state.
        """
        
        self.project_root: Optional[str] = None
        self.server: Optional[ServerLogic] = None
        self.selected_version: Optional[str] = None
        self.selected_files: List[str] = []
        self.memo_query = None
        self.memo_version = None
        self.logic = logic

    # ---------- Projet ----------

    def select_project(self, path: str) -> None:
        self.project_root = path
        self.server = ServerLogic(path)

        # IMPORTANT : mettre à jour QueriesLogic avec le vrai chemin du projet
        if self.logic:
            self.logic.base_path = path


    def has_project(self) -> bool:
        """
        Return True if a project is currently selected.
        """
        return self.server is not None

    def open_project_folder(self) -> None:
        """
        Open the current project folder in the system file explorer.
        """
        if not self.project_root:
            return
        if os.name == "nt":  # Windows
            os.startfile(self.project_root)
        elif os.name == "posix":  # macOS / Linux
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", self.project_root])

    # ---------- Extraction ----------

    def extract_full_project(self) -> str:
        """
        Scan, snapshot, and export the full project context. Sets the selected version.
        Returns:
            The version identifier of the new snapshot.
        """
        if not self.server:
            raise RuntimeError("Aucun projet sélectionné.")
        snapshot = self.server.scan_project()
        self.server.save_snapshot(snapshot)
        self.server.export_full_context(snapshot)
        self.selected_version = snapshot.version
        return snapshot.version

    # ---------- Versions ----------

    def get_available_versions(self) -> List[str]:
        """
        Return a list of all available version identifiers for the current project.
        """
        if not self.server:
            return []
        return self.server.list_versions()

    def select_version(self, version: str) -> None:
        """
        Set the currently selected version.
        Args:
            version: Version identifier to select.
        """
        self.selected_version = version

    def delete_selected_version(self) -> None:
        """
        Delete the currently selected version from the project.
        """
        if not self.server or not self.selected_version:
            return
        self.server.delete_version(self.selected_version)
        self.selected_version = None

    # ---------- Fichiers ----------

    def get_files_from_selected_version(self) -> List[str]:
        """
        Return a sorted list of file paths from the currently selected version.
        """
        if not self.server or not self.selected_version:
            return []
        snapshot = self.server.load_snapshot(self.selected_version)
        return sorted(snapshot.files_content.keys())

    def set_selected_files(self, files: List[str]) -> None:
        """
        Set the list of currently selected files for export/restore actions.
        Args:
            files: List of file paths to select.
        """
        self.selected_files = files

    # ---------- Export sélection ----------

    def export_selected_markdown_and_html(self) -> None:
        """
        Export the selected files as Markdown and HTML context files.
        """
        if not self.server or not self.selected_version:
            return
        snapshot = self.server.load_snapshot(self.selected_version)
        self.server.export_selected_context(snapshot, self.selected_files)

    # ---------- Restauration ----------

    def restore_full_version(self) -> None:
        """
        Restore all files from the currently selected version to the project directory.
        """
        if not self.server or not self.selected_version:
            return
        snapshot = self.server.load_snapshot(self.selected_version)
        self.server.restore_all(snapshot)

    def restore_selected_files(self) -> None:
        """
        Restore only the selected files from the current version to the project directory.
        """
        if not self.server or not self.selected_version:
            return
        snapshot = self.server.load_snapshot(self.selected_version)
        self.server.restore_selected(snapshot, self.selected_files)

    def memorize_query_and_version(self, query, version):
        self.memo_query = query
        self.memo_version = version

    def generate_github_copilot(self):
        selected_files = self.logic.get_selected_files()

        return self.logic.generate_github_copilot(
            self.memo_query,
            self.memo_version,
            selected_files
        )

    def generate_edge_copilot(self):

        selected_files = self.logic.get_selected_files()

        return self.logic.generate_edge_copilot(
            self.memo_query,
            self.memo_version,
            selected_files
        )

        