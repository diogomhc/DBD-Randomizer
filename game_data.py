"""Loading and access to the static game data (killers.json, perks.json).

This module has no Tkinter or randomization logic in it, so it can be
imported and tested without a display.
"""

import json


def load_json(path: str) -> dict:
    """Load a JSON object file, converting its top-level string keys to ints."""
    with open(path, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


class GameData:
    """Read-only view of the killers and perks defined in the JSON files.

    killers_by_key: {0: {"name": ..., "portrait": ..., "power": ...,
                          "addons": [{"name": ..., "rarity": ..., "img": ...}]}, ...}
    perks_by_key:   {0: {"name": ..., "killer": ..., "image": ...}, ...}
    """

    def __init__(self, killers_file: str = "killers.json", perks_file: str = "perks.json"):
        self.killers_by_key = load_json(killers_file)
        self.perks_by_key = load_json(perks_file)

        self.killers = [self.killers_by_key[k]["name"] for k in self.killers_by_key]
        self.killer_addons = {
            k: self.killers_by_key[k].get("addons", []) for k in self.killers_by_key
        }

    def killer_name(self, killer_index: int) -> str:
        return self.killers_by_key[killer_index]["name"]

    def perk_name(self, perk_index: int) -> str:
        return self.perks_by_key[perk_index]["name"]

    def perk_index_by_name(self, perk_name: str):
        for key, data in self.perks_by_key.items():
            if data["name"] == perk_name:
                return key
        return None
