import os
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


DEFAULT_EXCLUDES = [
    "venv", "code_source", "archive", ".env", ".venv", ".git", "__pycache__", ".python-version", "dist", "build", "main.spec"
]


@dataclass
class ProjectPaths:
    """
    Utility class for managing all important file and directory paths for a project.
    Provides properties for code source, exclusion file, context files, and versioned JSONs.
    """
    root: str

    @property
    def code_source(self) -> str:
        """Return the path to the code_source directory."""
        return os.path.join(self.root, "code_source")

    @property
    def exclude_file(self) -> str:
        """Return the path to the exclusion rules file."""
        return os.path.join(self.code_source, "exclude.txt")

    def organisation_json(self, version: str) -> str:
        """Return the path to the organisation JSON for a given version."""
        return os.path.join(self.code_source, f"organisation.{version}.json")

    def files_content_json(self, version: str) -> str:
        """Return the path to the files content JSON for a given version."""
        return os.path.join(self.code_source, f"files_content.{version}.json")

    @property
    def context_md(self) -> str:
        """Return the path to the main context Markdown file."""
        return os.path.join(self.code_source, "context.md")

    @property
    def context_html(self) -> str:
        """Return the path to the main context HTML file."""
        return os.path.join(self.code_source, "context.html")

    @property
    def selected_context_md(self) -> str:
        """Return the path to the selected context Markdown file."""
        return os.path.join(self.code_source, "selected_context.md")

    @property
    def selected_context_html(self) -> str:
        """Return the path to the selected context HTML file."""
        return os.path.join(self.code_source, "selected_context.html")


@dataclass
class FileEntry:
    """
    Represents a single file's relative path and its content.
    """
    relative_path: str
    content: str


@dataclass
class ProjectSnapshot:
    """
    Represents a snapshot of the project at a given version.
    Contains the version, folder/file organisation, and file contents.
    """
    version: str
    organisation: Dict[str, Dict[str, List[str]]]
    files_content: Dict[str, str]


@dataclass
class ExclusionRules:
    """
    Manages default and custom exclusion rules for files and folders.
    Used to determine which files/folders should be ignored during project scans.
    """
    defaults: Set[str] = field(default_factory=lambda: set(DEFAULT_EXCLUDES))
    custom: Set[str] = field(default_factory=set)

    def all(self) -> Set[str]:
        """Return the union of default and custom exclusion rules."""
        return self.defaults.union(self.custom)

    def should_exclude(self, name: str) -> bool:
        """
        Determine if a file or folder should be excluded based on the rules.
        Args:
            name: File or folder name to check.
        Returns:
            True if excluded, False otherwise.
        """
        for ex in self.all():
            if name == ex or name.startswith(ex):
                return True
        return False
