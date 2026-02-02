import os
import webbrowser
from typing import List, Dict, Callable, Optional
import subprocess


from data.queries_manager import QueriesManager


"""
QueriesLogic contains all backend logic for prompt building, context file actions, and Copilot query generation.
This class is responsible for constructing prompts for Copilot (GitHub/Edge), handling context file opening, and clipboard actions.
It does not access UI state directly and is orchestrated by ClientLogic. All UI dependencies are injected via callbacks.
"""

class QueriesLogic:
    """
    Backend logic for prompt/query management and Copilot integration.
    Handles prompt construction, clipboard, and context file opening.
    """
    def __init__(
        self,
        manager: QueriesManager,
        copy_to_clipboard: Callable[[str], None],
        get_selected_files: Callable[[], List[str]],
        base_path: Optional[str] = None,
    ):
        """
        Initialize the QueriesLogic backend.
        Args:
            manager: Instance of QueriesManager for data access.
            copy_to_clipboard: Function to copy text to clipboard (injected from UI layer).
            get_selected_files: Callback to get selected files from UI (injected from UI layer).
            base_path: Optional base path for locating context files. Defaults to project root.
        """
        self.manager = manager
        self.copy_to_clipboard = copy_to_clipboard
        self.get_selected_files = get_selected_files

        # Determine base path for context files (default: project root)
        if base_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.base_path = base_path

        # Paths to generated context files (HTML and Markdown)
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


    # ---------- Prompt Construction Methods ----------

    def build_edge_query(self, query: Dict, version: Dict) -> str:
        """
        Build the prompt for Edge Copilot using the selected query and version.
        The context block is always a fixed message referencing the @selected_context tab.
        Args:
            query: The query dictionary (from QueriesManager).
            version: The version dictionary (from QueriesManager).
        Returns:
            The full prompt string for Edge Copilot.
        """
        before = version.get("before", "").strip()
        after = version.get("after", "").strip()

        # Always include a context block for Edge Copilot
        context_block = (
            "Interface: the context files are available in the @selected_context tab."
        )

        parts = [p for p in [before, context_block, after] if p]
        return "\n\n".join(parts)

    def build_github_query(self, query: Dict, version: Dict) -> str:
        """
        Build the prompt for GitHub Copilot using the selected query, version, and selected files.
        The context block lists all selected files, or a message if none are selected.
        Args:
            query: The query dictionary (from QueriesManager).
            version: The version dictionary (from QueriesManager).
        Returns:
            The full prompt string for GitHub Copilot.
        """
        before = version.get("before", "").strip()
        after = version.get("after", "").strip()

        selected_files = self.get_selected_files()
        # Build a context block listing all selected files, or a placeholder if none
        if selected_files:
            context_lines = [f"@{path}" for path in selected_files]
            context_block = "Context files:\n" + "\n".join(context_lines)
        else:
            context_block = "Context files: (no files selected)"

        parts = [p for p in [before, context_block, after] if p]
        return "\n\n".join(parts)

    # ---------- Context File and Copilot Actions ----------



    def open_edge_context_html(self) -> None:
        """
        Open the generated HTML and Markdown context files in the default browser and Edge (if available).
        Used for Edge Copilot context visualization. Opens HTML in default browser, and tries to open MD in Edge.
        """
        # Open HTML in default browser
        if os.path.exists(self.context_html_path):
            webbrowser.open(self.context_html_path)

        # Try to open Markdown in Edge (Windows only)
        if os.path.exists(self.context_md_path):
            try:
                subprocess.Popen([
                    "cmd", "/c", "start", "msedge.exe", self.context_md_path
                ], shell=True)
            except Exception as e:
                print("Erreur ouverture MD dans Edge:", e)


    def generate_edge_copilot(self) -> str:
        """
        Generate the Edge Copilot prompt for the currently memorized query and version.
        Copies the result to clipboard and opens the context HTML/MD files for user reference.
        Returns:
            The generated prompt string.
        """
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
        """
        Generate the GitHub Copilot prompt for the currently memorized query and version.
        Copies the result to clipboard for user to paste into Copilot.
        Returns:
            The generated prompt string.
        """
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
