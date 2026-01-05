"""
UI Effects - Animations, visual feedback, and fun UI elements
"""

import tkinter as tk
from tkinter import ttk
import random
import math


class FloatingText:
    """Creates floating text that rises and fades out."""

    def __init__(self, parent, text: str, x: int, y: int, color: str = "#10B981",
                 font_size: int = 12, duration: int = 1000):
        self.parent = parent
        self.canvas = tk.Canvas(
            parent,
            width=150,
            height=50,
            highlightthickness=0,
            bg=parent.cget("bg") if hasattr(parent, 'cget') else "white"
        )

        # Make canvas transparent-ish
        self.canvas.configure(bg='SystemButtonFace')

        self.text_id = self.canvas.create_text(
            75, 25,
            text=text,
            font=("Consolas", font_size, "bold"),
            fill=color
        )

        # Position near the click
        self.canvas.place(x=x - 75, y=y - 25)

        self.start_y = y - 25
        self.current_step = 0
        self.total_steps = duration // 20
        self.duration = duration

        self._animate()

    def _animate(self):
        """Animate the floating text."""
        if self.current_step >= self.total_steps:
            self.canvas.destroy()
            return

        # Move up
        progress = self.current_step / self.total_steps
        new_y = self.start_y - (progress * 40)
        self.canvas.place(y=new_y)

        # Fade effect (change color intensity)
        alpha = 1 - progress
        # Simulate fade by changing to lighter color
        r = int(16 + (239 - 16) * (1 - alpha))
        g = int(185 + (239 - 185) * (1 - alpha))
        b = int(129 + (239 - 129) * (1 - alpha))
        color = f"#{r:02x}{g:02x}{b:02x}"

        try:
            self.canvas.itemconfig(self.text_id, fill=color)
        except tk.TclError:
            return

        self.current_step += 1
        self.parent.after(20, self._animate)


class PulseEffect:
    """Creates a pulse/glow effect on a widget."""

    def __init__(self, widget, color: str = "#10B981", duration: int = 300):
        self.widget = widget
        self.original_bg = None
        self.duration = duration
        self.steps = duration // 20
        self.current_step = 0

        # Store original background
        try:
            self.original_bg = widget.cget("background")
        except tk.TclError:
            self.original_bg = "SystemButtonFace"

        self._pulse()

    def _pulse(self):
        """Animate the pulse effect."""
        if self.current_step >= self.steps:
            try:
                self.widget.configure(background=self.original_bg)
            except tk.TclError:
                pass
            return

        # Calculate color interpolation
        progress = self.current_step / self.steps
        if progress < 0.5:
            # Fade in
            intensity = progress * 2
        else:
            # Fade out
            intensity = (1 - progress) * 2

        # Green pulse color
        r = int(240 - (240 - 16) * intensity)
        g = int(240 - (240 - 185) * intensity)
        b = int(240 - (240 - 129) * intensity)

        try:
            self.widget.configure(background=f"#{r:02x}{g:02x}{b:02x}")
        except tk.TclError:
            return

        self.current_step += 1
        self.widget.after(20, self._pulse)


