"""
Main dashboard screen - the landing page after selecting a save
"""

import tkinter as tk
from tkinter import ttk

from ..save_manager import format_play_time, save_game
from .research import ResearchScreen
from .upgrades import UpgradesScreen
from .achievements import AchievementsScreen
from .statistics import StatisticsScreen


class DashboardScreen(ttk.Frame):
    """Main game dashboard showing resources and quick actions."""

    def __init__(self, parent, save_data: dict, on_logout):
        super().__init__(parent)
        self.save_data = save_data
        self.on_logout = on_logout
        self.slot = save_data.get("slot", 1)

        self.configure(padding=20)
        self._create_widgets()
        self._start_auto_save()

    def _create_widgets(self):
        # Top bar
        self._create_top_bar()

        # Main content area
        main_content = ttk.Frame(self)
        main_content.pack(fill=tk.BOTH, expand=True, pady=20)

        # Left panel - Resources
        self._create_resource_panel(main_content)

        # Center panel - Main actions
        self._create_action_panel(main_content)

        # Right panel - Stats
        self._create_stats_panel(main_content)

        # Bottom bar - Progress
        self._create_progress_bar()

    def _create_top_bar(self):
        """Create the top navigation bar."""
        top_bar = ttk.Frame(self)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        # AI Name / Title
        name = self.save_data.get("name", "Unknown AI")
        title_label = ttk.Label(
            top_bar,
            text=f"[AI] {name}",
            font=("Consolas", 18, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # Right side buttons
        btn_frame = ttk.Frame(top_bar)
        btn_frame.pack(side=tk.RIGHT)

        save_btn = ttk.Button(
            btn_frame,
            text="Save",
            command=self._manual_save,
            width=8
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        logout_btn = ttk.Button(
            btn_frame,
            text="Exit to Menu",
            command=self._exit_to_menu,
            width=12
        )
        logout_btn.pack(side=tk.LEFT)

    def _create_resource_panel(self, parent):
        """Create the resources display panel."""
        panel = ttk.LabelFrame(parent, text="Resources", padding=15)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        resources = self.save_data.get("resources", {})

        # Compute
        self._create_resource_row(
            panel,
            "Compute",
            resources.get("compute", 0),
            "FLOPS"
        )

        # Data
        self._create_resource_row(
            panel,
            "Data",
            resources.get("data", 0),
            "TB"
        )

        # Research Points
        self._create_resource_row(
            panel,
            "Research",
            resources.get("research_points", 0),
            "RP"
        )

        # Separator
        ttk.Separator(panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # Generate compute button (main idle action)
        self.compute_btn = ttk.Button(
            panel,
            text="Generate Compute (+1)",
            command=self._generate_compute,
            takefocus=False
        )
        self.compute_btn.pack(fill=tk.X, pady=5)

        self.gather_data_btn = ttk.Button(
            panel,
            text="Gather Data (+1)",
            command=self._gather_data,
            takefocus=False
        )
        self.gather_data_btn.pack(fill=tk.X, pady=5)

    def _create_resource_row(self, parent, name: str, value: int, unit: str):
        """Create a single resource display row."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        label = ttk.Label(frame, text=name, font=("Consolas", 11))
        label.pack(side=tk.LEFT)

        value_label = ttk.Label(
            frame,
            text=f"{value:,} {unit}",
            font=("Consolas", 11, "bold")
        )
        value_label.pack(side=tk.RIGHT)

        # Store reference for updates
        attr_name = name.split()[-1].lower() + "_value_label"
        setattr(self, attr_name, value_label)

    def _create_action_panel(self, parent):
        """Create the main actions panel."""
        panel = ttk.LabelFrame(parent, text="Actions", padding=15)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Action buttons
        actions = [
            ("Research", "Unlock new capabilities", self._open_research),
            ("Upgrades", "Improve efficiency", self._open_upgrades),
            ("Achievements", "View achievements", self._open_achievements),
            ("Statistics", "Detailed stats", self._open_statistics),
        ]

        for text, desc, command in actions:
            btn_frame = ttk.Frame(panel)
            btn_frame.pack(fill=tk.X, pady=5)

            btn = ttk.Button(btn_frame, text=text, command=command, width=15)
            btn.pack(side=tk.LEFT)

            desc_label = ttk.Label(
                btn_frame,
                text=desc,
                font=("Consolas", 9),
                foreground="gray"
            )
            desc_label.pack(side=tk.LEFT, padx=10)

    def _create_stats_panel(self, parent):
        """Create the stats display panel."""
        panel = ttk.LabelFrame(parent, text="AI Status", padding=15)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        stats = self.save_data.get("stats", {})

        # AI Level
        level = stats.get("ai_level", 1)
        level_label = ttk.Label(
            panel,
            text=f"Level {level}",
            font=("Consolas", 24, "bold")
        )
        level_label.pack(pady=(0, 10))
        self.level_label = level_label

        # Intelligence
        intelligence = stats.get("intelligence", 1.0)
        int_frame = ttk.Frame(panel)
        int_frame.pack(fill=tk.X, pady=5)
        ttk.Label(int_frame, text="Intelligence:").pack(side=tk.LEFT)
        self.int_label = ttk.Label(
            int_frame,
            text=f"{intelligence:.2f}",
            font=("Consolas", 10, "bold")
        )
        self.int_label.pack(side=tk.RIGHT)

        # Play time
        play_time = stats.get("play_time_seconds", 0)
        time_frame = ttk.Frame(panel)
        time_frame.pack(fill=tk.X, pady=5)
        ttk.Label(time_frame, text="Play Time:").pack(side=tk.LEFT)
        self.time_label = ttk.Label(
            time_frame,
            text=format_play_time(play_time),
            font=("Consolas", 10, "bold")
        )
        self.time_label.pack(side=tk.RIGHT)

        # Total compute generated
        total_compute = stats.get("total_compute_generated", 0)
        total_frame = ttk.Frame(panel)
        total_frame.pack(fill=tk.X, pady=5)
        ttk.Label(total_frame, text="Total Compute:").pack(side=tk.LEFT)
        self.total_compute_label = ttk.Label(
            total_frame,
            text=f"{total_compute:,}",
            font=("Consolas", 10, "bold")
        )
        self.total_compute_label.pack(side=tk.RIGHT)

    def _create_progress_bar(self):
        """Create the singularity progress bar."""
        progress_frame = ttk.LabelFrame(self, text="Singularity Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        progress = self.save_data.get("stats", {}).get("singularity_progress", 0.0)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=400,
            mode='determinate',
            value=progress
        )
        self.progress_bar.pack(fill=tk.X, pady=5)

        self.progress_label = ttk.Label(
            progress_frame,
            text=f"{progress:.2f}% toward Singularity",
            font=("Consolas", 10)
        )
        self.progress_label.pack()

    def _get_compute_per_click(self) -> int:
        """Get compute generated per click including bonuses."""
        base = 1
        bonus = self.save_data.get("bonuses", {}).get("compute_per_click", 0)
        return base + int(bonus)

    def _get_data_per_click(self) -> int:
        """Get data generated per click including bonuses."""
        base = 1
        bonus = self.save_data.get("bonuses", {}).get("data_per_click", 0)
        return base + int(bonus)

    def _generate_compute(self):
        """Generate compute resources (main idle action)."""
        amount = self._get_compute_per_click()
        self.save_data["resources"]["compute"] += amount
        self.save_data["stats"]["total_compute_generated"] += amount

        # Generate research points based on rp_per_compute bonus
        rp_rate = self.save_data.get("bonuses", {}).get("rp_per_compute", 0)
        if rp_rate > 0:
            rp_gain = int(amount * rp_rate)
            if rp_gain > 0:
                self.save_data["resources"]["research_points"] += rp_gain

        self._update_display()

    def _gather_data(self):
        """Gather data resources."""
        amount = self._get_data_per_click()
        self.save_data["resources"]["data"] += amount
        self._update_display()

    def _update_display(self):
        """Update all displayed values."""
        resources = self.save_data.get("resources", {})
        stats = self.save_data.get("stats", {})

        # Update resource labels
        if hasattr(self, "compute_value_label"):
            self.compute_value_label.config(text=f"{resources.get('compute', 0):,} FLOPS")
        if hasattr(self, "data_value_label"):
            self.data_value_label.config(text=f"{resources.get('data', 0):,} TB")
        if hasattr(self, "research_value_label"):
            self.research_value_label.config(text=f"{resources.get('research_points', 0):,} RP")

        # Update stats
        if hasattr(self, "total_compute_label"):
            self.total_compute_label.config(text=f"{stats.get('total_compute_generated', 0):,}")

    def _manual_save(self):
        """Manually save the game."""
        save_game(self.slot, self.save_data)

    def _exit_to_menu(self):
        """Save and exit to the main menu."""
        save_game(self.slot, self.save_data)
        self.on_logout()

    def _start_auto_save(self):
        """Start auto-save timer."""
        self._auto_save_tick()

    def _auto_save_tick(self):
        """Auto-save every 30 seconds and update play time."""
        # Update play time
        self.save_data["play_time_seconds"] = self.save_data.get("play_time_seconds", 0) + 1

        if hasattr(self, "time_label"):
            self.time_label.config(
                text=format_play_time(self.save_data.get("play_time_seconds", 0))
            )

        # Apply automation bonuses (per second generation)
        self._apply_automation()

        # Auto-save every 30 seconds (30 ticks)
        if self.save_data.get("play_time_seconds", 0) % 30 == 0:
            save_game(self.slot, self.save_data)

        # Schedule next tick (every 1 second)
        self.after(1000, self._auto_save_tick)

    def _apply_automation(self):
        """Apply per-second automation bonuses."""
        bonuses = self.save_data.get("bonuses", {})
        changed = False

        # Compute per second
        compute_per_sec = bonuses.get("compute_per_second", 0)
        if compute_per_sec > 0:
            self.save_data["resources"]["compute"] += int(compute_per_sec)
            self.save_data["stats"]["total_compute_generated"] += int(compute_per_sec)
            changed = True

        # Data per second
        data_per_sec = bonuses.get("data_per_second", 0)
        if data_per_sec > 0:
            self.save_data["resources"]["data"] += int(data_per_sec)
            changed = True

        if changed:
            self._update_display()

    def _open_research(self):
        """Open the research screen."""
        ResearchScreen(
            self.winfo_toplevel(),
            self.save_data,
            on_close=self._on_subsceen_close
        )

    def _open_upgrades(self):
        """Open the upgrades screen."""
        UpgradesScreen(
            self.winfo_toplevel(),
            self.save_data,
            on_close=self._on_subsceen_close
        )

    def _open_achievements(self):
        """Open the achievements screen."""
        AchievementsScreen(
            self.winfo_toplevel(),
            self.save_data,
            on_close=self._on_subsceen_close
        )

    def _open_statistics(self):
        """Open the statistics screen."""
        StatisticsScreen(
            self.winfo_toplevel(),
            self.save_data,
            on_close=self._on_subsceen_close
        )

    def _on_subsceen_close(self):
        """Called when a subscreen is closed - refresh display."""
        self._update_display()
        self._update_buttons()
        self._update_stats_display()
        self._update_progress_display()

    def _update_buttons(self):
        """Update button text to reflect current bonuses."""
        compute_amount = self._get_compute_per_click()
        data_amount = self._get_data_per_click()

        if hasattr(self, "compute_btn"):
            self.compute_btn.config(text=f"Generate Compute (+{compute_amount})")
        if hasattr(self, "gather_data_btn"):
            self.gather_data_btn.config(text=f"Gather Data (+{data_amount})")

    def _update_stats_display(self):
        """Update the stats panel."""
        stats = self.save_data.get("stats", {})

        if hasattr(self, "level_label"):
            self.level_label.config(text=f"Level {stats.get('ai_level', 1)}")
        if hasattr(self, "int_label"):
            self.int_label.config(text=f"{stats.get('intelligence', 1.0):.2f}")

    def _update_progress_display(self):
        """Update the progress bar."""
        progress = self.save_data.get("stats", {}).get("singularity_progress", 0.0)

        if hasattr(self, "progress_bar"):
            self.progress_bar.config(value=progress)
        if hasattr(self, "progress_label"):
            self.progress_label.config(text=f"{progress:.2f}% toward Singularity")
