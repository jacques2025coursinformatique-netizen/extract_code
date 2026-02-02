import os
import json
from typing import Dict, List, Tuple
from .models import ProjectSnapshot


def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def list_existing_versions(code_source_dir: str) -> List[str]:
    if not os.path.isdir(code_source_dir):
        return []
    versions = set()
    for name in os.listdir(code_source_dir):
        if name.startswith("organisation.") and name.endswith(".json"):
            middle = name[len("organisation."):-len(".json")]
            versions.add(middle)
    return sorted(versions)


def get_next_version_number(code_source_dir: str) -> str:
    versions = list_existing_versions(code_source_dir)
    if not versions:
        return "001"
    last = max(int(v) for v in versions)
    return f"{last + 1:03d}"


def delete_version_files(code_source_dir: str, version: str) -> None:
    org = os.path.join(code_source_dir, f"organisation.{version}.json")
    fc = os.path.join(code_source_dir, f"files_content.{version}.json")
    for path in (org, fc):
        if os.path.exists(path):
            os.remove(path)


def generate_markdown(snapshot: ProjectSnapshot) -> str:
    md = "# Organisation du projet\n\n"
    for folder, content in snapshot.organisation.items():
        md += f"## {folder}\n"
        md += "**Dossiers :**\n"
        for d in content.get("dirs", []):
            md += f"- {d}\n"
        md += "\n**Fichiers :**\n"
        for f in content.get("files", []):
            md += f"- {f}\n"
        md += "\n---\n"

    md += "\n# Contenu des fichiers\n\n"
    for filepath, text in snapshot.files_content.items():
        md += f"## {filepath}\n\n"

        # 🔥 Échapper les backticks pour Notion
        safe_text = text.replace("```", "`` `")

        md += "```code\n"
        md += safe_text
        md += "\n```\n\n"

    return md



def generate_html(snapshot: ProjectSnapshot) -> str:
    """
    Version adaptée à Copilot :
    - HTML simple, non échappé
    - structure proche du Markdown
    - lisible comme un document texte dans Edge
    """
    parts: List[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append("<html>")
    parts.append("<head><meta charset='utf-8'><title>Context</title></head>")
    parts.append("<body>")
    parts.append("<h1>Organisation du projet</h1>")

    for folder, content in snapshot.organisation.items():
        parts.append(f"<h2>{folder}</h2>")
        parts.append("<h3>Dossiers :</h3><ul>")
        for d in content.get("dirs", []):
            parts.append(f"<li>{d}</li>")
        parts.append("</ul>")
        parts.append("<h3>Fichiers :</h3><ul>")
        for f in content.get("files", []):
            parts.append(f"<li>{f}</li>")
        parts.append("</ul><hr>")

    parts.append("<h1>Contenu des fichiers</h1>")
    for filepath, text in snapshot.files_content.items():
        parts.append(f"<h2>{filepath}</h2>")
        parts.append("<pre>")
        parts.append(text)
        parts.append("</pre>")

    parts.append("</body></html>")
    return "\n".join(parts)


def escape_html(text: str) -> str:
    # Gardée pour compatibilité éventuelle, mais plus utilisée dans generate_html
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def filter_snapshot(snapshot: ProjectSnapshot, selected_files: List[str]) -> ProjectSnapshot:
    selected_set = set(selected_files)
    filtered_files = {
        path: content
        for path, content in snapshot.files_content.items()
        if path in selected_set
    }

    filtered_org: Dict[str, Dict[str, List[str]]] = {}
    for folder, content in snapshot.organisation.items():
        files = [f for f in content.get("files", []) if os.path.join(folder, f) in selected_set]
        if files:
            filtered_org[folder] = {
                "dirs": content.get("dirs", []),
                "files": files,
            }

    return ProjectSnapshot(
        version=snapshot.version,
        organisation=filtered_org,
        files_content=filtered_files,
    )
