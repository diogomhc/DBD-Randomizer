# DBD Randomizer

A desktop app that generates random **Killer builds** (Survivor coming soon) for *Dead by Daylight*. One click gives you a random Killer, two add-ons, and four perks, so you never have to decide what to play again.

Built with Python, Tkinter, and Pillow.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4a9db9b6-e6e6-4b91-ac69-71f7b83de144" />

## Features

- **Randomize Build**: picks a Killer, two add-ons, and four perks in one click
- **Randomize Killer**: picks a random Killer and shows their portrait, name, and power, plus two distinct add-ons displayed on their rarity-colored backgrounds (Common, Uncommon, Rare, Very Rare, Visceral)
- **Randomize Perks**: rolls a fresh set of four distinct killer perks
- **Manage Killers**: full-screen grid of every Killer portrait. Click one to enable (green border) or disable (red border) it, so the randomizer only picks from Killers you own or want to play. Includes **Enable All** and **Disable All**
- **Manage Perks**: scrollable grid of every killer perk with the same enable/disable toggling, plus:
  - **Deactivate Perks of Deactivated Killers**
  - **Activate Perks of Active Killers**
- **Manage Addons**: click a Killer's portrait to open a scrollable grid of that Killer's add-ons, and enable/disable them individually the same way as Killers and Perks. Includes **Enable All** and **Disable All** per Killer

Rolls never repeat the same perk or add-on within a single result, and only pull from what's currently enabled.

## Requirements

- Python 3.8 or newer
- [Pillow](https://pypi.org/project/pillow/)
- Tkinter (bundled with most Python installers; on Debian/Ubuntu install it with `sudo apt install python3-tk`)

## Installation

```bash
git clone https://github.com/diogomhc/DBD-Randomizer.git
cd DBD-Randomizer
pip install -r requirements.txt
```

## Usage

Run the app from the project folder, since image paths are relative:

```bash
python main.py
```

The app opens full screen.

| Button | Action |
| --- | --- |
| Randomize Build | Rolls a Killer, add-ons, and perks |
| Randomize Killer | Rolls only the Killer and add-ons |
| Randomize Perks | Rolls only the four perks |
| Manage Killers | Opens the Killer enable/disable grid |
| Manage Perks | Opens the perk enable/disable grid |
| Manage Addons | Opens a Killer picker; selecting a Killer opens their add-on enable/disable grid |
| Close | Exits the app |

Press **Esc** in the main window to quit, in a management screen to go back, or in a Killer's add-on grid to return to the Killer picker.

> Enabled/disabled selections — Killers, Perks, and now Add-ons — are saved to file automatically as you toggle them, so they persist when you restart the app.

If fewer than 4 perks are active, Randomize Perks/Build shows a message instead of rolling. Same for a Killer with fewer than 2 active add-ons — whether that's because few are defined or because you've disabled most of them in Manage Addons.

## Project structure

```
DBD-Randomizer/
├── main.py               # Entry point - run this
├── game_data.py           # Loads killers.json / perks.json (no UI, no randomization)
├── randomizer.py          # RandomizerState - active/inactive tracking, randomization, save/load (no UI)
├── images.py               # Pillow helpers for loading/resizing images
├── ui.py                  # All Tkinter windows and widgets
├── test_randomizer.py     # Unit tests for randomizer.py (pytest, no display needed)
├── killers.json           # Killer data (name, portrait, power, add-ons)
├── perks.json              # Perk data (name, owning killer, image)
├── randomizer_state.json  # Active Killers/Perks/Add-ons selections (auto-generated on first run)
├── requirements.txt
├── CharPortraits/          # Killer portraits
├── Powers/                 # Killer power icons
├── ItemAddons/              # Add-on icons
├── Perks/                   # Perk icons
└── Rarity_Backgrounds/      # Rarity backgrounds for add-ons and perks
```

`randomizer_state.json` is created automatically the first time you toggle a Killer, Perk, or Add-on — you don't need to create it yourself, and it's already excluded via `.gitignore` since it's per-user state rather than project data.

### Running the tests

```bash
pip install pytest
pytest test_randomizer.py -v
```

The tests cover `randomizer.py` only (no Tkinter/Pillow involved), so they run in well under a second with no display required.

## Data format

Both JSON files use numeric string keys.

**`killers.json`**

```json
{
  "0": {
    "name": "Killer Name",
    "portrait": "CharPortraits/killer.png",
    "power": "Powers/power.png",
    "addons": [
      { "name": "Add-on Name", "rarity": "Rare", "img": "ItemAddons/addon.png" }
    ]
  }
}
```

Valid `rarity` values: `Common`, `Uncommon`, `Rare`, `Very Rare`, `Visceral`. The `"addons"` field is optional — Killers without it simply won't roll add-ons yet, and their entry in Manage Addons will say so instead of showing an empty grid.

**`perks.json`**

```json
{
  "0": {
    "name": "Perk Name",
    "killer": "Killer Name",
    "image": "Perks/perk.png"
  }
}
```

The `killer` field links a perk to its Killer, which powers the "related perks" buttons in the perk manager.

### `randomizer_state.json`

```json
{
  "active_killers": ["Killer Name", "..."],
  "active_perks": ["Perk Name", "..."],
  "active_addons": {
    "0": ["Add-on Name", "..."]
  }
}
```

`active_addons` is keyed by killer index (as a string, since that's how JSON objects work) and lists that killer's currently-active add-on names. If a killer is missing from this map — for example because they were added to `killers.json` after this file was last saved — all of their add-ons default to active rather than none.

## Disclaimer

This is an unofficial fan project and is not affiliated with or endorsed by Behaviour Interactive. *Dead by Daylight* and all related names, images, and assets are trademarks or property of Behaviour Interactive Inc.