class ShakeEffect:
    """Creates a shake effect on a widget."""

    def __init__(self, widget, intensity: int = 5, duration: int = 200):
        self.widget = widget
        self.intensity = intensity
        self.steps = duration // 20
        self.current_step = 0

        # Store original position
        self.original_x = widget.winfo_x()
        self.original_y = widget.winfo_y()

        self._shake()

    def _shake(self):
        """Animate the shake."""
        if self.current_step >= self.steps:
            return

        # Random offset
        offset_x = random.randint(-self.intensity, self.intensity)
        offset_y = random.randint(-self.intensity // 2, self.intensity // 2)

        # Apply offset via place (if using place) or just visual effect
        try:
            info = self.widget.place_info()
            if info:
                self.widget.place(x=self.original_x + offset_x, y=self.original_y + offset_y)
        except (tk.TclError, KeyError):
            pass

        self.current_step += 1
        self.widget.after(20, self._shake)


class ParticleSystem:
    """Creates particle effects for celebrations."""

    def __init__(self, parent, x: int, y: int, particle_count: int = 20,
                 colors: list = None, duration: int = 1500):
        self.parent = parent
        self.particles = []
        self.canvas = tk.Canvas(
            parent,
            width=300,
            height=200,
            highlightthickness=0,
            bg='SystemButtonFace'
        )
        self.canvas.place(x=x - 150, y=y - 100)

        colors = colors or ["#10B981", "#3B82F6", "#8B5CF6", "#F59E0B", "#EF4444"]

        # Create particles
        for _ in range(particle_count):
            particle = {
                'id': self.canvas.create_oval(145, 95, 155, 105,
                                              fill=random.choice(colors),
                                              outline=""),
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-8, -2),
                'gravity': 0.2,
                'x': 150,
                'y': 100
            }
            self.particles.append(particle)

        self.duration = duration
        self.start_time = 0
        self._animate()

    def _animate(self):
        """Animate all particles."""
        self.start_time += 20

        if self.start_time >= self.duration:
            self.canvas.destroy()
            return

        for particle in self.particles:
            # Update velocity
            particle['vy'] += particle['gravity']

            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # Move particle
            try:
                self.canvas.coords(
                    particle['id'],
                    particle['x'] - 5,
                    particle['y'] - 5,
                    particle['x'] + 5,
                    particle['y'] + 5
                )
            except tk.TclError:
                return

        self.parent.after(20, self._animate)


class ProgressBarAnimated:
    """An animated progress bar with color transitions."""

    def __init__(self, parent, initial_value: float = 0, **kwargs):
        self.frame = ttk.Frame(parent)
        self.target_value = initial_value
        self.current_value = initial_value

        # Create canvas for custom progress bar
        self.canvas = tk.Canvas(
            self.frame,
            height=25,
            highlightthickness=1,
            highlightbackground="#374151",
            bg="#1F2937"
        )
        self.canvas.pack(fill=tk.X, expand=True)

        # Progress bar fill
        self.bar = self.canvas.create_rectangle(
            2, 2, 2, 23,
            fill=self._get_color(initial_value),
            outline=""
        )

        # Text
        self.text = self.canvas.create_text(
            0, 12,
            text=f"{initial_value:.1f}%",
            font=("Consolas", 10, "bold"),
            fill="white"
        )

        self.canvas.bind("<Configure>", self._on_resize)

    def _get_color(self, value: float) -> str:
        """Get color based on progress value."""
        if value < 25:
            return "#3B82F6"  # Blue
        elif value < 50:
            return "#10B981"  # Green
        elif value < 75:
            return "#F59E0B"  # Orange
        else:
            return "#8B5CF6"  # Purple

    def _on_resize(self, event):
        """Handle resize."""
        self._update_bar()

    def _update_bar(self):
        """Update the bar display."""
        width = self.canvas.winfo_width()
        fill_width = max(4, (self.current_value / 100) * (width - 4))

        self.canvas.coords(self.bar, 2, 2, fill_width, 23)
        self.canvas.itemconfig(self.bar, fill=self._get_color(self.current_value))
        self.canvas.coords(self.text, width // 2, 12)
        self.canvas.itemconfig(self.text, text=f"{self.current_value:.1f}%")

    def set_value(self, value: float, animate: bool = True):
        """Set the progress value, optionally with animation."""
        self.target_value = min(100, max(0, value))

        if animate:
            self._animate_to_target()
        else:
            self.current_value = self.target_value
            self._update_bar()

    def _animate_to_target(self):
        """Animate to target value."""
        diff = self.target_value - self.current_value

        if abs(diff) < 0.1:
            self.current_value = self.target_value
            self._update_bar()
            return

        # Ease toward target
        self.current_value += diff * 0.1
        self._update_bar()

        self.frame.after(20, self._animate_to_target)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class Toast:
    """Creates toast notification popups."""

    active_toasts = []

    def __init__(self, parent, message: str, toast_type: str = "info",
                 duration: int = 3000):
        self.parent = parent

        # Colors based on type
        colors = {
            "info": ("#3B82F6", "#DBEAFE"),
            "success": ("#10B981", "#D1FAE5"),
            "warning": ("#F59E0B", "#FEF3C7"),
            "error": ("#EF4444", "#FEE2E2"),
            "achievement": ("#8B5CF6", "#EDE9FE"),
        }

        bg_color, _ = colors.get(toast_type, colors["info"])

        # Create toast frame
        self.toast = tk.Frame(
            parent,
            bg=bg_color,
            padx=15,
            pady=10
        )

        # Icon based on type
        icons = {
            "info": "i",
            "success": "v",
            "warning": "!",
            "error": "X",
            "achievement": "*",
        }

        icon_label = tk.Label(
            self.toast,
            text=icons.get(toast_type, "i"),
            font=("Consolas", 14, "bold"),
            bg=bg_color,
            fg="white"
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))

        msg_label = tk.Label(
            self.toast,
            text=message,
            font=("Consolas", 10),
            bg=bg_color,
            fg="white",
            wraplength=250
        )
        msg_label.pack(side=tk.LEFT)

        # Position toast
        Toast.active_toasts.append(self)
        self._update_positions()

        # Show toast
        self.toast.place(relx=1.0, x=-10, y=10 + (len(Toast.active_toasts) - 1) * 60, anchor="ne")

        # Auto-dismiss
        self.parent.after(duration, self._dismiss)

    def _update_positions(self):
        """Update positions of all active toasts."""
        for i, toast in enumerate(Toast.active_toasts):
            if toast.toast.winfo_exists():
                toast.toast.place(relx=1.0, x=-10, y=10 + i * 60, anchor="ne")

    def _dismiss(self):
        """Dismiss the toast."""
        if self in Toast.active_toasts:
            Toast.active_toasts.remove(self)
        try:
            self.toast.destroy()
        except tk.TclError:
            pass
        self._update_positions()


