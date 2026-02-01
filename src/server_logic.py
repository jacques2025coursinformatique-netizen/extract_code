import os
from typing import List, Dict, Tuple
from data.models import ProjectPaths, ExclusionRules, ProjectSnapshot
from data.utils import (
    save_json,
    load_json,
    generate_markdown,
    generate_html,
    get_next_version_number,
    list_existing_versions,
    delete_version_files,
)


class ServerLogic:
    def __init__(self, project_root: str):
        self.paths = ProjectPaths(project_root)
        self.exclusions = ExclusionRules()
        self._ensure_code_source()

    # ---------- Initialisation / exclusions ----------

    def _ensure_code_source(self) -> None:
        os.makedirs(self.paths.code_source, exist_ok=True)
        if not os.path.exists(self.paths.exclude_file):
            with open(self.paths.exclude_file, "w", encoding="utf-8") as f:
                f.write("\n".join(sorted(self.exclusions.defaults)))

    def load_exclusions(self) -> None:
        self.exclusions.custom.clear()
        if os.path.exists(self.paths.exclude_file):
            with open(self.paths.exclude_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.exclusions.custom.add(line)

    # ---------- Scan / snapshot ----------

    def scan_project(self) -> ProjectSnapshot:
        self.load_exclusions()
        organisation: Dict[str, Dict[str, List[str]]] = {}
        files_content: Dict[str, str] = {}

        for current_root, dirs, files in os.walk(self.paths.root):
            rel_root = os.path.relpath(current_root, self.paths.root)
            if rel_root == ".":
                rel_root = ""

            dirs[:] = [d for d in dirs if not self.exclusions.should_exclude(d)]

            organisation[rel_root] = {
                "dirs": dirs.copy(),
                "files": [f for f in files if not self.exclusions.should_exclude(f)],
            }

            for f in files:
                if self.exclusions.should_exclude(f):
                    continue
                rel_path = os.path.join(rel_root, f) if rel_root else f
                file_path = os.path.join(current_root, f)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                        files_content[rel_path] = fp.read()
                except Exception:
                    files_content[rel_path] = "<< Impossible de lire ce fichier >>"

        version = get_next_version_number(self.paths.code_source)
        return ProjectSnapshot(version=version, organisation=organisation, files_content=files_content)

    # ---------- Sauvegarde / chargement snapshot ----------

    def save_snapshot(self, snapshot: ProjectSnapshot) -> None:
        save_json(self.paths.organisation_json(snapshot.version), snapshot.organisation)
        save_json(self.paths.files_content_json(snapshot.version), snapshot.files_content)

    def load_snapshot(self, version: str) -> ProjectSnapshot:
        org = load_json(self.paths.organisation_json(version))
        fc = load_json(self.paths.files_content_json(version))
        return ProjectSnapshot(version=version, organisation=org, files_content=fc)

    # ---------- Exports ----------

    def export_full_context(self, snapshot: ProjectSnapshot) -> None:
        md = generate_markdown(snapshot)
        html = generate_html(snapshot)
        with open(self.paths.context_md, "w", encoding="utf-8") as f:
            f.write(md)
        with open(self.paths.context_html, "w", encoding="utf-8") as f:
            f.write(html)

    def export_selected_context(self, snapshot: ProjectSnapshot, selected_files: List[str]) -> None:
        from data.utils import filter_snapshot
        filtered = filter_snapshot(snapshot, selected_files)
        md = generate_markdown(filtered)
        html = generate_html(filtered)
        with open(self.paths.selected_context_md, "w", encoding="utf-8") as f:
            f.write(md)
        with open(self.paths.selected_context_html, "w", encoding="utf-8") as f:
            f.write(html)

    # ---------- Versioning ----------

    def list_versions(self) -> List[str]:
        return list_existing_versions(self.paths.code_source)

    def delete_version(self, version: str) -> None:
        delete_version_files(self.paths.code_source, version)

    # ---------- Restauration ----------

    def restore_all(self, snapshot: ProjectSnapshot) -> None:
        for rel_path, content in snapshot.files_content.items():
            abs_path = os.path.join(self.paths.root, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)

    def restore_selected(self, snapshot: ProjectSnapshot, selected_files: List[str]) -> None:
        selected_set = set(selected_files)
        for rel_path, content in snapshot.files_content.items():
            if rel_path not in selected_set:
                continue
            abs_path = os.path.join(self.paths.root, rel_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)