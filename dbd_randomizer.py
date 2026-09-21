import json
from random import randint
import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.title("DBD Randomizer")

POWER_IMAGE_SIZE = (120, 120)
PERK_IMAGE_SIZE = (100, 100)

KILLERS_FILE = "killers.json"
PERKS_FILE = "perks.json"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return {int(k): v for k, v in json.load(f).items()}


killers_by_key = load_json(KILLERS_FILE)   # {0: {"name": ..., "portrait": ..., "power": ..., "addons": [{"name": ..., "rarity": ..., "img": ...}]}, ...}
perks_by_key = load_json(PERKS_FILE)       # {0: {"name": ..., "killer": ..., "image": ...}, ...}

killers = [killers_by_key[k]["name"] for k in killers_by_key]
killer_addons = {k: killers_by_key[k].get("addons", []) for k in killers_by_key}
killer_addons_mutable = [killers_by_key[k]["addons"] for k in killers_by_key]

addon_bg_images = {
    "Visceral": "./Rarity_Backgrounds/Item+Addon_Visceral.png",
    "Very Rare": "./Rarity_Backgrounds/Item+Addon_VeryRare.png",
    "Rare": "./Rarity_Backgrounds/Item+Addon_Rare.png",
    "Uncommon": "./Rarity_Backgrounds/Item+Addon_Uncommon.png",
    "Common": "./Rarity_Backgrounds/Item+Addon_Common.png"
}

image_label = None
text_label = "No Killer Picked"
current_photo = None
current_power = None
current_addon1 = None
current_bg_addon1 = None
current_bg_addon2 = None
current_addon2 = None
current_perks = []
current_perks_photos = []
root.killer_menu_win = None
root.killer_perk_menu_win = None

power_canvas = None
power_image_on_canvas = None
power_bg_photo = None
addon1_canvas = None
addon2_canvas = None
addon1_on_canvas = None
addon2_on_canvas = None
addon1_text_label = None
addon2_text_label = None
addon1_bg_on_canvas = None
addon2_bg_on_canvas = None

perk1_canvas = None
perk2_canvas = None
perk3_canvas = None
perk4_canvas = None
perk1_on_canvas = None
perk2_on_canvas = None
perk3_on_canvas = None
perk4_on_canvas = None
perk1_text_label = None
perk2_text_label = None
perk3_text_label = None
perk4_text_label = None
perk_bg_photo = None

STATE_FILE = "randomizer_state.json"

def killer_perks_mutable_default():
    return [perks_by_key[k]["name"] for k in perks_by_key]


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("active_killers", killers.copy()), state.get("active_perks", killer_perks_mutable_default())
    except (FileNotFoundError, json.JSONDecodeError):
        return killers.copy(), [perks_by_key[k]["name"] for k in perks_by_key]

killers_mutable, killer_perks_mutable = load_state()

