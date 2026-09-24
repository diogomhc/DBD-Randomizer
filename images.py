"""Thin Pillow helpers for loading and resizing images for Tkinter widgets.

Kept separate so the resizing/rarity-background logic isn't tangled up
inside the widget-building code in ui.py.
"""

from PIL import Image, ImageTk

RARITY_BACKGROUNDS = {
    "Visceral": "./Rarity_Backgrounds/Item+Addon_Visceral.png",
    "Very Rare": "./Rarity_Backgrounds/Item+Addon_VeryRare.png",
    "Rare": "./Rarity_Backgrounds/Item+Addon_Rare.png",
    "Uncommon": "./Rarity_Backgrounds/Item+Addon_Uncommon.png",
    "Common": "./Rarity_Backgrounds/Item+Addon_Common.png",
}


def load_image(path: str, size: tuple | None = None) -> ImageTk.PhotoImage:
    """Open an image file and optionally resize it, returning a Tk-usable photo."""
    img = Image.open(path)
    if size is not None:
        img = img.resize(size, Image.NEAREST)
    return ImageTk.PhotoImage(img)


def load_rarity_background(rarity: str, size: tuple) -> ImageTk.PhotoImage:
    """Load the background image for a given add-on/perk rarity tier."""
    path = RARITY_BACKGROUNDS.get(rarity)
    if path is None:
        raise KeyError(f"Unknown rarity: {rarity!r}")
    return load_image(path, size)
