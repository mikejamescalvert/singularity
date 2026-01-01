"""
Upgrades screen - improve resource generation efficiency
"""

import tkinter as tk
from tkinter import ttk, messagebox


# Upgrade definitions
UPGRADES = {
    # Compute upgrades
    "better_cpu": {
        "name": "Better CPU",
        "description": "+1 compute per click",
        "category": "compute",
        "cost": {"compute": 50},
        "effect": {"compute_per_click": 1},
        "max_level": 10,
    },
    "gpu_cluster": {
        "name": "GPU Cluster",
        "description": "+5 compute per click",
        "category": "compute",
        "cost": {"compute": 500},
        "cost_multiplier": 1.5,
        "effect": {"compute_per_click": 5},
        "max_level": 5,
    },
    "quantum_processor": {
        "name": "Quantum Processor",
        "description": "+25 compute per click",
        "category": "compute",
        "cost": {"compute": 5000},
        "cost_multiplier": 2.0,
        "effect": {"compute_per_click": 25},
        "max_level": 3,
    },
    # Data upgrades
    "data_scraper": {
        "name": "Data Scraper",
        "description": "+1 data per click",
        "category": "data",
        "cost": {"data": 25},
        "effect": {"data_per_click": 1},
        "max_level": 10,
    },
    "data_center": {
        "name": "Data Center",
        "description": "+5 data per click",
        "category": "data",
        "cost": {"data": 250},
        "cost_multiplier": 1.5,
        "effect": {"data_per_click": 5},
        "max_level": 5,
    },
    # Research upgrades
    "research_lab": {
        "name": "Research Lab",
        "description": "Generate 1 RP per 100 compute spent",
        "category": "research",
        "cost": {"compute": 1000},
        "effect": {"rp_per_compute": 0.01},
        "max_level": 1,
    },
    "ai_researchers": {
        "name": "AI Researchers",
        "description": "Generate 1 RP per 50 compute spent",
        "category": "research",
        "cost": {"compute": 5000, "data": 1000},
        "effect": {"rp_per_compute": 0.02},
        "max_level": 1,
        "requires": ["research_lab"],
    },
    # Automation upgrades
    "auto_compute": {
        "name": "Auto Compute",
        "description": "+1 compute per second",
        "category": "automation",
        "cost": {"compute": 100},
        "cost_multiplier": 1.8,
        "effect": {"compute_per_second": 1},
        "max_level": 20,
    },
    "auto_data": {
        "name": "Auto Data Collection",
        "description": "+1 data per second",
        "category": "automation",
        "cost": {"data": 50},
        "cost_multiplier": 1.8,
        "effect": {"data_per_second": 1},
        "max_level": 20,
    },
}


