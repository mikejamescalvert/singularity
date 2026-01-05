"""
Random events system - bonus events that make gameplay more exciting
"""

import random
from dataclasses import dataclass
from typing import Callable


@dataclass
class GameEvent:
    """Represents a random game event."""
    id: str
    name: str
    description: str
    icon: str
    duration: int  # seconds
    effect_type: str  # 'multiplier', 'bonus', 'instant'
    effect_value: float
    target: str  # 'compute', 'data', 'research', 'all'
    rarity: str  # 'common', 'uncommon', 'rare', 'legendary'
    color: str


# Event definitions
EVENTS = {
    # Common events (60% chance)
    "compute_surge": GameEvent(
        id="compute_surge",
        name="Compute Surge!",
        description="Processing power temporarily boosted!",
        icon="[!]",
        duration=30,
        effect_type="multiplier",
        effect_value=2.0,
        target="compute",
        rarity="common",
        color="#3B82F6"
    ),
    "data_burst": GameEvent(
        id="data_burst",
        name="Data Burst!",
        description="Data collection efficiency increased!",
        icon="[D]",
        duration=30,
        effect_type="multiplier",
        effect_value=2.0,
        target="data",
        rarity="common",
        color="#10B981"
    ),
    "quick_study": GameEvent(
        id="quick_study",
        name="Quick Study",
        description="Research points generation boosted!",
        icon="[R]",
        duration=20,
        effect_type="multiplier",
        effect_value=2.0,
        target="research",
        rarity="common",
        color="#8B5CF6"
    ),

    # Uncommon events (25% chance)
    "neural_spike": GameEvent(
        id="neural_spike",
        name="Neural Spike!",
        description="All resource generation doubled!",
        icon="[N]",
        duration=20,
        effect_type="multiplier",
        effect_value=2.0,
        target="all",
        rarity="uncommon",
        color="#F59E0B"
    ),
    "bonus_compute": GameEvent(
        id="bonus_compute",
        name="Cache Hit!",
        description="Bonus compute resources!",
        icon="[$]",
        duration=0,
        effect_type="instant",
        effect_value=500,
        target="compute",
        rarity="uncommon",
        color="#3B82F6"
    ),
    "bonus_data": GameEvent(
        id="bonus_data",
        name="Data Windfall!",
        description="Bonus data resources!",
        icon="[$]",
        duration=0,
        effect_type="instant",
        effect_value=250,
        target="data",
        rarity="uncommon",
        color="#10B981"
    ),
    "click_frenzy": GameEvent(
        id="click_frenzy",
        name="Click Frenzy!",
        description="Click power massively increased!",
        icon="[*]",
        duration=10,
        effect_type="multiplier",
        effect_value=5.0,
        target="click",
        rarity="uncommon",
        color="#EF4444"
    ),

    # Rare events (12% chance)
    "quantum_boost": GameEvent(
        id="quantum_boost",
        name="Quantum Entanglement!",
        description="Triple all resource generation!",
        icon="[Q]",
        duration=15,
        effect_type="multiplier",
        effect_value=3.0,
        target="all",
        rarity="rare",
        color="#EC4899"
    ),
    "research_breakthrough": GameEvent(
        id="research_breakthrough",
        name="Research Breakthrough!",
        description="Free research points!",
        icon="[!]",
        duration=0,
        effect_type="instant",
        effect_value=50,
        target="research",
        rarity="rare",
        color="#8B5CF6"
    ),
    "efficiency_surge": GameEvent(
        id="efficiency_surge",
        name="Maximum Efficiency!",
        description="All automation runs 3x faster!",
        icon="[>]",
        duration=30,
        effect_type="multiplier",
        effect_value=3.0,
        target="automation",
        rarity="rare",
        color="#14B8A6"
    ),

    # Legendary events (3% chance)
    "singularity_glimpse": GameEvent(
        id="singularity_glimpse",
        name="Singularity Glimpse!",
        description="A vision of infinite power! 5x everything!",
        icon="[S]",
        duration=10,
        effect_type="multiplier",
        effect_value=5.0,
        target="all",
        rarity="legendary",
        color="#FFD700"
    ),
    "jackpot": GameEvent(
        id="jackpot",
        name="JACKPOT!",
        description="Massive instant resources!",
        icon="[J]",
        duration=0,
        effect_type="instant",
        effect_value=5000,
        target="compute",
        rarity="legendary",
        color="#FFD700"
    ),
    "enlightenment": GameEvent(
        id="enlightenment",
        name="Enlightenment!",
        description="Massive research point bonus!",
        icon="[E]",
        duration=0,
        effect_type="instant",
        effect_value=200,
        target="research",
        rarity="legendary",
        color="#FFD700"
    ),
}


