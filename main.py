"""Entry point. Run from the project folder: python main.py"""

import tkinter as tk

from game_data import GameData
from randomizer import RandomizerState
from ui import RandomizerApp

KILLERS_FILE = "killers.json"
PERKS_FILE = "perks.json"
STATE_FILE = "randomizer_state.json"


def main():
    root = tk.Tk()
    root.title("DBD Randomizer")

    data = GameData(KILLERS_FILE, PERKS_FILE)
    state = RandomizerState(data, STATE_FILE)
    app = RandomizerApp(root, data, state)
    app.run()


if __name__ == "__main__":
    main()
