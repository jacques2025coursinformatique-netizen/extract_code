import os
import json
from tkinter import Tk, Button, Label, filedialog, messagebox

DEFAULT_EXCLUDES = ["venv", "code_source", "archive", ".env", "__pycache__"]

selected_project_path = None


def load_excludes(path):
    excludes = set(DEFAULT_EXCLUDES)
    exclude_file = os.path.join(path, "code_source", "exclude.txt")

    if os.path.exists(exclude_file):
        with open(exclude_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    excludes.add(line)

    return excludes


def should_exclude(name, excludes):
    return any(name == ex or name.startswith(ex) for ex in excludes)


def scan_project(root_path, excludes):
    organisation = {}
    files_content = {}

    for current_root, dirs, files in os.walk(root_path):
        rel_root = os.path.relpath(current_root, root_path)

        dirs[:] = [d for d in dirs if not should_exclude(d, excludes)]

        organisation[rel_root] = {
            "dirs": dirs,
            "files": [f for f in files if not should_exclude(f, excludes)]
        }

        for f in files:
            if should_exclude(f, excludes):
                continue

            file_path = os.path.join(current_root, f)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                    files_content[os.path.join(rel_root, f)] = fp.read()
            except Exception:
                files_content[os.path.join(rel_root, f)] = "<< Impossible de lire ce fichier >>"

    return organisation, files_content


def generate_markdown(organisation, files_content):
    md = "# Organisation du projet\n\n"

    for folder, content in organisation.items():
        md += f"## {folder}\n"
        md += "**Dossiers :**\n"
        for d in content["dirs"]:
            md += f"- {d}\n"
        md += "\n**Fichiers :**\n"
        for f in content["files"]:
            md += f"- {f}\n"
        md += "\n---\n"

    md += "\n# Contenu des fichiers\n\n"
    for filepath, text in files_content.items():
        md += f"## {filepath}\n\n"
        md += "```\n"
        md += text
        md += "\n```\n\n"

    return md


def create_code_source_structure(path):
    code_source_path = os.path.join(path, "code_source")
    os.makedirs(code_source_path, exist_ok=True)

    exclude_file = os.path.join(code_source_path, "exclude.txt")

    if not os.path.exists(exclude_file):
        with open(exclude_file, "w", encoding="utf-8") as f:
            f.write("\n".join(DEFAULT_EXCLUDES))
        messagebox.showinfo(
            "Étape 1 terminée",
            "Le dossier code_source a été créé.\n"
            "Le fichier exclude.txt a été généré avec les exclusions par défaut.\n"
            "Vous pouvez maintenant le compléter."
        )
    else:
        messagebox.showinfo(
            "Étape 1 terminée",
            "Le dossier code_source existe déjà.\n"
            "Le fichier exclude.txt existant a été conservé.\n"
            "Vous pouvez le modifier avant de générer les fichiers."
        )


def generate_outputs():
    global selected_project_path

    if not selected_project_path:
        messagebox.showerror("Erreur", "Aucun projet sélectionné.")
        return

    excludes = load_excludes(selected_project_path)
    organisation, files_content = scan_project(selected_project_path, excludes)

    code_source_path = os.path.join(selected_project_path, "code_source")

    with open(os.path.join(code_source_path, "organisation.json"), "w", encoding="utf-8") as f:
        json.dump(organisation, f, indent=4, ensure_ascii=False)

    with open(os.path.join(code_source_path, "files_content.json"), "w", encoding="utf-8") as f:
        json.dump(files_content, f, indent=4, ensure_ascii=False)

    md = generate_markdown(organisation, files_content)
    with open(os.path.join(code_source_path, "context.md"), "w", encoding="utf-8") as f:
        f.write(md)

    messagebox.showinfo("Succès", "Les fichiers JSON et Markdown ont été générés.")


def select_folder():
    global selected_project_path
    folder = filedialog.askdirectory()

    if folder:
        selected_project_path = folder
        create_code_source_structure(folder)


def main():
    root = Tk()
    root.title("Extraction code source")

    Label(root, text="Étape 1 : Sélectionnez un dossier projet").pack(pady=10)
    Button(root, text="Choisir un dossier", command=select_folder).pack(pady=10)

    Label(root, text="Étape 2 : Après modification de exclude.txt").pack(pady=10)
    Button(root, text="Générer les fichiers JSON et MD", command=generate_outputs).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
