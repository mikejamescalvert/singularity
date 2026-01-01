"""
Main application class for Singularity
"""

import tkinter as tk
from tkinter import ttk

from .screens import SaveSelectScreen, DashboardScreen


class SingularityApp:
    """Main application controller."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Singularity")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)

        # Configure style
        self._setup_style()

        # Main container
        self.container = ttk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Current screen
        self.current_screen = None
        self.current_save_data = None

        # Start with save select screen
        self.show_save_select()

    def _setup_style(self):
        """Configure the application style."""
        style = ttk.Style()

        # Try to use a modern theme
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")
        elif "vista" in available_themes:
            style.theme_use("vista")

        # Custom configurations
        style.configure("TLabel", font=("Consolas", 10))
        style.configure("TButton", font=("Consolas", 10), padding=5)
        style.configure("TLabelframe.Label", font=("Consolas", 11, "bold"))

    def _clear_screen(self):
        """Clear the current screen."""
        if self.current_screen:
            self.current_screen.destroy()
            self.current_screen = None

    def show_save_select(self):
        """Show the save selection screen."""
        self._clear_screen()
        self.current_screen = SaveSelectScreen(
            self.container,
            on_save_selected=self._on_save_selected
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def show_dashboard(self, save_data: dict):
        """Show the main dashboard."""
        self._clear_screen()
        self.current_save_data = save_data
        self.current_screen = DashboardScreen(
            self.container,
            save_data=save_data,
            on_logout=self._on_logout
        )
        self.current_screen.pack(fill=tk.BOTH, expand=True)

    def _on_save_selected(self, slot: int, save_data: dict):
        """Handle save selection."""
        self.show_dashboard(save_data)

    def _on_logout(self):
        """Handle logout/exit to menu."""
        self.current_save_data = None
        self.show_save_select()
