import json
import os
from typing import Dict, List, Optional, Any


class QueriesManager:
    """
    Gestion des fichiers :
    - data/categories.json : liste de valeurs possibles pour le champ "category"
    - data/queries.json : liste de requêtes complètes
    """

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))  # .../data
        else:
            if os.path.basename(base_dir) == "data":
                data_dir = base_dir
            else:
                data_dir = os.path.join(base_dir, "data")

        self.categories_path = os.path.join(data_dir, "categories.json")
        self.queries_path = os.path.join(data_dir, "queries.json")

        self.categories: List[str] = []
        self.queries: List[Dict[str, Any]] = []

        self.load_all()

    # ------------------------------------------------------------------ #
    # Chargement / sauvegarde
    # ------------------------------------------------------------------ #

    def load_all(self) -> None:
        self.categories = self._load_categories(self.categories_path)
        self.queries = self._load_queries(self.queries_path)

    def save_all(self) -> None:
        self._save_categories(self.categories_path, self.categories)
        self._save_queries(self.queries_path, self.queries)

    def _load_categories(self, path: str) -> List[str]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "categories" in data:
            return list(data["categories"])
        if isinstance(data, list):
            return data
        return []

    def _save_categories(self, path: str, categories: List[str]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"categories": categories}, f, indent=4, ensure_ascii=False)

    def _load_queries(self, path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "queries" in data:
            return list(data["queries"])
        if isinstance(data, list):
            return data
        return []

    def _save_queries(self, path: str, queries: List[Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"queries": queries}, f, indent=4, ensure_ascii=False)

    # ------------------------------------------------------------------ #
    # Catégories (liste de valeurs possibles)
    # ------------------------------------------------------------------ #

    def get_categories(self) -> List[str]:
        return list(self.categories)

    def add_category(self, name: str) -> None:
        if name and name not in self.categories:
            self.categories.append(name)
            self.save_all()

    def delete_category(self, name: str) -> None:
        if name in self.categories:
            self.categories.remove(name)
            self.save_all()

    def rename_category(self, old: str, new: str) -> None:
        if old in self.categories and new:
            idx = self.categories.index(old)
            self.categories[idx] = new
            self.save_all()

    # ------------------------------------------------------------------ #
    # Requêtes
    # ------------------------------------------------------------------ #

    def get_all_query_names(self) -> List[str]:
        return [q.get("name", "") for q in self.queries]

    def get_query(self, name: str) -> Optional[Dict[str, Any]]:
        for q in self.queries:
            if q.get("name") == name:
                return q
        return None

    def add_query(self, name: str) -> None:
        if not name:
            return
        if self.get_query(name) is not None:
            return
        self.queries.append(
            {
                "name": name,
                "description": "",
                "category": "",
                "context_files": "",
                "versions": [],
            }
        )
        self.save_all()

    def delete_query(self, name: str) -> None:
        before = len(self.queries)
        self.queries = [q for q in self.queries if q.get("name") != name]
        if len(self.queries) != before:
            self.save_all()

    def update_query_fields(
        self,
        old_name: str,
        new_name: str,
        category: str,
        description: str,
        context_files: str,
    ) -> None:
        q = self.get_query(old_name)
        if not q:
            return
        q["name"] = new_name or old_name
        q["category"] = category or ""
        q["description"] = description or ""
        q["context_files"] = context_files or ""
        self.save_all()

    # ------------------------------------------------------------------ #
    # Versions
    # ------------------------------------------------------------------ #

    def get_versions_for_query(self, query_name: str) -> List[str]:
        q = self.get_query(query_name)
        if not q:
            return []
        return [v.get("version", "") for v in q.get("versions", [])]

    def get_version(self, query_name: str, version_number: str) -> Optional[Dict[str, Any]]:
        q = self.get_query(query_name)
        if not q:
            return None
        for v in q.get("versions", []):
            if v.get("version") == version_number:
                return v
        return None

    def add_version(self, query_name: str, version_number: str) -> None:
        q = self.get_query(query_name)
        if not q or not version_number:
            return
        versions = q.setdefault("versions", [])
        for v in versions:
            if v.get("version") == version_number:
                return
        versions.append(
            {
                "version": version_number,
                "before": "",
                "after": "",
            }
        )
        self.save_all()

    def delete_version(self, query_name: str, version_number: str) -> None:
        q = self.get_query(query_name)
        if not q:
            return
        versions = q.get("versions", [])
        new_versions = [v for v in versions if v.get("version") != version_number]
        if len(new_versions) != len(versions):
            q["versions"] = new_versions
            self.save_all()

    def update_version(
        self,
        query_name: str,
        old_version: str,
        new_version: str,
        before: str,
        after: str,
    ) -> None:
        q = self.get_query(query_name)
        if not q:
            return
        versions = q.setdefault("versions", [])
        for v in versions:
            if v.get("version") == old_version:
                v["version"] = new_version or old_version
                v["before"] = before or ""
                v["after"] = after or ""
                self.save_all()
                return