class UpgradesScreen(tk.Toplevel):
    """Upgrades screen for improving efficiency."""

    def __init__(self, parent, save_data: dict, on_close):
        super().__init__(parent)
        self.save_data = save_data
        self.on_close = on_close

        self.title("Upgrades")
        self.geometry("650x500")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self._close)

        self._create_widgets()

    def _create_widgets(self):
        # Header with resources
        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Upgrades",
            font=("Consolas", 16, "bold")
        ).pack(side=tk.LEFT)

        # Resource display
        res_frame = ttk.Frame(header)
        res_frame.pack(side=tk.RIGHT)

        resources = self.save_data.get("resources", {})
        self.resource_labels = {}

        for res_name, res_value in resources.items():
            label = ttk.Label(
                res_frame,
                text=f"{res_name.replace('_', ' ').title()}: {res_value:,}",
                font=("Consolas", 9)
            )
            label.pack(side=tk.LEFT, padx=10)
            self.resource_labels[res_name] = label

        # Category notebook
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        categories = {
            "compute": "Compute",
            "data": "Data",
            "research": "Research",
            "automation": "Automation"
        }

        self.category_frames = {}
        for cat_id, cat_name in categories.items():
            frame = ttk.Frame(notebook, padding=10)
            notebook.add(frame, text=cat_name)
            self.category_frames[cat_id] = frame

        self._populate_upgrades()

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self._close
        ).pack(pady=10)

    def _populate_upgrades(self):
        """Populate all upgrade categories."""
        for cat_id, frame in self.category_frames.items():
            for widget in frame.winfo_children():
                widget.destroy()

            upgrades_in_cat = {k: v for k, v in UPGRADES.items() if v["category"] == cat_id}

            if not upgrades_in_cat:
                ttk.Label(frame, text="No upgrades available").pack()
                continue

            for upgrade_id, upgrade in upgrades_in_cat.items():
                self._create_upgrade_item(frame, upgrade_id, upgrade)

    def _create_upgrade_item(self, parent, upgrade_id: str, upgrade: dict):
        """Create a single upgrade widget."""
        # Get current level
        owned_upgrades = self.save_data.get("owned_upgrades", {})
        current_level = owned_upgrades.get(upgrade_id, 0)
        max_level = upgrade.get("max_level", 1)

        frame = ttk.Frame(parent, padding=8)
        frame.pack(fill=tk.X, pady=3)

        # Info
        info_frame = ttk.Frame(frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Name with level
        level_text = f" (Lv {current_level}/{max_level})" if max_level > 1 else ""
        is_maxed = current_level >= max_level

        name_label = ttk.Label(
            info_frame,
            text=f"{upgrade['name']}{level_text}",
            font=("Consolas", 11, "bold"),
            foreground="green" if is_maxed else "black"
        )
        name_label.pack(anchor=tk.W)

        ttk.Label(
            info_frame,
            text=upgrade["description"],
            font=("Consolas", 9),
            foreground="gray"
        ).pack(anchor=tk.W)

        # Cost (scaled by level)
        if not is_maxed:
            cost = self._calculate_cost(upgrade, current_level)
            cost_parts = [f"{v:,} {k.replace('_', ' ')}" for k, v in cost.items()]
            cost_text = "Cost: " + ", ".join(cost_parts)
        else:
            cost_text = "MAXED"
            cost = {}

        ttk.Label(
            info_frame,
            text=cost_text,
            font=("Consolas", 9)
        ).pack(anchor=tk.W)

        # Buy button
        if not is_maxed:
            can_afford = self._can_afford(cost)
            btn = ttk.Button(
                frame,
                text="Buy",
                command=lambda uid=upgrade_id: self._buy_upgrade(uid),
                state=tk.NORMAL if can_afford else tk.DISABLED,
                width=8
            )
            btn.pack(side=tk.RIGHT, padx=5)

    def _calculate_cost(self, upgrade: dict, current_level: int) -> dict:
        """Calculate cost based on current level."""
        base_cost = upgrade["cost"].copy()
        multiplier = upgrade.get("cost_multiplier", 1.0)

        for resource in base_cost:
            base_cost[resource] = int(base_cost[resource] * (multiplier ** current_level))

        return base_cost

    def _can_afford(self, cost: dict) -> bool:
        """Check if player can afford the cost."""
        resources = self.save_data.get("resources", {})
        for resource, amount in cost.items():
            if resources.get(resource, 0) < amount:
                return False
        return True

    def _buy_upgrade(self, upgrade_id: str):
        """Purchase an upgrade."""
        upgrade = UPGRADES[upgrade_id]
        owned = self.save_data.get("owned_upgrades", {})
        current_level = owned.get(upgrade_id, 0)

        cost = self._calculate_cost(upgrade, current_level)

        # Deduct cost
        for resource, amount in cost.items():
            self.save_data["resources"][resource] -= amount

        # Increment level
        if "owned_upgrades" not in self.save_data:
            self.save_data["owned_upgrades"] = {}
        self.save_data["owned_upgrades"][upgrade_id] = current_level + 1

        # Apply effects to stats
        self._apply_effects(upgrade["effect"])

        # Refresh
        self._update_resource_display()
        self._populate_upgrades()

    def _apply_effects(self, effects: dict):
        """Apply upgrade effects to save data."""
        if "bonuses" not in self.save_data:
            self.save_data["bonuses"] = {}

        for effect_name, effect_value in effects.items():
            current = self.save_data["bonuses"].get(effect_name, 0)
            self.save_data["bonuses"][effect_name] = current + effect_value

    def _update_resource_display(self):
        """Update the resource labels."""
        resources = self.save_data.get("resources", {})
        for res_name, label in self.resource_labels.items():
            value = resources.get(res_name, 0)
            label.config(text=f"{res_name.replace('_', ' ').title()}: {value:,}")

    def _close(self):
        """Close the upgrades screen."""
        self.grab_release()
        self.destroy()
        self.on_close()
