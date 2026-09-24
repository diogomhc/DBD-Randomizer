"""Randomization and active/inactive state, kept separate from the UI.

Nothing in this module touches Tkinter or Pillow, so it can be unit
tested with plain `assert` statements or pytest without a display.
"""

import json
from random import randint, sample

from game_data import GameData

DEFAULT_STATE_FILE = "randomizer_state.json"


class RandomizerState:
    """Tracks which killers/perks are enabled and picks random builds.

    The active/inactive sets are persisted to `state_file` as JSON and
    reloaded automatically on the next run. Every method that changes
    the active sets saves immediately afterward, so no explicit "save"
    call is needed elsewhere and nothing is lost on a crash or a hard
    close of the window.
    """

    def __init__(self, data: GameData, state_file: str = DEFAULT_STATE_FILE):
        self.data = data
        self.state_file = state_file
        self.active_killers, self.active_perks, self.active_addons = self._load_state()

    def _default_active_killers(self):
        return list(self.data.killers)

    def _default_active_perks(self):
        return [self.data.perks_by_key[k]["name"] for k in self.data.perks_by_key]

    def _default_active_addons(self):
        """{killer_index: [addon_name, ...]} - every add-on active by default."""
        return {
            killer_index: [addon["name"] for addon in addons]
            for killer_index, addons in self.data.killer_addons.items()
        }

    def _load_state(self):
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return (
                self._default_active_killers(),
                self._default_active_perks(),
                self._default_active_addons(),
            )

        active_killers = state.get("active_killers", self._default_active_killers())
        active_perks = state.get("active_perks", self._default_active_perks())

        raw_addons = state.get("active_addons")
        if raw_addons is None:
            active_addons = self._default_active_addons()
        else:
            # JSON object keys are always strings - convert back to the int
            # killer indices used everywhere else.
            active_addons = {int(k): v for k, v in raw_addons.items()}
            # A killer added to killers.json after this state file was last
            # saved won't have an entry yet - default it to "all active"
            # instead of silently having zero add-ons available.
            for killer_index in self.data.killer_addons:
                if killer_index not in active_addons:
                    active_addons[killer_index] = [
                        addon["name"] for addon in self.data.killer_addons[killer_index]
                    ]

        return active_killers, active_perks, active_addons

    def save_state(self) -> None:
        state = {
            "active_killers": self.active_killers,
            "active_perks": self.active_perks,
            "active_addons": {str(k): v for k, v in self.active_addons.items()},
        }
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def is_killer_active(self, key: int) -> bool:
        return self.data.killers[key] in self.active_killers

    def toggle_killer(self, key: int) -> None:
        killer = self.data.killers[key]
        if killer in self.active_killers:
            self.active_killers.remove(killer)
        else:
            self.active_killers.insert(key, killer)
        self.save_state()

    def bulk_toggle_killers(self, activate: bool) -> None:
        for key, name in enumerate(self.data.killers):
            is_active = name in self.active_killers
            if activate and not is_active:
                self.active_killers.insert(self.data.killers.index(name), name)
            elif not activate and is_active:
                self.active_killers.remove(name)
        self.save_state()

    def is_perk_active(self, key: int) -> bool:
        return self.data.perks_by_key[key]["name"] in self.active_perks

    def toggle_perk(self, key: int) -> None:
        perk_name = self.data.perks_by_key[key]["name"]
        if perk_name in self.active_perks:
            self.active_perks.remove(perk_name)
        else:
            self.active_perks.insert(key, perk_name)
        self.save_state()

    def bulk_toggle_perks(self, activate: bool) -> None:
        for key, pdata in self.data.perks_by_key.items():
            name = pdata["name"]
            is_active = name in self.active_perks
            if activate and not is_active:
                self.active_perks.insert(key, name)
            elif not activate and is_active:
                self.active_perks.remove(name)
        self.save_state()

    def deactivate_related_perks(self) -> None:
        """Turn off perks belonging to any currently-deactivated killer."""
        deactivated_killers = [k for k in self.data.killers if k not in self.active_killers]
        for pdata in self.data.perks_by_key.values():
            perk_name, killer_name = pdata["name"], pdata["killer"]
            if killer_name in deactivated_killers and perk_name in self.active_perks:
                self.active_perks.remove(perk_name)
        self.save_state()

    def activate_related_perks(self) -> None:
        """Turn on perks belonging to any currently-activated killer."""
        for key, pdata in self.data.perks_by_key.items():
            perk_name, killer_name = pdata["name"], pdata["killer"]
            if killer_name in self.active_killers and perk_name not in self.active_perks:
                self.active_perks.insert(key, perk_name)
        self.save_state()

    def is_addon_active(self, killer_index: int, addon_index: int) -> bool:
        addon_name = self.data.killer_addons[killer_index][addon_index]["name"]
        return addon_name in self.active_addons.get(killer_index, [])

    def toggle_addon(self, killer_index: int, addon_index: int) -> None:
        addon_name = self.data.killer_addons[killer_index][addon_index]["name"]
        active_list = self.active_addons.setdefault(killer_index, [])
        if addon_name in active_list:
            active_list.remove(addon_name)
        else:
            active_list.insert(addon_index, addon_name)
        self.save_state()

    def bulk_toggle_addons(self, killer_index: int, activate: bool) -> None:
        addons = self.data.killer_addons.get(killer_index, [])
        self.active_addons[killer_index] = (
            [addon["name"] for addon in addons] if activate else []
        )
        self.save_state()

    def active_addon_indices(self, killer_index: int):
        """Indices (into that killer's add-on list) of currently-active add-ons."""
        addons = self.data.killer_addons.get(killer_index, [])
        active_names = self.active_addons.get(killer_index, [])
        return [i for i, addon in enumerate(addons) if addon["name"] in active_names]

    def random_killer(self):
        """Return a random active killer's index, or None if none are active."""
        if not self.active_killers:
            return None
        killer_name = self.active_killers[randint(0, len(self.active_killers) - 1)]
        return self.data.killers.index(killer_name)

    def random_addons(self, killer_index: int):
        """Return two distinct random active add-on indices for a killer, or
        (None, None) if that killer has fewer than two active add-ons."""
        active_indices = self.active_addon_indices(killer_index)
        if len(active_indices) < 2:
            return None, None
        i1, i2 = sample(active_indices, 2)
        return i1, i2

    def random_perks(self, count: int = 4):
        """Return up to `count` distinct random active perk names.

        Uses sampling without replacement, so the same perk never appears
        twice in one result (fixes the duplicate-perk bug in the original
        script). Returns fewer than `count` names if fewer are active.
        """
        if not self.active_perks:
            return []
        n = min(count, len(self.active_perks))
        return sample(self.active_perks, n)
