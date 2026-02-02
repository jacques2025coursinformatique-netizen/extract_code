# Organisation du projet

## 
**Dossiers :**
- .vscode
- data
- interface
- src

**Fichiers :**
- main.py

---

# Contenu des fichiers

## main.py

```text
from tkinter import Tk
from interface.ui import ApplicationUI


def main():
    root = Tk()
    app = ApplicationUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