def save_state():
    state = {
        "active_killers": killers_mutable,
        "active_perks": killer_perks_mutable
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def randomize_all():
    randomize_killer()
    randomize_perks()

def randomize_killer():
    global current_photo, current_power, current_addon1, current_addon2, current_bg_addon1, current_bg_addon2

    if not killers_mutable:
        text_label.config(text="No active killers")
        image_label.config(image="")
        power_canvas.itemconfig(power_image_on_canvas, image="")
        return

    killer_name = killers_mutable[randint(0, len(killers_mutable) - 1)]
    killer_index = killers.index(killer_name)

    addon1_index, addon2_index = randomize_addons(killer_index)
    current_addon1 = get_addon_image(killer_index, addon1_index)
    current_bg_addon1 = get_bg_addon_image(killer_index, addon1_index)
    addon1_canvas.itemconfig(addon1_bg_on_canvas, image=current_bg_addon1)
    addon1_canvas.itemconfig(addon1_on_canvas, image=current_addon1)
    current_addon2 = get_addon_image(killer_index, addon2_index)
    current_bg_addon2 = get_bg_addon_image(killer_index, addon2_index)
    addon2_canvas.itemconfig(addon2_bg_on_canvas, image=current_bg_addon2)
    addon2_canvas.itemconfig(addon2_on_canvas, image=current_addon2)

    addon1_name = killer_addons.get(killer_index)[addon1_index]["name"]
    addon2_name = killer_addons.get(killer_index)[addon2_index]["name"]
    addon1_text_label.config(text=addon1_name)
    addon2_text_label.config(text=addon2_name)

    current_photo = get_portrait(killer_index)
    current_power = get_power_image(killer_index)
    power_canvas.itemconfig(power_image_on_canvas, image=current_power)
    image_label.config(image=current_photo)
    text_label.config(text=killer_name)

def get_bg_addon_image(killer_index, addon_index) -> ImageTk.PhotoImage:
    rarity = killer_addons.get(killer_index)[addon_index]["rarity"]
    path = addon_bg_images.get(rarity)
    img = Image.open(path)
    img = img.resize(PERK_IMAGE_SIZE, Image.NEAREST)
    return ImageTk.PhotoImage(img)
    
def get_addon_image(killer_index, addon_index) -> ImageTk.PhotoImage:
    img = Image.open(killer_addons.get(killer_index)[addon_index]["img"])
    img = img.resize(PERK_IMAGE_SIZE, Image.NEAREST)
    return ImageTk.PhotoImage(img)

def randomize_addons(killer_index) -> dict:
    addons = killer_addons.get(killer_index, [])
    if len(addons) < 2:
        return None, None
    indices = list(range(len(addons)))
    i1 = indices.pop(randint(0, len(indices) - 1))
    i2 = indices.pop(randint(0, len(indices) - 1))
    return i1, i2


def randomize_perks():
    global current_perks, current_perks_photos
    current_perks_photos.clear()
    current_perks.clear()

    perk_canvases = [perk1_canvas, perk2_canvas, perk3_canvas, perk4_canvas]
    perk_canvas_items = [perk1_on_canvas, perk2_on_canvas, perk3_on_canvas, perk4_on_canvas]
    perk_text_labels = [perk1_text_label, perk2_text_label, perk3_text_label, perk4_text_label]

    if len(killer_perks_mutable) < 4:
        text_label.config(text="Not enough active perks")
        for canvas, item in zip(perk_canvases, perk_canvas_items):
            canvas.itemconfig(item, image="")
        for label in perk_text_labels:
            label.config(text="")
        return

    indices = list(range(len(killer_perks_mutable)))
    chosen_indices = []
    for _ in range(4):
        chosen_indices.append(indices.pop(randint(0, len(indices) - 1)))

    for i in chosen_indices:
        perk_name = killer_perks_mutable[i]
        perk_index = get_perk_index(perk_name)
        current_perks_photos.append(get_perk_image(perk_index))
        current_perks.append(perk_name)

    for canvas, item, photo, label, name in zip(
        perk_canvases, perk_canvas_items, current_perks_photos, perk_text_labels, current_perks
    ):
        canvas.itemconfig(item, image=photo)
        label.config(text=name)


def get_perk_image(perk_index) -> ImageTk.PhotoImage:
    img = Image.open(perks_by_key[perk_index]["image"])
    img = img.resize(PERK_IMAGE_SIZE, Image.NEAREST)
    return ImageTk.PhotoImage(img)


def get_perk_index(perk_name):
    for key, data in perks_by_key.items():
        if data["name"] == perk_name:
            return key


def get_portrait(killer_index: int) -> ImageTk.PhotoImage:
    img = Image.open(killers_by_key[killer_index]["portrait"])
    return ImageTk.PhotoImage(img)


def get_power_image(killer_index: int, size=POWER_IMAGE_SIZE) -> ImageTk.PhotoImage:
    img = Image.open(killers_by_key[killer_index]["power"])
    img = img.resize(size, Image.NEAREST)
    return ImageTk.PhotoImage(img)


def toggle_killer(key: int):
    killer = killers[key]
    if killer in killers_mutable:
        killers_mutable.remove(killer)
    else:
        killers_mutable.insert(key, killer)


def toggle_and_refresh(key: int, border_frame):
    toggle_killer(key)
    is_active = killers[key] in killers_mutable
    border_frame.config(bg="#116611" if is_active else "#661111")
    save_state()


def toggle_perk(key: int):
    perk_name = perks_by_key[key]["name"]
    if perk_name in killer_perks_mutable:
        killer_perks_mutable.remove(perk_name)
    else:
        killer_perks_mutable.insert(key, perk_name)


def toggle_and_refresh_perk(key: int, border_frame):
    toggle_perk(key)
    perk_name = perks_by_key[key]["name"]
    is_active = perk_name in killer_perks_mutable
    border_frame.config(bg="#116611" if is_active else "#661111")
    save_state()


def open_killer_menu():
    root.killer_menu_win.deiconify()
    root.killer_menu_win.focus_force()


def prebuild_killer_menu():
    killer_menu_win = tk.Toplevel(root)
    root.killer_menu_win = killer_menu_win
    killer_menu_win.title("Deactivate/Activate Killers")
    killer_menu_win.configure(bg="#333333")
    killer_menu_win.attributes('-fullscreen', True)
    killer_menu_win.withdraw()
    killer_menu_win.bind("<Escape>", lambda e: killer_menu_win.withdraw())
    killer_menu_win.protocol("WM_DELETE_WINDOW", lambda e: killer_menu_win.withdraw())
    killer_menu_win.focus_force()

    build_killer_grid(killer_menu_win)


def build_killer_grid(killer_menu_win):
    killer_menu_win.update_idletasks()

    total = len(killers_by_key)
    pad = 5
    border = 3

    button_bar = tk.Frame(killer_menu_win, bg="#333333")

    back_btn = tk.Button(button_bar, text="Back", command=lambda: killer_menu_win.withdraw(), fg="white", bg="#1e1e1e", font=('Arial', 10))
    back_btn.pack(side="left", padx=10)

    deactivate_all_btn = tk.Button(button_bar, text="Disable All", command=lambda: bulk_toggle(killer_menu_win, activate=False), fg="white", bg="#661111", font=('Arial', 10))
    deactivate_all_btn.pack(side="left", padx=10)

    activate_all_btn = tk.Button(button_bar, text="Enable All", command=lambda: bulk_toggle(killer_menu_win, activate=True), fg="white", bg="#116611", font=('Arial', 10))
    activate_all_btn.pack(side="left", padx=10)

    killer_menu_win.update_idletasks()
    bar_height = button_bar.winfo_reqheight() + 25

    win_w = killer_menu_win.winfo_screenwidth()
    win_h = killer_menu_win.winfo_screenheight() - bar_height

    best_size = 0
    best_cols = 1
    for cols in range(1, total + 1):
        rows = -(-total // cols)
        cell_w = win_w // cols - (2 * pad) - (2 * border)
        cell_h = win_h // rows - (2 * pad) - (2 * border)
        size = min(cell_w, cell_h)
        if size > best_size:
            best_size = size
            best_cols = cols

    thumb_size = (best_size, best_size)
    columns = best_cols

    button_bar.grid(row=0, column=0, columnspan=columns, pady=10)

    killer_menu_win.border_frames = {}
    killer_menu_win.thumb_images = []

    for index, key in enumerate(sorted(killers_by_key)):
        path = killers_by_key[key]["portrait"]
        img = Image.open(path)
        img = img.resize(thumb_size, Image.NEAREST)
        photo = ImageTk.PhotoImage(img)
        killer_menu_win.thumb_images.append(photo)

        is_active = killers[key] in killers_mutable

        border_frame = tk.Frame(killer_menu_win, bg="#116611" if is_active else "#661111")
        row = (index // columns) + 1
        col = index % columns
        border_frame.grid(row=row, column=col, padx=pad, pady=pad)
        killer_menu_win.border_frames[key] = border_frame

        btn = tk.Button(border_frame, image=photo, command=lambda k=key, f=border_frame: toggle_and_refresh(k, f), relief="flat", bg="#1e1e1e", borderwidth=0)
        btn.pack(padx=border, pady=border)


def bulk_toggle(killer_menu_win, activate: bool):
    for key, name in enumerate(killers):
        is_active = name in killers_mutable
        if activate and not is_active:
            killers_mutable.insert(killers.index(name), name)
        elif not activate and is_active:
            killers_mutable.remove(name)

    new_color = "#116611" if activate else "#661111"
    for border_frame in killer_menu_win.border_frames.values():
        border_frame.config(bg=new_color)
    save_state()


def bulk_toggle_perks(killer_perk_menu_win, activate: bool):
    for key, data in perks_by_key.items():
        name = data["name"]
        is_active = name in killer_perks_mutable
        if activate and not is_active:
            killer_perks_mutable.insert(key, name)
        elif not activate and is_active:
            killer_perks_mutable.remove(name)

    new_color = "#116611" if activate else "#661111"
    for border_frame in killer_perk_menu_win.border_frames.values():
        border_frame.config(bg=new_color)
    save_state()


def prebuild_killer_perk_menu():
    killer_perk_menu_win = tk.Toplevel(root)
    root.killer_perk_menu_win = killer_perk_menu_win
    killer_perk_menu_win.title("Deactivate/Activate Killer Perks")
    killer_perk_menu_win.configure(bg="#333333")
    killer_perk_menu_win.attributes('-fullscreen', True)
    killer_perk_menu_win.withdraw()
    killer_perk_menu_win.bind("<Escape>", lambda e: killer_perk_menu_win.withdraw())
    killer_perk_menu_win.protocol("WM_DELETE_WINDOW", lambda e: killer_perk_menu_win.withdraw())
    killer_perk_menu_win.focus_force()

    build_killer_perk_grid(killer_perk_menu_win)


def open_killer_perk_menu():
    root.killer_perk_menu_win.deiconify()
    root.killer_perk_menu_win.focus_force()


def deactivate_related_killer_perks(killer_perk_menu_win):
    deactivated_killers = [k for k in killers if k not in killers_mutable]

    for key, data in perks_by_key.items():
        perk_name, killer_name = data["name"], data["killer"]
        if killer_name in deactivated_killers and perk_name in killer_perks_mutable:
            killer_perks_mutable.remove(perk_name)
            killer_perk_menu_win.border_frames[key].config(bg="#661111")
    save_state()


def activate_related_killer_perks(killer_perk_menu_win):
    for key, data in perks_by_key.items():
        perk_name, killer_name = data["name"], data["killer"]
        if killer_name in killers_mutable and perk_name not in killer_perks_mutable:
            killer_perks_mutable.insert(key, perk_name)
            killer_perk_menu_win.border_frames[key].config(bg="#116611")
    save_state()


def build_killer_perk_grid(killer_perk_menu_win):
    killer_perk_menu_win.update_idletasks()

    pad = 5
    border = 3
    thumb_px = 120

    button_bar = tk.Frame(killer_perk_menu_win, bg="#333333")
    button_bar.pack(side="top", fill="x", pady=10)

    back_btn = tk.Button(button_bar, text="Back", command=lambda: killer_perk_menu_win.withdraw(), fg="white", bg="#1e1e1e", font=('Arial', 10))
    back_btn.pack(side="left", padx=5)

    deactivate_all_btn = tk.Button(button_bar, text="Disable All", command=lambda: bulk_toggle_perks(killer_perk_menu_win, activate=False), fg="white", bg="#661111", font=('Arial', 10))
    deactivate_all_btn.pack(side="right", padx=5)

    activate_all_btn = tk.Button(button_bar, text="Enable All", command=lambda: bulk_toggle_perks(killer_perk_menu_win, activate=True), fg="white", bg="#116611", font=('Arial', 10))
    activate_all_btn.pack(side="right", padx=5)

    deactivate_related_btn = tk.Button(button_bar, text="Deactivate Perks of Deactivated Killers", command=lambda: deactivate_related_killer_perks(killer_perk_menu_win), fg="white", bg="#1e1e1e", font=('Arial', 10))
    deactivate_related_btn.pack(side="left", padx=5)

    activate_related_btn = tk.Button(button_bar, text="Activate Perks of Active Killers", command=lambda: activate_related_killer_perks(killer_perk_menu_win), fg="white", bg="#1e1e1e", font=('Arial', 10))
    activate_related_btn.pack(side="left", padx=5)

    canvas = tk.Canvas(killer_perk_menu_win, bg="#333333", highlightthickness=0)
    scrollbar = tk.Scrollbar(killer_perk_menu_win, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg="#333333")

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    def unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")

    canvas.bind("<Enter>", bind_mousewheel)
    canvas.bind("<Leave>", unbind_mousewheel)

    win_w = killer_perk_menu_win.winfo_screenwidth()
    columns = max(1, (win_w - scrollbar.winfo_reqwidth()) // (thumb_px + 2 * pad + 2 * border))
    thumb_size = (thumb_px, thumb_px)

    killer_perk_menu_win.border_frames = {}
    killer_perk_menu_win.thumb_images = []

    bg_img = Image.open("./Rarity_Backgrounds/Perk_Tier3.png")
    bg_img = bg_img.resize(thumb_size, Image.NEAREST)
    bg_photo = ImageTk.PhotoImage(bg_img)
    killer_perk_menu_win.thumb_images.append(bg_photo)

    for index, key in enumerate(sorted(perks_by_key)):
        path = perks_by_key[key]["image"]
        img = Image.open(path)
        img = img.resize(thumb_size, Image.NEAREST)
        photo = ImageTk.PhotoImage(img)
        killer_perk_menu_win.thumb_images.append(photo)

        perk_name = perks_by_key[key]["name"]
        is_active = perk_name in killer_perks_mutable

        border_frame = tk.Frame(scroll_frame, bg="#116611" if is_active else "#661111")
        row = index // columns
        col = index % columns
        border_frame.grid(row=row, column=col, padx=pad, pady=pad)
        killer_perk_menu_win.border_frames[key] = border_frame

        cell_canvas = tk.Canvas(border_frame, width=thumb_px, height=thumb_px, bg="#1e1e1e", highlightthickness=0)
        cell_canvas.pack(padx=border, pady=border)

        cell_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
        cell_canvas.create_image(0, 0, image=photo, anchor="nw")

        cell_canvas.bind("<Button-1>", lambda e, k=key, f=border_frame: toggle_and_refresh_perk(k, f))


def main():
    global image_label, text_label
    global power_canvas, power_image_on_canvas, power_bg_photo
    global perk1_canvas, perk2_canvas, perk3_canvas, perk4_canvas
    global perk1_on_canvas, perk2_on_canvas, perk3_on_canvas, perk4_on_canvas
    global perk1_text_label, perk2_text_label, perk3_text_label, perk4_text_label, perk_bg_photo
    global addon1_on_canvas, addon2_on_canvas, addon1_canvas, addon2_canvas, addon1_text_label, addon2_text_label, addon1_bg_on_canvas, addon2_bg_on_canvas

    root.configure(bg="#333333")
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", lambda e: root.destroy())

    images_frame = tk.Frame(root, bg="#333333")
    images_frame.pack(pady=20)

    image_label = tk.Label(images_frame, bg="#333333")
    image_label.grid(row=0, column=0, rowspan=3, columnspan=2, pady=10)

    text_label = tk.Label(images_frame, text=text_label, font=("Arial", 20), fg="white", bg="#333333")
    text_label.grid(row=0, column=3, padx=10)

    power_bg_img = Image.open("./Rarity_Backgrounds/Item+Addon_Common.png")
    power_bg_img = power_bg_img.resize(POWER_IMAGE_SIZE, Image.NEAREST)
    power_bg_photo = ImageTk.PhotoImage(power_bg_img)

    power_canvas = tk.Canvas(images_frame, width=POWER_IMAGE_SIZE[0], height=POWER_IMAGE_SIZE[1], bg="#333333", highlightthickness=0)
    power_canvas.grid(row=1, column=3, padx=10)
    power_canvas.create_image(0, 0, image=power_bg_photo, anchor="nw")
    power_image_on_canvas = power_canvas.create_image(0, 0, image=None, anchor="nw")

    addons_frame = tk.Frame(images_frame, bg="#333333")
    addons_frame.grid(row=1, column=4, padx=10)

    addon1_canvas = tk.Canvas(addons_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1], bg="#333333", highlightthickness=0)
    addon1_canvas.grid(row=0, column=0, padx=5)
    addon1_bg_on_canvas = addon1_canvas.create_image(0, 0, image=None, anchor="nw")
    addon1_on_canvas = addon1_canvas.create_image(0, 0, image=None, anchor="nw")

    addon2_canvas = tk.Canvas(addons_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1], bg="#333333", highlightthickness=0)
    addon2_canvas.grid(row=0, column=1, padx=5)
    addon2_bg_on_canvas = addon2_canvas.create_image(0, 0, image=None, anchor="nw")
    addon2_on_canvas = addon2_canvas.create_image(0, 0, image=None, anchor="nw")

    addon1_text_label = tk.Label(addons_frame, bg="#333333", fg="white")
    addon1_text_label.grid(row=1, column=0, padx=5)
    addon2_text_label = tk.Label(addons_frame, bg="#333333", fg="white")
    addon2_text_label.grid(row=1, column=1, padx=5)
        
    perk_bg_img = Image.open("./Rarity_Backgrounds/Perk_Tier3.png")
    perk_bg_img = perk_bg_img.resize(PERK_IMAGE_SIZE, Image.NEAREST)
    perk_bg_photo = ImageTk.PhotoImage(perk_bg_img)

    perks_frame = tk.Frame(images_frame, bg="#333333")
    perks_frame.grid(row=2, column=3, columnspan=2, padx=10, pady=5)

    perk1_canvas = tk.Canvas(perks_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1], bg="#333333", highlightthickness=0)
    perk1_canvas.grid(row=0, column=0, padx=5)
    perk1_canvas.create_image(0, 0, image=perk_bg_photo, anchor="nw")
    perk1_on_canvas = perk1_canvas.create_image(0, 0, image=None, anchor="nw")

    perk2_canvas = tk.Canvas(perks_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1], bg="#333333", highlightthickness=0)
    perk2_canvas.grid(row=0, column=1, padx=5)
    perk2_canvas.create_image(0, 0, image=perk_bg_photo, anchor="nw")
    perk2_on_canvas = perk2_canvas.create_image(0, 0, image=None, anchor="nw")

    perk3_canvas = tk.Canvas(perks_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1], bg="#333333", highlightthickness=0)
    perk3_canvas.grid(row=0, column=2, padx=5)
    perk3_canvas.create_image(0, 0, image=perk_bg_photo, anchor="nw")
    perk3_on_canvas = perk3_canvas.create_image(0, 0, image=None, anchor="nw")

    perk4_canvas = tk.Canvas(perks_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1], bg="#333333", highlightthickness=0)
    perk4_canvas.grid(row=0, column=3, padx=5)
    perk4_canvas.create_image(0, 0, image=perk_bg_photo, anchor="nw")
    perk4_on_canvas = perk4_canvas.create_image(0, 0, image=None, anchor="nw")

    perk1_text_label = tk.Label(perks_frame, bg="#333333", fg="white")
    perk1_text_label.grid(row=1, column=0, padx=5)
    perk2_text_label = tk.Label(perks_frame, bg="#333333", fg="white")
    perk2_text_label.grid(row=1, column=1, padx=5)
    perk3_text_label = tk.Label(perks_frame, bg="#333333", fg="white")
    perk3_text_label.grid(row=1, column=2, padx=5)
    perk4_text_label = tk.Label(perks_frame, bg="#333333", fg="white")
    perk4_text_label.grid(row=1, column=3, padx=5)

    buttons_frame = tk.Frame(root, bg="#333333")
    buttons_frame.pack(pady=10)

    randomize_button = tk.Button(buttons_frame, text="Randomize Build", command=randomize_all, fg="white", bg="#1e1e1e", anchor='w', font=('Arial', 18))
    randomize_button.grid(row=0, column=1, padx=5)

    randomize_killer_btn = tk.Button(buttons_frame, text="Randomize Killer", command=randomize_killer, fg="white", bg="#1e1e1e", anchor='w', font=('Arial', 18))
    randomize_killer_btn.grid(row=0, column=0, padx=5)

    randomize_perks_btn = tk.Button(buttons_frame, text="Randomize Perks", command=randomize_perks, fg="white", bg="#1e1e1e", anchor='w', font=('Arial', 18))
    randomize_perks_btn.grid(row=0, column=2, padx=5)

    killer_perks_menu_button = tk.Button(buttons_frame, text="Manage Perks", command=open_killer_perk_menu, fg="white", bg="#1e1e1e", font=('Arial', 18))
    killer_perks_menu_button.grid(row=1, column=0, padx=5)

    killer_menu_button = tk.Button(buttons_frame, text="Manage Killers", command=open_killer_menu, fg="white", bg="#1e1e1e", font=('Arial', 18))
    killer_menu_button.grid(row=1, column=1, padx=5)

    close_button = tk.Button(buttons_frame, text="Close", command=root.destroy, fg="white", bg="#1e1e1e", anchor="center", font=('Arial', 18))
    close_button.grid(row=2, column=1, padx=5)

    root.after(100, prebuild_killer_menu)
    root.after(200, prebuild_killer_perk_menu)

    root.mainloop()


if __name__ == "__main__":
    main()
