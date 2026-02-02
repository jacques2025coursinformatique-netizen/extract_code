import os
import webbrowser
from typing import List, Dict, Callable, Optional
import subprocess


from data.queries_manager import QueriesManager


class QueriesLogic:
    def __init__(
        self,
        manager: QueriesManager,
        copy_to_clipboard: Callable[[str], None],
        get_selected_files: Callable[[], List[str]],
        base_path: Optional[str] = None,
    ):
        self.manager = manager
        self.copy_to_clipboard = copy_to_clipboard
        self.get_selected_files = get_selected_files

        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = base_path

        self.context_html_path = os.path.join(
            self.base_path,
            "code_source",
            "selected_context.html",
        )

        self.context_md_path = os.path.join(
            self.base_path,
            "code_source",
            "selected_context.md",
        )


    # ---------- Construction des requêtes ----------

    def build_edge_query(self, query: Dict, version: Dict) -> str:
        before = version.get("before", "").strip()
        after = version.get("after", "").strip()

        context_block = (
            "Interface: the context files are available in the @selected_context tab."
        )

        parts = [p for p in [before, context_block, after] if p]
        return "\n\n".join(parts)

    def build_github_query(self, query: Dict, version: Dict) -> str:
        before = version.get("before", "").strip()
        after = version.get("after", "").strip()

        selected_files = self.get_selected_files()
        if selected_files:
            context_lines = [f"@{path}" for path in selected_files]
            context_block = "Context files:\n" + "\n".join(context_lines)
        else:
            context_block = "Context files: (no files selected)"

        parts = [p for p in [before, context_block, after] if p]
        return "\n\n".join(parts)

    # ---------- Actions ----------



    def open_edge_context_html(self) -> None:
        # Ouvrir le HTML normalement
        if os.path.exists(self.context_html_path):
            webbrowser.open(self.context_html_path)

        # Ouvrir le MD dans Edge (forcer Edge)
        if os.path.exists(self.context_md_path):
            try:
                subprocess.Popen([
                    "cmd", "/c", "start", "msedge.exe", self.context_md_path
                ], shell=True)
            except Exception as e:
                print("Erreur ouverture MD dans Edge:", e)


    def generate_edge_copilot(self) -> str:
        query_name = self.ui.memo_query
        query = self.manager.get_query(query_name)
        if query is None:
            return ""
        
        version_number = self.ui.memo_version
        version = self.manager.get_version(query_name, version_number)
        if version is None:
            return ""
        text = self.build_edge_query(query, version)
        self.open_edge_context_html()
        self.copy_to_clipboard(text)
        return text

    def generate_github_copilot(self) -> str:
        query_name = self.ui.memo_query
        query = self.manager.get_query(query_name)
        if query is None:
            return ""
        
        version_number = self.ui.memo_version
        version = self.manager.get_version(query_name, version_number)
        if version is None:
            return ""
        text = self.build_github_query(query, version)
        self.copy_to_clipboard(text)
        return text