class NumberTicker:
    """Animated number display that ticks up/down to target value."""

    def __init__(self, parent, initial_value: int = 0, prefix: str = "",
                 suffix: str = "", font: tuple = ("Consolas", 12, "bold"),
                 color: str = "black"):
        self.label = ttk.Label(
            parent,
            text=f"{prefix}{initial_value:,}{suffix}",
            font=font,
            foreground=color
        )

        self.current_value = initial_value
        self.target_value = initial_value
        self.prefix = prefix
        self.suffix = suffix
        self.animating = False

    def set_value(self, value: int, animate: bool = True):
        """Set the value, optionally with animation."""
        self.target_value = value

        if animate and not self.animating:
            self.animating = True
            self._animate()
        elif not animate:
            self.current_value = value
            self._update_display()

    def _animate(self):
        """Animate to target value."""
        diff = self.target_value - self.current_value

        if diff == 0:
            self.animating = False
            return

        # Calculate step size
        step = max(1, abs(diff) // 10)
        if diff > 0:
            self.current_value = min(self.current_value + step, self.target_value)
        else:
            self.current_value = max(self.current_value - step, self.target_value)

        self._update_display()

        if self.current_value != self.target_value:
            self.label.after(30, self._animate)
        else:
            self.animating = False

    def _update_display(self):
        """Update the label display."""
        self.label.config(text=f"{self.prefix}{self.current_value:,}{self.suffix}")

    def pack(self, **kwargs):
        self.label.pack(**kwargs)

    def grid(self, **kwargs):
        self.label.grid(**kwargs)

    def config(self, **kwargs):
        self.label.config(**kwargs)


class GlowButton(tk.Button):
    """A button with hover glow effect."""

    def __init__(self, parent, text: str, command=None,
                 bg: str = "#3B82F6", hover_bg: str = "#2563EB",
                 fg: str = "white", **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            relief=tk.FLAT,
            font=("Consolas", 10, "bold"),
            cursor="hand2",
            **kwargs
        )

        self.default_bg = bg
        self.hover_bg = hover_bg

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.configure(bg=self.hover_bg)

    def _on_leave(self, event):
        self.configure(bg=self.default_bg)


def create_gradient_frame(parent, width: int, height: int,
                          color1: str = "#1F2937", color2: str = "#374151"):
    """Create a frame with a gradient background."""
    canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0)

    # Parse colors
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)

    # Draw gradient lines
    for i in range(height):
        ratio = i / height
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)

    return canvas
