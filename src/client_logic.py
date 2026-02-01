import os
import subprocess
from typing import List, Optional
from src.server_logic import ServerLogic


class ClientLogic:
    def __init__(self):
        self.project_root: Optional[str] = None
        self.server: Optional[ServerLogic] = None
        self.selected_version: Optional[str] = None
        self.selected_files: List[str] = []

    # ---------- Projet ----------

    def select_project(self, path: str) -> None:
        self.project_root = path
        self.server = ServerLogic(path)

    def has_project(self) -> bool:
        return self.server is not None

    def open_project_folder(self) -> None:
        if not self.project_root:
            return
        if os.name == "nt":  # Windows
            os.startfile(self.project_root)
        elif os.name == "posix":  # macOS / Linux
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", self.project_root])

    # ---------- Extraction ----------

    def extract_full_project(self) -> str:
        if not self.server:
            raise RuntimeError("Aucun projet sélectionné.")
        snapshot = self.server.scan_project()
        self.server.save_snapshot(snapshot)
        self.server.export_full_context(snapshot)
        self.selected_version = snapshot.version
        return snapshot.version

    # ---------- Versions ----------

    def get_available_versions(self) -> List[str]:
        if not self.server:
            return []
        return self.server.list_versions()

    def select_version(self, version: str) -> None:
        self.selected_version = version

    def delete_selected_version(self) -> None:
        if not self.server or not self.selected_version:
            return
        self.server.delete_version(self.selected_version)
        self.selected_version = None

    # ---------- Fichiers ----------

    def get_files_from_selected_version(self) -> List[str]:
        if not self.server or not self.selected_version:
            return []
        snapshot = self.server.load_snapshot(self.selected_version)
        return sorted(snapshot.files_content.keys())

    def set_selected_files(self, files: List[str]) -> None:
        self.selected_files = files

    # ---------- Export sélection ----------

    def export_selected_markdown_and_html(self) -> None:
        if not self.server or not self.selected_version:
            return
        snapshot = self.server.load_snapshot(self.selected_version)
        self.server.export_selected_context(snapshot, self.selected_files)

    # ---------- Restauration ----------

    def restore_full_version(self) -> None:
        if not self.server or not self.selected_version:
            return
        snapshot = self.server.load_snapshot(self.selected_version)
        self.server.restore_all(snapshot)

    def restore_selected_files(self) -> None:
        if not self.server or not self.selected_version:
            return
        snapshot = self.server.load_snapshot(self.selected_version)
        self.server.restore_selected(snapshot, self.selected_files)
