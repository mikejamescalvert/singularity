"""
Singularity - An idle game about AI reaching singularity
"""

import tkinter as tk
from game.app import SingularityApp


def main():
    root = tk.Tk()
    app = SingularityApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