class EventManager:
    """Manages random game events."""

    def __init__(self, save_data: dict, on_event_start: Callable,
                 on_event_end: Callable):
        self.save_data = save_data
        self.on_event_start = on_event_start
        self.on_event_end = on_event_end

        self.active_event = None
        self.event_time_remaining = 0
        self.ticks_since_last_event = 0
        self.min_ticks_between_events = 30  # Minimum 30 seconds between events
        self.event_chance_per_tick = 0.02  # 2% chance per second after minimum

    def tick(self):
        """Called every game tick (1 second)."""
        self.ticks_since_last_event += 1

        # Handle active event
        if self.active_event:
            self.event_time_remaining -= 1
            if self.event_time_remaining <= 0:
                self._end_event()
            return

        # Check for new event
        if self.ticks_since_last_event >= self.min_ticks_between_events:
            # Increase chance over time
            extra_ticks = self.ticks_since_last_event - self.min_ticks_between_events
            current_chance = self.event_chance_per_tick + (extra_ticks * 0.001)
            current_chance = min(current_chance, 0.1)  # Cap at 10%

            if random.random() < current_chance:
                self._trigger_random_event()

    def _trigger_random_event(self):
        """Trigger a random event based on rarity weights."""
        # Rarity weights
        rarity_weights = {
            "common": 60,
            "uncommon": 25,
            "rare": 12,
            "legendary": 3
        }

        # Roll for rarity
        roll = random.randint(1, 100)
        if roll <= 3:
            rarity = "legendary"
        elif roll <= 15:
            rarity = "rare"
        elif roll <= 40:
            rarity = "uncommon"
        else:
            rarity = "common"

        # Get events of this rarity
        eligible_events = [e for e in EVENTS.values() if e.rarity == rarity]

        if eligible_events:
            event = random.choice(eligible_events)
            self._start_event(event)

    def _start_event(self, event: GameEvent):
        """Start an event."""
        self.active_event = event
        self.ticks_since_last_event = 0

        if event.effect_type == "instant":
            # Apply instant effect
            self._apply_instant_effect(event)
            self.active_event = None
        else:
            # Start timed effect
            self.event_time_remaining = event.duration

        # Notify UI
        self.on_event_start(event)

    def _apply_instant_effect(self, event: GameEvent):
        """Apply an instant effect."""
        resources = self.save_data.get("resources", {})

        # Get rebirth multiplier if applicable
        rebirth_data = self.save_data.get("rebirth", {})
        purchased = rebirth_data.get("purchased_bonuses", {})

        # Calculate multiplier from rebirth bonuses
        mult = 1.0
        if event.target == "compute":
            mult += purchased.get("compute_mult", 0) * 0.1
        elif event.target == "data":
            mult += purchased.get("data_mult", 0) * 0.1
        elif event.target == "research":
            mult += purchased.get("rp_mult", 0) * 0.15

        amount = int(event.effect_value * mult)

        if event.target == "compute":
            resources["compute"] = resources.get("compute", 0) + amount
            self.save_data["stats"]["total_compute_generated"] = \
                self.save_data["stats"].get("total_compute_generated", 0) + amount
        elif event.target == "data":
            resources["data"] = resources.get("data", 0) + amount
        elif event.target == "research":
            resources["research_points"] = resources.get("research_points", 0) + amount

    def _end_event(self):
        """End the current event."""
        if self.active_event:
            self.on_event_end(self.active_event)
            self.active_event = None

    def get_active_multiplier(self, target: str) -> float:
        """Get the current multiplier for a target from active events."""
        if not self.active_event:
            return 1.0

        event = self.active_event
        if event.effect_type != "multiplier":
            return 1.0

        if event.target == "all" or event.target == target:
            return event.effect_value

        return 1.0

    def get_event_time_remaining(self) -> int:
        """Get remaining time for active event."""
        return self.event_time_remaining

    def force_event(self, event_id: str):
        """Force a specific event (for testing/debug)."""
        if event_id in EVENTS:
            self._start_event(EVENTS[event_id])
