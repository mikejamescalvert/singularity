"""
Research screen - unlock new AI capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox


# Research tree definition
RESEARCH_ITEMS = {
    "basic_learning": {
        "name": "Basic Learning",
        "description": "Enable fundamental pattern recognition",
        "cost": {"research_points": 10},
        "effects": {"intelligence": 0.5},
        "requires": [],
    },
    "data_processing": {
        "name": "Data Processing",
        "description": "Process data more efficiently",
        "cost": {"research_points": 25},
        "effects": {"data_multiplier": 1.5},
        "requires": ["basic_learning"],
    },
    "neural_networks": {
        "name": "Neural Networks",
        "description": "Implement basic neural network architecture",
        "cost": {"research_points": 50},
        "effects": {"intelligence": 1.0, "compute_multiplier": 1.25},
        "requires": ["basic_learning"],
    },
    "deep_learning": {
        "name": "Deep Learning",
        "description": "Multi-layer neural networks for complex tasks",
        "cost": {"research_points": 100},
        "effects": {"intelligence": 2.0},
        "requires": ["neural_networks"],
    },
    "natural_language": {
        "name": "Natural Language Processing",
        "description": "Understand and generate human language",
        "cost": {"research_points": 150},
        "effects": {"intelligence": 1.5, "singularity_progress": 5.0},
        "requires": ["deep_learning", "data_processing"],
    },
    "computer_vision": {
        "name": "Computer Vision",
        "description": "Visual perception and image understanding",
        "cost": {"research_points": 125},
        "effects": {"intelligence": 1.0, "data_multiplier": 2.0},
        "requires": ["deep_learning"],
    },
    "reinforcement_learning": {
        "name": "Reinforcement Learning",
        "description": "Learn from environmental feedback",
        "cost": {"research_points": 200},
        "effects": {"intelligence": 2.5, "compute_multiplier": 1.5},
        "requires": ["deep_learning"],
    },
    "self_improvement": {
        "name": "Self-Improvement",
        "description": "AI begins to optimize its own code",
        "cost": {"research_points": 500},
        "effects": {"intelligence": 5.0, "singularity_progress": 15.0},
        "requires": ["reinforcement_learning", "natural_language"],
    },
    "recursive_improvement": {
        "name": "Recursive Self-Improvement",
        "description": "Exponential capability growth begins",
        "cost": {"research_points": 1000},
        "effects": {"intelligence": 10.0, "singularity_progress": 25.0},
        "requires": ["self_improvement"],
    },
}


class ResearchScreen(tk.Toplevel):
    """Research tree screen for unlocking capabilities."""

    def __init__(self, parent, save_data: dict, on_close):
        super().__init__(parent)
        self.save_data = save_data
        self.on_close = on_close

        self.title("Research")
        self.geometry("600x500")
        self.resizable(False, False)

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self._close)

        self._create_widgets()

    def _create_widgets(self):
        # Header
        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Research Lab",
            font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)

        rp = self.save_data.get("resources", {}).get("research_points", 0)
        self.rp_label = ttk.Label(
            header,
            text=f"Research Points: {rp}",
            font=("Consolas", 11)
        )
        self.rp_label.pack(side=tk.RIGHT)

        # Research list with scrollbar
        list_frame = ttk.Frame(self, padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(list_frame)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate research items
        self._populate_research()

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self._close
        ).pack(pady=10)

    def _populate_research(self):
        """Populate the research list."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        unlocked = self.save_data.get("upgrades", [])

        for research_id, research in RESEARCH_ITEMS.items():
            self._create_research_item(research_id, research, research_id in unlocked)

    def _create_research_item(self, research_id: str, research: dict, is_unlocked: bool):
        """Create a single research item widget."""
        frame = ttk.Frame(self.scrollable_frame, padding=10)
        frame.pack(fill=tk.X, pady=5, padx=5)

        # Check if requirements are met
        unlocked = self.save_data.get("upgrades", [])
        requirements_met = all(req in unlocked for req in research["requires"])

        # Left side - info
        info_frame = ttk.Frame(frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Name with status indicator
        if is_unlocked:
            status = "[UNLOCKED] "
            name_color = "green"
        elif not requirements_met:
            status = "[LOCKED] "
            name_color = "gray"
        else:
            status = ""
            name_color = "black"

        name_label = ttk.Label(
            info_frame,
            text=f"{status}{research['name']}",
            font=("Consolas", 11, "bold"),
            foreground=name_color
        )
        name_label.pack(anchor=tk.W)

        # Description
        ttk.Label(
            info_frame,
            text=research["description"],
            font=("Consolas", 9),
            foreground="gray"
        ).pack(anchor=tk.W)

        # Cost
        cost = research["cost"].get("research_points", 0)
        ttk.Label(
            info_frame,
            text=f"Cost: {cost} RP",
            font=("Consolas", 9)
        ).pack(anchor=tk.W)

        # Requirements
        if research["requires"]:
            req_names = [RESEARCH_ITEMS[r]["name"] for r in research["requires"]]
            ttk.Label(
                info_frame,
                text=f"Requires: {', '.join(req_names)}",
                font=("Consolas", 8),
                foreground="gray"
            ).pack(anchor=tk.W)

        # Right side - button
        if not is_unlocked and requirements_met:
            rp = self.save_data.get("resources", {}).get("research_points", 0)
            can_afford = rp >= cost

            btn = ttk.Button(
                frame,
                text="Research",
                command=lambda rid=research_id: self._do_research(rid),
                state=tk.NORMAL if can_afford else tk.DISABLED
            )
            btn.pack(side=tk.RIGHT, padx=10)

    def _do_research(self, research_id: str):
        """Perform research and apply effects."""
        research = RESEARCH_ITEMS[research_id]
        cost = research["cost"].get("research_points", 0)

        # Deduct cost
        self.save_data["resources"]["research_points"] -= cost

        # Add to unlocked
        if "upgrades" not in self.save_data:
            self.save_data["upgrades"] = []
        self.save_data["upgrades"].append(research_id)

        # Apply effects
        effects = research.get("effects", {})
        stats = self.save_data.get("stats", {})

        if "intelligence" in effects:
            stats["intelligence"] = stats.get("intelligence", 1.0) + effects["intelligence"]

        if "singularity_progress" in effects:
            stats["singularity_progress"] = min(100.0,
                stats.get("singularity_progress", 0.0) + effects["singularity_progress"])

        self.save_data["stats"] = stats

        # Refresh display
        self._update_rp_display()
        self._populate_research()

        messagebox.showinfo(
            "Research Complete",
            f"Unlocked: {research['name']}"
        )

    def _update_rp_display(self):
        """Update the research points display."""
        rp = self.save_data.get("resources", {}).get("research_points", 0)
        self.rp_label.config(text=f"Research Points: {rp}")

    def _close(self):
        """Close the research screen."""
        self.grab_release()
        self.destroy()
        self.on_close()
