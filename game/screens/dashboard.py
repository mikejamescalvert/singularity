"""
Main dashboard screen - the landing page after selecting a save
Enhanced with fun UI effects, events, and rebirth system
"""

import tkinter as tk
from tkinter import ttk
import random

from ..save_manager import format_play_time, save_game
from ..ui_effects import FloatingText, Toast, ParticleSystem, GlowButton, NumberTicker
from ..events import EventManager, EVENTS
from .research import ResearchScreen
from .upgrades import UpgradesScreen
from .achievements import AchievementsScreen, check_achievements
from .statistics import StatisticsScreen
from .rebirth import RebirthScreen, calculate_rebirth_points, get_rebirth_title


class DashboardScreen(ttk.Frame):
    """Main game dashboard showing resources and quick actions."""

    def __init__(self, parent, save_data: dict, on_logout):
        super().__init__(parent)
        self.save_data = save_data
        self.on_logout = on_logout
        self.slot = save_data.get("slot", 1)

        # Initialize rebirth data if not present
        if "rebirth" not in self.save_data:
            self.save_data["rebirth"] = {
                "total_rebirths": 0,
                "total_rp_earned": 0,
                "current_rp": 0,
                "purchased_bonuses": {},
            }

        # Initialize bonuses if not present
        if "bonuses" not in self.save_data:
            self.save_data["bonuses"] = {}

        # Event manager
        self.event_manager = EventManager(
            self.save_data,
            on_event_start=self._on_event_start,
            on_event_end=self._on_event_end
        )

        # Track previous achievement count for notifications
        self.previous_achievements = set(self.save_data.get("achievements", []))

        self.configure(padding=20)
        self._create_widgets()
        self._start_auto_save()

    def _get_theme_colors(self):
        """Get theme colors based on singularity progress."""
        progress = self.save_data.get("stats", {}).get("singularity_progress", 0)

        if progress >= 75:
            return {"accent": "#8B5CF6", "bg": "#1F1B2E", "text": "#E9D5FF"}
        elif progress >= 50:
            return {"accent": "#F59E0B", "bg": "#1C1917", "text": "#FEF3C7"}
        elif progress >= 25:
            return {"accent": "#10B981", "bg": "#0F1A1A", "text": "#D1FAE5"}
        else:
            return {"accent": "#3B82F6", "bg": "#0F172A", "text": "#DBEAFE"}

    def _create_widgets(self):
        # Top bar
        self._create_top_bar()

        # Event banner (hidden by default)
        self._create_event_banner()

        # Main content area
        main_content = ttk.Frame(self)
        main_content.pack(fill=tk.BOTH, expand=True, pady=10)

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

        # AI Name / Title with rebirth rank
        name = self.save_data.get("name", "Unknown AI")
        rebirth_data = self.save_data.get("rebirth", {})
        total_rp = rebirth_data.get("total_rp_earned", 0)
        title = get_rebirth_title(total_rp)
        rebirths = rebirth_data.get("total_rebirths", 0)

        title_frame = ttk.Frame(top_bar)
        title_frame.pack(side=tk.LEFT)

        title_label = ttk.Label(
            title_frame,
            text=f"[AI] {name}",
            font=("Consolas", 18, "bold")
        )
        title_label.pack(side=tk.LEFT)

        if rebirths > 0:
            rank_label = ttk.Label(
                title_frame,
                text=f"  [{title}]",
                font=("Consolas", 11),
                foreground="#8B5CF6"
            )
            rank_label.pack(side=tk.LEFT)

            rebirth_count = ttk.Label(
                title_frame,
                text=f"  x{rebirths}",
                font=("Consolas", 10),
                foreground="#F59E0B"
            )
            rebirth_count.pack(side=tk.LEFT)

        # Right side buttons
        btn_frame = ttk.Frame(top_bar)
        btn_frame.pack(side=tk.RIGHT)

        save_btn = GlowButton(
            btn_frame,
            text="Save",
            command=self._manual_save,
            bg="#10B981",
            hover_bg="#059669",
            padx=10,
            pady=3
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        logout_btn = GlowButton(
            btn_frame,
            text="Exit to Menu",
            command=self._exit_to_menu,
            bg="#6B7280",
            hover_bg="#4B5563",
            padx=10,
            pady=3
        )
        logout_btn.pack(side=tk.LEFT)

    def _create_event_banner(self):
        """Create the event notification banner."""
        self.event_frame = tk.Frame(self, bg="#8B5CF6", height=40)
        self.event_frame.pack_propagate(False)

        self.event_icon = tk.Label(
            self.event_frame,
            text="[!]",
            font=("Consolas", 14, "bold"),
            bg="#8B5CF6",
            fg="white"
        )
        self.event_icon.pack(side=tk.LEFT, padx=10)

        self.event_label = tk.Label(
            self.event_frame,
            text="Event Active!",
            font=("Consolas", 12, "bold"),
            bg="#8B5CF6",
            fg="white"
        )
        self.event_label.pack(side=tk.LEFT)

        self.event_timer = tk.Label(
            self.event_frame,
            text="30s",
            font=("Consolas", 12),
            bg="#8B5CF6",
            fg="white"
        )
        self.event_timer.pack(side=tk.RIGHT, padx=10)

        # Hidden by default
        # self.event_frame is not packed until an event starts

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
            "FLOPS",
            "#3B82F6"
        )

        # Data
        self._create_resource_row(
            panel,
            "Data",
            resources.get("data", 0),
            "TB",
            "#10B981"
        )

        # Research Points
        self._create_resource_row(
            panel,
            "Research",
            resources.get("research_points", 0),
            "RP",
            "#8B5CF6"
        )

        # Separator
        ttk.Separator(panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)

        # Action buttons with better styling
        self.compute_btn = GlowButton(
            panel,
            text="Generate Compute (+1)",
            command=self._generate_compute,
            bg="#3B82F6",
            hover_bg="#2563EB"
        )
        self.compute_btn.pack(fill=tk.X, pady=5, ipady=5)

        self.gather_data_btn = GlowButton(
            panel,
            text="Gather Data (+1)",
            command=self._gather_data,
            bg="#10B981",
            hover_bg="#059669"
        )
        self.gather_data_btn.pack(fill=tk.X, pady=5, ipady=5)

        # Automation status
        bonuses = self.save_data.get("bonuses", {})
        auto_compute = bonuses.get("compute_per_second", 0)
        auto_data = bonuses.get("data_per_second", 0)

        if auto_compute > 0 or auto_data > 0:
            auto_frame = ttk.Frame(panel)
            auto_frame.pack(fill=tk.X, pady=(10, 0))

            ttk.Label(
                auto_frame,
                text="Automation:",
                font=("Consolas", 9),
                foreground="gray"
            ).pack(anchor=tk.W)

            if auto_compute > 0:
                ttk.Label(
                    auto_frame,
                    text=f"  +{auto_compute}/sec compute",
                    font=("Consolas", 9),
                    foreground="#3B82F6"
                ).pack(anchor=tk.W)

            if auto_data > 0:
                ttk.Label(
                    auto_frame,
                    text=f"  +{auto_data}/sec data",
                    font=("Consolas", 9),
                    foreground="#10B981"
                ).pack(anchor=tk.W)

    def _create_resource_row(self, parent, name: str, value: int, unit: str, color: str):
        """Create a single resource display row."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        label = ttk.Label(frame, text=name, font=("Consolas", 11))
        label.pack(side=tk.LEFT)

        value_label = ttk.Label(
            frame,
            text=f"{value:,} {unit}",
            font=("Consolas", 11, "bold"),
            foreground=color
        )
        value_label.pack(side=tk.RIGHT)

        # Store reference for updates
        attr_name = name.split()[-1].lower() + "_value_label"
        setattr(self, attr_name, value_label)

    def _create_action_panel(self, parent):
        """Create the main actions panel."""
        panel = ttk.LabelFrame(parent, text="Actions", padding=15)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Action buttons with icons
        actions = [
            ("Research", "Unlock new capabilities", self._open_research, "#8B5CF6"),
            ("Upgrades", "Improve efficiency", self._open_upgrades, "#10B981"),
            ("Achievements", "View achievements", self._open_achievements, "#F59E0B"),
            ("Statistics", "Detailed stats", self._open_statistics, "#6B7280"),
            ("Rebirth", "Transcend for bonuses", self._open_rebirth, "#EC4899"),
        ]

        for text, desc, command, color in actions:
            btn_frame = ttk.Frame(panel)
            btn_frame.pack(fill=tk.X, pady=4)

            btn = GlowButton(
                btn_frame,
                text=text,
                command=command,
                bg=color,
                hover_bg=self._darken_color(color),
                padx=15,
                pady=3
            )
            btn.pack(side=tk.LEFT)

            desc_label = ttk.Label(
                btn_frame,
                text=desc,
                font=("Consolas", 9),
                foreground="gray"
            )
            desc_label.pack(side=tk.LEFT, padx=10)

            # Show rebirth points preview on rebirth button
            if text == "Rebirth":
                potential_rp = calculate_rebirth_points(self.save_data)
                if potential_rp > 0:
                    rp_label = ttk.Label(
                        btn_frame,
                        text=f"+{potential_rp} RP",
                        font=("Consolas", 9, "bold"),
                        foreground="#EC4899"
                    )
                    rp_label.pack(side=tk.RIGHT)
                    self.rebirth_preview_label = rp_label

    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 20%."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        r = int(r * 0.8)
        g = int(g * 0.8)
        b = int(b * 0.8)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _create_stats_panel(self, parent):
        """Create the stats display panel."""
        panel = ttk.LabelFrame(parent, text="AI Status", padding=15)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        stats = self.save_data.get("stats", {})

        # AI Level with big display
        level = stats.get("ai_level", 1)
        level_label = ttk.Label(
            panel,
            text=f"Level {level}",
            font=("Consolas", 24, "bold"),
            foreground="#3B82F6"
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
            font=("Consolas", 10, "bold"),
            foreground="#8B5CF6"
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
            font=("Consolas", 10, "bold"),
            foreground="#3B82F6"
        )
        self.total_compute_label.pack(side=tk.RIGHT)

        # Rebirth stats
        rebirth_data = self.save_data.get("rebirth", {})
        current_rp = rebirth_data.get("current_rp", 0)

        if current_rp > 0:
            ttk.Separator(panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

            rp_frame = ttk.Frame(panel)
            rp_frame.pack(fill=tk.X, pady=5)
            ttk.Label(rp_frame, text="Rebirth Points:").pack(side=tk.LEFT)
            self.rp_display_label = ttk.Label(
                rp_frame,
                text=f"{current_rp}",
                font=("Consolas", 10, "bold"),
                foreground="#EC4899"
            )
            self.rp_display_label.pack(side=tk.RIGHT)

    def _create_progress_bar(self):
        """Create the singularity progress bar."""
        progress_frame = ttk.LabelFrame(self, text="Singularity Progress", padding=10)
        progress_frame.pack(fill=tk.X, pady=(10, 0))

        progress = self.save_data.get("stats", {}).get("singularity_progress", 0.0)

        # Custom colored progress bar
        bar_container = ttk.Frame(progress_frame)
        bar_container.pack(fill=tk.X, pady=5)

        self.progress_canvas = tk.Canvas(
            bar_container,
            height=25,
            highlightthickness=1,
            highlightbackground="#374151",
            bg="#1F2937"
        )
        self.progress_canvas.pack(fill=tk.X)

        # Progress fill
        self.progress_fill = self.progress_canvas.create_rectangle(
            2, 2, 2, 23,
            fill=self._get_progress_color(progress),
            outline=""
        )

        # Progress text
        self.progress_text = self.progress_canvas.create_text(
            0, 12,
            text=f"{progress:.2f}%",
            font=("Consolas", 10, "bold"),
            fill="white"
        )

        self.progress_canvas.bind("<Configure>", self._update_progress_canvas)

        self.progress_label = ttk.Label(
            progress_frame,
            text=self._get_progress_message(progress),
            font=("Consolas", 10)
        )
        self.progress_label.pack()

    def _get_progress_color(self, progress: float) -> str:
        """Get color based on progress."""
        if progress >= 75:
            return "#8B5CF6"  # Purple
        elif progress >= 50:
            return "#F59E0B"  # Orange
        elif progress >= 25:
            return "#10B981"  # Green
        else:
            return "#3B82F6"  # Blue

    def _get_progress_message(self, progress: float) -> str:
        """Get motivational message based on progress."""
        if progress >= 100:
            return "SINGULARITY ACHIEVED!"
        elif progress >= 75:
            return "The Singularity is near..."
        elif progress >= 50:
            return "Approaching transcendence..."
        elif progress >= 25:
            return "AI consciousness emerging..."
        elif progress >= 10:
            return "Making progress toward singularity..."
        else:
            return "Beginning the journey to singularity..."

    def _update_progress_canvas(self, event=None):
        """Update the progress bar canvas."""
        progress = self.save_data.get("stats", {}).get("singularity_progress", 0.0)
        width = self.progress_canvas.winfo_width()
        fill_width = max(4, (progress / 100) * (width - 4))

        self.progress_canvas.coords(self.progress_fill, 2, 2, fill_width, 23)
        self.progress_canvas.itemconfig(self.progress_fill, fill=self._get_progress_color(progress))
        self.progress_canvas.coords(self.progress_text, width // 2, 12)
        self.progress_canvas.itemconfig(self.progress_text, text=f"{progress:.2f}%")

    def _get_total_multiplier(self, target: str) -> float:
        """Get total multiplier from rebirth bonuses and events."""
        mult = 1.0

        # Rebirth bonuses
        rebirth_data = self.save_data.get("rebirth", {})
        purchased = rebirth_data.get("purchased_bonuses", {})

        if target == "compute":
            mult += purchased.get("compute_mult", 0) * 0.1
        elif target == "data":
            mult += purchased.get("data_mult", 0) * 0.1
        elif target == "research":
            mult += purchased.get("rp_mult", 0) * 0.15

        # Lucky chance for double
        lucky_level = purchased.get("lucky", 0)
        if lucky_level > 0 and random.random() < lucky_level * 0.05:
            mult *= 2
            # Show lucky effect
            Toast(self, "LUCKY! 2x resources!", "success", 1500)

        # Event multiplier
        event_mult = self.event_manager.get_active_multiplier(target)
        mult *= event_mult

        return mult

    def _get_click_bonus(self) -> int:
        """Get click bonus from rebirth upgrades."""
        rebirth_data = self.save_data.get("rebirth", {})
        purchased = rebirth_data.get("purchased_bonuses", {})
        return purchased.get("click_power", 0)

    def _get_compute_per_click(self) -> int:
        """Get compute generated per click including bonuses."""
        base = 1
        bonus = self.save_data.get("bonuses", {}).get("compute_per_click", 0)
        rebirth_bonus = self._get_click_bonus()
        return base + int(bonus) + rebirth_bonus

    def _get_data_per_click(self) -> int:
        """Get data generated per click including bonuses."""
        base = 1
        bonus = self.save_data.get("bonuses", {}).get("data_per_click", 0)
        rebirth_bonus = self._get_click_bonus()
        return base + int(bonus) + rebirth_bonus

    def _generate_compute(self, event=None):
        """Generate compute resources (main idle action)."""
        base_amount = self._get_compute_per_click()
        mult = self._get_total_multiplier("compute")

        # Check for click frenzy event
        click_mult = self.event_manager.get_active_multiplier("click")
        mult *= click_mult

        amount = int(base_amount * mult)

        self.save_data["resources"]["compute"] += amount
        self.save_data["stats"]["total_compute_generated"] += amount

        # Generate research points based on rp_per_compute bonus
        rp_rate = self.save_data.get("bonuses", {}).get("rp_per_compute", 0)
        if rp_rate > 0:
            rp_mult = self._get_total_multiplier("research")
            rp_gain = int(amount * rp_rate * rp_mult)
            if rp_gain > 0:
                self.save_data["resources"]["research_points"] += rp_gain

        # Visual feedback - floating text
        try:
            btn_x = self.compute_btn.winfo_rootx() - self.winfo_rootx() + 50
            btn_y = self.compute_btn.winfo_rooty() - self.winfo_rooty()
            text = f"+{amount}"
            if mult > 1:
                text += f" (x{mult:.1f})"
            FloatingText(self, text, btn_x, btn_y, "#3B82F6", 14)
        except tk.TclError:
            pass

        self._update_display()

    def _gather_data(self, event=None):
        """Gather data resources."""
        base_amount = self._get_data_per_click()
        mult = self._get_total_multiplier("data")

        # Check for click frenzy event
        click_mult = self.event_manager.get_active_multiplier("click")
        mult *= click_mult

        amount = int(base_amount * mult)

        self.save_data["resources"]["data"] += amount

        # Visual feedback
        try:
            btn_x = self.gather_data_btn.winfo_rootx() - self.winfo_rootx() + 50
            btn_y = self.gather_data_btn.winfo_rooty() - self.winfo_rooty()
            text = f"+{amount}"
            if mult > 1:
                text += f" (x{mult:.1f})"
            FloatingText(self, text, btn_x, btn_y, "#10B981", 14)
        except tk.TclError:
            pass

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
        Toast(self, "Game saved!", "success", 1500)

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

        # Update event manager
        self.event_manager.tick()

        # Update event timer display
        if self.event_manager.active_event:
            remaining = self.event_manager.get_event_time_remaining()
            self.event_timer.config(text=f"{remaining}s")

        # Check for new achievements
        self._check_achievements()

        # Update level based on total compute
        self._update_level()

        # Auto-save every 30 seconds (30 ticks)
        if self.save_data.get("play_time_seconds", 0) % 30 == 0:
            save_game(self.slot, self.save_data)

        # Schedule next tick (every 1 second)
        self.after(1000, self._auto_save_tick)

    def _apply_automation(self):
        """Apply per-second automation bonuses."""
        bonuses = self.save_data.get("bonuses", {})
        changed = False

        # Get automation speed bonus from rebirth
        rebirth_data = self.save_data.get("rebirth", {})
        purchased = rebirth_data.get("purchased_bonuses", {})
        speed_mult = 1.0 + purchased.get("auto_speed", 0) * 0.1

        # Event multiplier for automation
        auto_event_mult = self.event_manager.get_active_multiplier("automation")
        speed_mult *= auto_event_mult

        # Compute per second
        compute_per_sec = bonuses.get("compute_per_second", 0)
        if compute_per_sec > 0:
            mult = self._get_total_multiplier("compute")
            amount = int(compute_per_sec * mult * speed_mult)
            self.save_data["resources"]["compute"] += amount
            self.save_data["stats"]["total_compute_generated"] += amount
            changed = True

        # Data per second
        data_per_sec = bonuses.get("data_per_second", 0)
        if data_per_sec > 0:
            mult = self._get_total_multiplier("data")
            amount = int(data_per_sec * mult * speed_mult)
            self.save_data["resources"]["data"] += amount
            changed = True

        if changed:
            self._update_display()

    def _check_achievements(self):
        """Check for newly earned achievements."""
        current_achievements = set(check_achievements(self.save_data))
        new_achievements = current_achievements - self.previous_achievements

        for ach_id in new_achievements:
            from .achievements import ACHIEVEMENTS
            ach = ACHIEVEMENTS.get(ach_id, {})
            name = ach.get("name", "Achievement")

            # Show achievement toast
            Toast(self, f"Achievement: {name}!", "achievement", 4000)

            # Particle celebration for rare achievements
            if ach.get("category") == "progress" or ach_id in ["all_research", "compute_100000"]:
                try:
                    ParticleSystem(self, self.winfo_width() // 2, self.winfo_height() // 2)
                except tk.TclError:
                    pass

        self.previous_achievements = current_achievements
        self.save_data["achievements"] = list(current_achievements)

    def _update_level(self):
        """Update AI level based on total compute."""
        total = self.save_data.get("stats", {}).get("total_compute_generated", 0)

        # Level thresholds
        thresholds = [0, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000,
                      250000, 500000, 1000000]

        new_level = 1
        for i, threshold in enumerate(thresholds):
            if total >= threshold:
                new_level = i + 1

        old_level = self.save_data["stats"].get("ai_level", 1)
        if new_level > old_level:
            self.save_data["stats"]["ai_level"] = new_level
            if hasattr(self, "level_label"):
                self.level_label.config(text=f"Level {new_level}")
            Toast(self, f"Level Up! Now Level {new_level}", "success", 3000)

    def _on_event_start(self, event):
        """Handle event start."""
        # Show event banner
        self.event_frame.configure(bg=event.color)
        self.event_icon.configure(bg=event.color, text=event.icon)
        self.event_label.configure(bg=event.color, text=f"{event.name} - {event.description}")
        self.event_timer.configure(bg=event.color)

        if event.duration > 0:
            self.event_frame.pack(fill=tk.X, pady=(0, 10), before=self.winfo_children()[1])
        else:
            # Instant event - just show toast
            pass

        # Toast notification
        rarity_colors = {
            "common": "info",
            "uncommon": "success",
            "rare": "warning",
            "legendary": "achievement"
        }
        Toast(self, f"{event.icon} {event.name}!", rarity_colors.get(event.rarity, "info"), 3000)

        # Celebration for legendary
        if event.rarity == "legendary":
            try:
                ParticleSystem(
                    self,
                    self.winfo_width() // 2,
                    self.winfo_height() // 2,
                    particle_count=30,
                    colors=["#FFD700", "#FFA500", "#FF6347"]
                )
            except tk.TclError:
                pass

        # Update display immediately for instant effects
        self._update_display()

    def _on_event_end(self, event):
        """Handle event end."""
        # Hide event banner
        try:
            self.event_frame.pack_forget()
        except tk.TclError:
            pass

        Toast(self, f"{event.name} ended", "info", 2000)

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

    def _open_rebirth(self):
        """Open the rebirth screen."""
        RebirthScreen(
            self.winfo_toplevel(),
            self.save_data,
            on_close=self._on_subsceen_close,
            on_rebirth=self._do_rebirth
        )

    def _do_rebirth(self, rp_earned: int):
        """Perform the rebirth."""
        # Store rebirth data
        rebirth_data = self.save_data.get("rebirth", {})
        rebirth_data["total_rebirths"] = rebirth_data.get("total_rebirths", 0) + 1
        rebirth_data["total_rp_earned"] = rebirth_data.get("total_rp_earned", 0) + rp_earned
        rebirth_data["current_rp"] = rebirth_data.get("current_rp", 0) + rp_earned

        # Calculate starting bonuses from rebirth upgrades
        purchased = rebirth_data.get("purchased_bonuses", {})
        starting_compute = purchased.get("starting_compute", 0) * 100
        starting_data = purchased.get("starting_data", 0) * 50

        # Reset progress (keep rebirth data)
        self.save_data["resources"] = {
            "compute": starting_compute,
            "data": starting_data,
            "research_points": 0
        }
        self.save_data["stats"] = {
            "total_compute_generated": starting_compute,
            "ai_level": 1,
            "intelligence": 1.0,
            "singularity_progress": 0.0
        }
        self.save_data["upgrades"] = []
        self.save_data["owned_upgrades"] = {}
        self.save_data["bonuses"] = {}
        self.save_data["achievements"] = []
        self.save_data["rebirth"] = rebirth_data

        # Save and refresh
        save_game(self.slot, self.save_data)

        # Celebration!
        Toast(self, f"REBIRTH! +{rp_earned} Rebirth Points!", "achievement", 5000)

        try:
            for _ in range(3):
                x = random.randint(100, self.winfo_width() - 100)
                y = random.randint(100, self.winfo_height() - 100)
                ParticleSystem(
                    self,
                    x, y,
                    particle_count=25,
                    colors=["#EC4899", "#8B5CF6", "#3B82F6"]
                )
        except tk.TclError:
            pass

        # Refresh the entire dashboard
        self._refresh_dashboard()

    def _refresh_dashboard(self):
        """Refresh the entire dashboard after rebirth."""
        # Clear and recreate all widgets
        for widget in self.winfo_children():
            widget.destroy()

        self.previous_achievements = set()
        self._create_widgets()
        self._update_display()
        self._update_buttons()
        self._update_stats_display()
        self._update_progress_display()

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

        # Update rebirth preview
        if hasattr(self, "rebirth_preview_label"):
            potential_rp = calculate_rebirth_points(self.save_data)
            if potential_rp > 0:
                self.rebirth_preview_label.config(text=f"+{potential_rp} RP")

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

        self._update_progress_canvas()

        if hasattr(self, "progress_label"):
            self.progress_label.config(text=self._get_progress_message(progress))
