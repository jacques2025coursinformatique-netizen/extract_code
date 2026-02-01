from tkinter import Tk
from interface.ui import ApplicationUI


def main():
    root = Tk()
    app = ApplicationUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()