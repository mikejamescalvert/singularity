"""
Rebirth screen - prestige system for permanent bonuses
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math


def calculate_rebirth_points(save_data: dict) -> int:
    """Calculate how many rebirth points would be earned from current progress."""
    stats = save_data.get("stats", {})

    # Based on singularity progress, intelligence, and total compute
    progress = stats.get("singularity_progress", 0)
    intelligence = stats.get("intelligence", 1)
    total_compute = stats.get("total_compute_generated", 0)

    # Minimum 25% progress to rebirth
    if progress < 25:
        return 0

    # Base points from progress (exponential scaling)
    base_points = int((progress / 10) ** 1.5)

    # Bonus from intelligence
    int_bonus = int(math.log10(max(intelligence, 1) + 1) * 5)

    # Bonus from total compute (logarithmic)
    compute_bonus = int(math.log10(max(total_compute, 1) + 1) * 2)

    return base_points + int_bonus + compute_bonus


def get_rebirth_bonuses(rebirth_points: int) -> dict:
    """Get all available rebirth bonuses and their costs."""
    return {
        "starting_compute": {
            "name": "Head Start: Compute",
            "description": "Start with bonus compute after rebirth",
            "cost": 1,
            "max_level": 20,
            "effect_per_level": 100,
            "effect_description": "+100 starting compute per level",
        },
        "starting_data": {
            "name": "Head Start: Data",
            "description": "Start with bonus data after rebirth",
            "cost": 1,
            "max_level": 20,
            "effect_per_level": 50,
            "effect_description": "+50 starting data per level",
        },
        "compute_mult": {
            "name": "Enhanced Processing",
            "description": "Permanent compute multiplier",
            "cost": 3,
            "max_level": 10,
            "effect_per_level": 0.1,
            "effect_description": "+10% compute per level",
        },
        "data_mult": {
            "name": "Data Optimization",
            "description": "Permanent data multiplier",
            "cost": 3,
            "max_level": 10,
            "effect_per_level": 0.1,
            "effect_description": "+10% data per level",
        },
        "rp_mult": {
            "name": "Research Efficiency",
            "description": "Permanent research point multiplier",
            "cost": 5,
            "max_level": 10,
            "effect_per_level": 0.15,
            "effect_description": "+15% research points per level",
        },
        "click_power": {
            "name": "Quantum Fingers",
            "description": "Bonus resources per click",
            "cost": 2,
            "max_level": 15,
            "effect_per_level": 1,
            "effect_description": "+1 per click (all resources)",
        },
        "auto_speed": {
            "name": "Overclocked",
            "description": "Automation runs faster",
            "cost": 10,
            "max_level": 5,
            "effect_per_level": 0.1,
            "effect_description": "+10% automation speed",
        },
        "lucky": {
            "name": "Lucky AI",
            "description": "Chance for double resources",
            "cost": 8,
            "max_level": 5,
            "effect_per_level": 0.05,
            "effect_description": "+5% chance for 2x resources",
        },
    }


REBIRTH_TITLES = [
    ("Novice AI", 0),
    ("Apprentice AI", 5),
    ("Journeyman AI", 15),
    ("Expert AI", 30),
    ("Master AI", 50),
    ("Grandmaster AI", 100),
    ("Legendary AI", 200),
    ("Mythical AI", 500),
    ("Transcendent AI", 1000),
    ("Eternal AI", 2500),
    ("Infinite AI", 5000),
]


def get_rebirth_title(total_rp_earned: int) -> str:
    """Get the title based on total rebirth points earned."""
    title = REBIRTH_TITLES[0][0]
    for name, threshold in REBIRTH_TITLES:
        if total_rp_earned >= threshold:
            title = name
    return title


class RebirthScreen(tk.Toplevel):
    """Rebirth/Prestige screen for permanent progression."""

    def __init__(self, parent, save_data: dict, on_close, on_rebirth):
        super().__init__(parent)
        self.save_data = save_data
        self.on_close = on_close
        self.on_rebirth = on_rebirth

        self.title("Rebirth - Transcend Your Limits")
        self.geometry("700x550")
        self.resizable(False, False)

        # Modal
        self.transient(parent)
        self.grab_set()

        self.protocol("WM_DELETE_WINDOW", self._close)

        # Initialize rebirth data if not present
        if "rebirth" not in self.save_data:
            self.save_data["rebirth"] = {
                "total_rebirths": 0,
                "total_rp_earned": 0,
                "current_rp": 0,
                "purchased_bonuses": {},
            }

        self._create_widgets()

    def _create_widgets(self):
        rebirth_data = self.save_data.get("rebirth", {})
        potential_rp = calculate_rebirth_points(self.save_data)
        current_rp = rebirth_data.get("current_rp", 0)
        total_rebirths = rebirth_data.get("total_rebirths", 0)
        total_rp_earned = rebirth_data.get("total_rp_earned", 0)

        # Header
        header = ttk.Frame(self, padding=15)
        header.pack(fill=tk.X)

        title = get_rebirth_title(total_rp_earned)
        ttk.Label(
            header,
            text=f"Rebirth Chamber",
            font=("Consolas", 18, "bold")
        ).pack(side=tk.LEFT)

        ttk.Label(
            header,
            text=f"Rank: {title}",
            font=("Consolas", 12),
            foreground="#8B5CF6"
        ).pack(side=tk.RIGHT)

        # Stats frame
        stats_frame = ttk.LabelFrame(self, text="Rebirth Status", padding=10)
        stats_frame.pack(fill=tk.X, padx=15, pady=5)

        stats_inner = ttk.Frame(stats_frame)
        stats_inner.pack(fill=tk.X)

        # Left stats
        left_stats = ttk.Frame(stats_inner)
        left_stats.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(left_stats, text=f"Total Rebirths: {total_rebirths}",
                  font=("Consolas", 10)).pack(anchor=tk.W)
        ttk.Label(left_stats, text=f"Lifetime RP Earned: {total_rp_earned}",
                  font=("Consolas", 10)).pack(anchor=tk.W)

        # Right stats
        right_stats = ttk.Frame(stats_inner)
        right_stats.pack(side=tk.RIGHT)

        self.rp_label = ttk.Label(
            right_stats,
            text=f"Available RP: {current_rp}",
            font=("Consolas", 14, "bold"),
            foreground="#10B981"
        )
        self.rp_label.pack()

        # Rebirth button section
        rebirth_frame = ttk.LabelFrame(self, text="Perform Rebirth", padding=10)
        rebirth_frame.pack(fill=tk.X, padx=15, pady=5)

        progress = self.save_data.get("stats", {}).get("singularity_progress", 0)
        can_rebirth = progress >= 25

        rebirth_info = ttk.Frame(rebirth_frame)
        rebirth_info.pack(fill=tk.X)

        if can_rebirth:
            info_text = f"Rebirth now to earn {potential_rp} Rebirth Points!"
            info_color = "#10B981"
        else:
            info_text = f"Reach 25% singularity progress to rebirth (current: {progress:.1f}%)"
            info_color = "#EF4444"

        ttk.Label(
            rebirth_info,
            text=info_text,
            font=("Consolas", 11),
            foreground=info_color
        ).pack(side=tk.LEFT)

        # Custom styled rebirth button
        rebirth_btn = tk.Button(
            rebirth_info,
            text=f"REBIRTH (+{potential_rp} RP)",
            command=self._do_rebirth,
            state=tk.NORMAL if can_rebirth else tk.DISABLED,
            font=("Consolas", 11, "bold"),
            bg="#8B5CF6" if can_rebirth else "#6B7280",
            fg="white",
            activebackground="#7C3AED",
            activeforeground="white",
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2" if can_rebirth else "arrow"
        )
        rebirth_btn.pack(side=tk.RIGHT, padx=5)

        ttk.Label(
            rebirth_frame,
            text="Warning: Rebirth resets your resources, upgrades, and research!",
            font=("Consolas", 9),
            foreground="#F59E0B"
        ).pack(anchor=tk.W, pady=(5, 0))

        # Bonuses section with notebook
        bonuses_frame = ttk.LabelFrame(self, text="Permanent Bonuses", padding=10)
        bonuses_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Create scrollable canvas
        canvas = tk.Canvas(bonuses_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(bonuses_frame, orient="vertical", command=canvas.yview)
        self.bonuses_inner = ttk.Frame(canvas)

        self.bonuses_inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.bonuses_inner, anchor="nw", width=640)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self._populate_bonuses()

        # Close button
        ttk.Button(
            self,
            text="Close",
            command=self._close
        ).pack(pady=10)

    def _populate_bonuses(self):
        """Populate the bonuses list."""
        for widget in self.bonuses_inner.winfo_children():
            widget.destroy()

        rebirth_data = self.save_data.get("rebirth", {})
        current_rp = rebirth_data.get("current_rp", 0)
        purchased = rebirth_data.get("purchased_bonuses", {})

        bonuses = get_rebirth_bonuses(current_rp)

        for bonus_id, bonus in bonuses.items():
            self._create_bonus_item(bonus_id, bonus, purchased.get(bonus_id, 0), current_rp)

    def _create_bonus_item(self, bonus_id: str, bonus: dict, current_level: int, current_rp: int):
        """Create a single bonus item widget."""
        max_level = bonus["max_level"]
        is_maxed = current_level >= max_level

        frame = ttk.Frame(self.bonuses_inner, padding=8)
        frame.pack(fill=tk.X, pady=3)

        # Info section
        info_frame = ttk.Frame(frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Name with level
        level_text = f" (Lv {current_level}/{max_level})"
        name_color = "#10B981" if is_maxed else "#1F2937"

        name_label = ttk.Label(
            info_frame,
            text=f"{bonus['name']}{level_text}",
            font=("Consolas", 11, "bold"),
            foreground=name_color
        )
        name_label.pack(anchor=tk.W)

        ttk.Label(
            info_frame,
            text=bonus["description"],
            font=("Consolas", 9),
            foreground="gray"
        ).pack(anchor=tk.W)

        ttk.Label(
            info_frame,
            text=bonus["effect_description"],
            font=("Consolas", 9),
            foreground="#6366F1"
        ).pack(anchor=tk.W)

        # Cost and button
        if not is_maxed:
            cost = bonus["cost"]
            can_afford = current_rp >= cost

            cost_label = ttk.Label(
                frame,
                text=f"Cost: {cost} RP",
                font=("Consolas", 10),
                foreground="#10B981" if can_afford else "#EF4444"
            )
            cost_label.pack(side=tk.RIGHT, padx=10)

            btn = tk.Button(
                frame,
                text="Buy",
                command=lambda bid=bonus_id, bcost=cost: self._buy_bonus(bid, bcost),
                state=tk.NORMAL if can_afford else tk.DISABLED,
                font=("Consolas", 10),
                bg="#3B82F6" if can_afford else "#9CA3AF",
                fg="white",
                activebackground="#2563EB",
                relief=tk.FLAT,
                padx=10,
                pady=2,
                cursor="hand2" if can_afford else "arrow"
            )
            btn.pack(side=tk.RIGHT)
        else:
            ttk.Label(
                frame,
                text="MAXED",
                font=("Consolas", 10, "bold"),
                foreground="#10B981"
            ).pack(side=tk.RIGHT, padx=10)

    def _buy_bonus(self, bonus_id: str, cost: int):
        """Purchase a rebirth bonus."""
        rebirth_data = self.save_data["rebirth"]

        # Deduct cost
        rebirth_data["current_rp"] -= cost

        # Increment level
        if "purchased_bonuses" not in rebirth_data:
            rebirth_data["purchased_bonuses"] = {}
        current = rebirth_data["purchased_bonuses"].get(bonus_id, 0)
        rebirth_data["purchased_bonuses"][bonus_id] = current + 1

        # Update display
        self.rp_label.config(text=f"Available RP: {rebirth_data['current_rp']}")
        self._populate_bonuses()

    def _do_rebirth(self):
        """Perform a rebirth."""
        potential_rp = calculate_rebirth_points(self.save_data)

        if potential_rp <= 0:
            messagebox.showwarning("Cannot Rebirth", "You need at least 25% singularity progress to rebirth!")
            return

        # Confirm rebirth
        result = messagebox.askyesno(
            "Confirm Rebirth",
            f"Are you sure you want to rebirth?\n\n"
            f"You will earn: {potential_rp} Rebirth Points\n\n"
            f"This will reset:\n"
            f"  - All resources (compute, data, RP)\n"
            f"  - All research progress\n"
            f"  - All upgrades\n"
            f"  - Singularity progress\n\n"
            f"Permanent bonuses will be kept!",
            icon="warning"
        )

        if result:
            self._close()
            self.on_rebirth(potential_rp)

    def _close(self):
        """Close the rebirth screen."""
        self.grab_release()
        self.destroy()
        self.on_close()
