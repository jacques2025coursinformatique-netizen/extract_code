import os
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


DEFAULT_EXCLUDES = ["venv", "code_source", "archive", ".env",".venv",".git","__pycache__",".python-version","dist","build","main.spec"]


@dataclass
class ProjectPaths:
    root: str

    @property
    def code_source(self) -> str:
        return os.path.join(self.root, "code_source")

    @property
    def exclude_file(self) -> str:
        return os.path.join(self.code_source, "exclude.txt")

    def organisation_json(self, version: str) -> str:
        return os.path.join(self.code_source, f"organisation.{version}.json")

    def files_content_json(self, version: str) -> str:
        return os.path.join(self.code_source, f"files_content.{version}.json")

    @property
    def context_md(self) -> str:
        return os.path.join(self.code_source, "context.md")

    @property
    def context_html(self) -> str:
        return os.path.join(self.code_source, "context.html")

    @property
    def selected_context_md(self) -> str:
        return os.path.join(self.code_source, "selected_context.md")

    @property
    def selected_context_html(self) -> str:
        return os.path.join(self.code_source, "selected_context.html")


@dataclass
class FileEntry:
    relative_path: str
    content: str


@dataclass
class ProjectSnapshot:
    version: str
    organisation: Dict[str, Dict[str, List[str]]]
    files_content: Dict[str, str]


@dataclass
class ExclusionRules:
    defaults: Set[str] = field(default_factory=lambda: set(DEFAULT_EXCLUDES))
    custom: Set[str] = field(default_factory=set)

    def all(self) -> Set[str]:
        return self.defaults.union(self.custom)

    def should_exclude(self, name: str) -> bool:
        for ex in self.all():
            if name == ex or name.startswith(ex):
                return True
        return False
