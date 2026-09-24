"""All Tkinter widgets and screens. Game logic lives in randomizer.py;
this module only builds widgets and calls into a RandomizerState.
"""

import tkinter as tk

from game_data import GameData
from randomizer import RandomizerState
from images import load_image, load_rarity_background

POWER_IMAGE_SIZE = (120, 120)
PERK_IMAGE_SIZE = (100, 100)

COLOR_BG = "#333333"
COLOR_BTN = "#1e1e1e"
COLOR_ACTIVE = "#116611"
COLOR_INACTIVE = "#661111"


class RandomizerApp:
    """Owns the main window and the two management sub-windows."""

    def __init__(self, root: tk.Tk, data: GameData, state: RandomizerState):
        self.root = root
        self.data = data
        self.state = state

        # Keep references to PhotoImage objects so Tkinter doesn't garbage collect them.
        self._photo_refs = {}

        self.killer_menu_win = None
        self.killer_perk_menu_win = None

        self._build_main_window()
        self.root.after(100, self._prebuild_killer_menu)
        self.root.after(200, self._prebuild_perk_menu)

    def run(self):
        self.root.mainloop()

    def _build_main_window(self):
        root = self.root
        root.configure(bg=COLOR_BG)
        root.attributes("-fullscreen", True)
        root.bind("<Escape>", lambda e: root.destroy())

        images_frame = tk.Frame(root, bg=COLOR_BG)
        images_frame.pack(pady=20)

        self.image_label = tk.Label(images_frame, bg=COLOR_BG)
        self.image_label.grid(row=0, column=0, rowspan=3, columnspan=2, pady=10)

        self.text_label = tk.Label(
            images_frame, text="No Killer Picked", font=("Arial", 20), fg="white", bg=COLOR_BG
        )
        self.text_label.grid(row=0, column=3, padx=10)

        self._photo_refs["power_bg"] = load_image(
            "./Rarity_Backgrounds/Item+Addon_Common.png", POWER_IMAGE_SIZE
        )
        self.power_canvas = tk.Canvas(
            images_frame, width=POWER_IMAGE_SIZE[0], height=POWER_IMAGE_SIZE[1],
            bg=COLOR_BG, highlightthickness=0,
        )
        self.power_canvas.grid(row=1, column=3, padx=10)
        self.power_canvas.create_image(0, 0, image=self._photo_refs["power_bg"], anchor="nw")
        self.power_image_item = self.power_canvas.create_image(0, 0, image=None, anchor="nw")

        addons_frame = tk.Frame(images_frame, bg=COLOR_BG)
        addons_frame.grid(row=1, column=4, padx=10)
        self.addon_canvases = []
        self.addon_bg_items = []
        self.addon_items = []
        self.addon_text_labels = []
        for i in range(2):
            canvas = tk.Canvas(
                addons_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1],
                bg=COLOR_BG, highlightthickness=0,
            )
            canvas.grid(row=0, column=i, padx=5)
            bg_item = canvas.create_image(0, 0, image=None, anchor="nw")
            fg_item = canvas.create_image(0, 0, image=None, anchor="nw")
            label = tk.Label(addons_frame, bg=COLOR_BG, fg="white")
            label.grid(row=1, column=i, padx=5)
            self.addon_canvases.append(canvas)
            self.addon_bg_items.append(bg_item)
            self.addon_items.append(fg_item)
            self.addon_text_labels.append(label)

        self._photo_refs["perk_bg"] = load_image(
            "./Rarity_Backgrounds/Perk_Tier3.png", PERK_IMAGE_SIZE
        )
        perks_frame = tk.Frame(images_frame, bg=COLOR_BG)
        perks_frame.grid(row=2, column=3, columnspan=2, padx=10, pady=5)
        self.perk_canvases = []
        self.perk_items = []
        self.perk_text_labels = []
        for i in range(4):
            canvas = tk.Canvas(
                perks_frame, width=PERK_IMAGE_SIZE[0], height=PERK_IMAGE_SIZE[1],
                bg=COLOR_BG, highlightthickness=0,
            )
            canvas.grid(row=0, column=i, padx=5)
            canvas.create_image(0, 0, image=self._photo_refs["perk_bg"], anchor="nw")
            item = canvas.create_image(0, 0, image=None, anchor="nw")
            label = tk.Label(perks_frame, bg=COLOR_BG, fg="white")
            label.grid(row=1, column=i, padx=5)
            self.perk_canvases.append(canvas)
            self.perk_items.append(item)
            self.perk_text_labels.append(label)

        buttons_frame = tk.Frame(root, bg=COLOR_BG)
        buttons_frame.pack(pady=10)
        self._make_button(buttons_frame, "Randomize Killer", self.randomize_killer, 0, 0)
        self._make_button(buttons_frame, "Randomize Build", self.randomize_all, 0, 1)
        self._make_button(buttons_frame, "Randomize Perks", self.randomize_perks, 0, 2)
        self._make_button(buttons_frame, "Manage Perks", self.open_perk_menu, 1, 0)
        self._make_button(buttons_frame, "Manage Killers", self.open_killer_menu, 1, 1)
        self._make_button(buttons_frame, "Close", root.destroy, 2, 1)

    def _make_button(self, parent, text, command, row, col):
        btn = tk.Button(
            parent, text=text, command=command, fg="white", bg=COLOR_BTN,
            anchor="w", font=("Arial", 18),
        )
        btn.grid(row=row, column=col, padx=5)
        return btn

    def randomize_all(self):
        self.randomize_killer()
        self.randomize_perks()

    def randomize_killer(self):
        killer_index = self.state.random_killer()
        if killer_index is None:
            self.text_label.config(text="No active killers")
            self.image_label.config(image="")
            self.power_canvas.itemconfig(self.power_image_item, image="")
            return

        addon1_index, addon2_index = self.state.random_addons(killer_index)
        addons = self.data.killer_addons.get(killer_index, [])
        for slot, addon_index in enumerate((addon1_index, addon2_index)):
            canvas = self.addon_canvases[slot]
            if addon_index is None:
                canvas.itemconfig(self.addon_bg_items[slot], image="")
                canvas.itemconfig(self.addon_items[slot], image="")
                self.addon_text_labels[slot].config(text="")
                continue
            addon = addons[addon_index]
            bg_photo = load_rarity_background(addon["rarity"], PERK_IMAGE_SIZE)
            fg_photo = load_image(addon["img"], PERK_IMAGE_SIZE)
            self._photo_refs[f"addon_bg_{slot}"] = bg_photo
            self._photo_refs[f"addon_fg_{slot}"] = fg_photo
            canvas.itemconfig(self.addon_bg_items[slot], image=bg_photo)
            canvas.itemconfig(self.addon_items[slot], image=fg_photo)
            self.addon_text_labels[slot].config(text=addon["name"])

        portrait = load_image(self.data.killers_by_key[killer_index]["portrait"])
        power = load_image(self.data.killers_by_key[killer_index]["power"], POWER_IMAGE_SIZE)
        self._photo_refs["portrait"] = portrait
        self._photo_refs["power"] = power
        self.power_canvas.itemconfig(self.power_image_item, image=power)
        self.image_label.config(image=portrait)
        self.text_label.config(text=self.data.killer_name(killer_index))

    def randomize_perks(self):
        perk_names = self.state.random_perks(count=4)

        if not perk_names:
            self.text_label.config(text="No active perks")
            for canvas, item, label in zip(
                self.perk_canvases, self.perk_items, self.perk_text_labels
            ):
                canvas.itemconfig(item, image="")
                label.config(text="")
            return

        for slot in range(4):
            canvas = self.perk_canvases[slot]
            item = self.perk_items[slot]
            label = self.perk_text_labels[slot]
            if slot >= len(perk_names):
                canvas.itemconfig(item, image="")
                label.config(text="")
                continue
            name = perk_names[slot]
            perk_index = self.data.perk_index_by_name(name)
            photo = load_image(self.data.perks_by_key[perk_index]["image"], PERK_IMAGE_SIZE)
            self._photo_refs[f"perk_{slot}"] = photo
            canvas.itemconfig(item, image=photo)
            label.config(text=name)

    def open_killer_menu(self):
        self.killer_menu_win.deiconify()
        self.killer_menu_win.focus_force()

    def _prebuild_killer_menu(self):
        win = tk.Toplevel(self.root)
        self.killer_menu_win = win
        win.title("Deactivate/Activate Killers")
        win.configure(bg=COLOR_BG)
        win.attributes("-fullscreen", True)
        win.withdraw()
        win.bind("<Escape>", lambda e: win.withdraw())
        win.protocol("WM_DELETE_WINDOW", win.withdraw)
        win.focus_force()
        self._build_killer_grid(win)

    def _build_killer_grid(self, win):
        win.update_idletasks()
        total = len(self.data.killers_by_key)
        pad, border = 5, 3

        button_bar = tk.Frame(win, bg=COLOR_BG)
        tk.Button(
            button_bar, text="Back", command=win.withdraw, fg="white", bg=COLOR_BTN,
            font=("Arial", 10),
        ).pack(side="left", padx=10)
        tk.Button(
            button_bar, text="Disable All",
            command=lambda: self._bulk_toggle_killers(win, False),
            fg="white", bg=COLOR_INACTIVE, font=("Arial", 10),
        ).pack(side="left", padx=10)
        tk.Button(
            button_bar, text="Enable All",
            command=lambda: self._bulk_toggle_killers(win, True),
            fg="white", bg=COLOR_ACTIVE, font=("Arial", 10),
        ).pack(side="left", padx=10)

        win.update_idletasks()
        bar_height = button_bar.winfo_reqheight() + 25
        win_w = win.winfo_screenwidth()
        win_h = win.winfo_screenheight() - bar_height

        best_size, best_cols = 0, 1
        for cols in range(1, total + 1):
            rows = -(-total // cols)
            cell_w = win_w // cols - (2 * pad) - (2 * border)
            cell_h = win_h // rows - (2 * pad) - (2 * border)
            size = min(cell_w, cell_h)
            if size > best_size:
                best_size, best_cols = size, cols

        thumb_size = (best_size, best_size)
        columns = best_cols
        button_bar.grid(row=0, column=0, columnspan=columns, pady=10)

        win.border_frames = {}
        win.thumb_images = []
        for index, key in enumerate(sorted(self.data.killers_by_key)):
            path = self.data.killers_by_key[key]["portrait"]
            photo = load_image(path, thumb_size)
            win.thumb_images.append(photo)

            is_active = self.state.is_killer_active(key)
            border_frame = tk.Frame(win, bg=COLOR_ACTIVE if is_active else COLOR_INACTIVE)
            row, col = (index // columns) + 1, index % columns
            border_frame.grid(row=row, column=col, padx=pad, pady=pad)
            win.border_frames[key] = border_frame

            tk.Button(
                border_frame, image=photo,
                command=lambda k=key, f=border_frame: self._toggle_killer(k, f),
                relief="flat", bg=COLOR_BTN, borderwidth=0,
            ).pack(padx=border, pady=border)

    def _toggle_killer(self, key, border_frame):
        self.state.toggle_killer(key)
        is_active = self.state.is_killer_active(key)
        border_frame.config(bg=COLOR_ACTIVE if is_active else COLOR_INACTIVE)

    def _bulk_toggle_killers(self, win, activate: bool):
        self.state.bulk_toggle_killers(activate)
        new_color = COLOR_ACTIVE if activate else COLOR_INACTIVE
        for border_frame in win.border_frames.values():
            border_frame.config(bg=new_color)

    def open_perk_menu(self):
        self.killer_perk_menu_win.deiconify()
        self.killer_perk_menu_win.focus_force()

    def _prebuild_perk_menu(self):
        win = tk.Toplevel(self.root)
        self.killer_perk_menu_win = win
        win.title("Deactivate/Activate Killer Perks")
        win.configure(bg=COLOR_BG)
        win.attributes("-fullscreen", True)
        win.withdraw()
        win.bind("<Escape>", lambda e: win.withdraw())
        win.protocol("WM_DELETE_WINDOW", win.withdraw)
        win.focus_force()
        self._build_perk_grid(win)

    def _build_perk_grid(self, win):
        win.update_idletasks()
        pad, border, thumb_px = 5, 3, 120

        button_bar = tk.Frame(win, bg=COLOR_BG)
        button_bar.pack(side="top", fill="x", pady=10)
        tk.Button(
            button_bar, text="Back", command=win.withdraw, fg="white", bg=COLOR_BTN,
            font=("Arial", 10),
        ).pack(side="left", padx=5)
        tk.Button(
            button_bar, text="Disable All",
            command=lambda: self._bulk_toggle_perks(win, False),
            fg="white", bg=COLOR_INACTIVE, font=("Arial", 10),
        ).pack(side="right", padx=5)
        tk.Button(
            button_bar, text="Enable All",
            command=lambda: self._bulk_toggle_perks(win, True),
            fg="white", bg=COLOR_ACTIVE, font=("Arial", 10),
        ).pack(side="right", padx=5)
        tk.Button(
            button_bar, text="Deactivate Perks of Deactivated Killers",
            command=lambda: self._deactivate_related_perks(win),
            fg="white", bg=COLOR_BTN, font=("Arial", 10),
        ).pack(side="left", padx=5)
        tk.Button(
            button_bar, text="Activate Perks of Active Killers",
            command=lambda: self._activate_related_perks(win),
            fg="white", bg=COLOR_BTN, font=("Arial", 10),
        ).pack(side="left", padx=5)

        canvas = tk.Canvas(win, bg=COLOR_BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLOR_BG)
        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
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

        win_w = win.winfo_screenwidth()
        columns = max(1, (win_w - scrollbar.winfo_reqwidth()) // (thumb_px + 2 * pad + 2 * border))
        thumb_size = (thumb_px, thumb_px)

        win.border_frames = {}
        win.thumb_images = []
        bg_photo = load_image("./Rarity_Backgrounds/Perk_Tier3.png", thumb_size)
        win.thumb_images.append(bg_photo)

        for index, key in enumerate(sorted(self.data.perks_by_key)):
            path = self.data.perks_by_key[key]["image"]
            photo = load_image(path, thumb_size)
            win.thumb_images.append(photo)

            is_active = self.state.is_perk_active(key)
            border_frame = tk.Frame(scroll_frame, bg=COLOR_ACTIVE if is_active else COLOR_INACTIVE)
            row, col = index // columns, index % columns
            border_frame.grid(row=row, column=col, padx=pad, pady=pad)
            win.border_frames[key] = border_frame

            cell_canvas = tk.Canvas(
                border_frame, width=thumb_px, height=thumb_px, bg=COLOR_BTN, highlightthickness=0
            )
            cell_canvas.pack(padx=border, pady=border)
            cell_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
            cell_canvas.create_image(0, 0, image=photo, anchor="nw")
            cell_canvas.bind(
                "<Button-1>", lambda e, k=key, f=border_frame: self._toggle_perk(k, f)
            )

    def _toggle_perk(self, key, border_frame):
        self.state.toggle_perk(key)
        is_active = self.state.is_perk_active(key)
        border_frame.config(bg=COLOR_ACTIVE if is_active else COLOR_INACTIVE)

    def _bulk_toggle_perks(self, win, activate: bool):
        self.state.bulk_toggle_perks(activate)
        new_color = COLOR_ACTIVE if activate else COLOR_INACTIVE
        for border_frame in win.border_frames.values():
            border_frame.config(bg=new_color)

    def _deactivate_related_perks(self, win):
        self.state.deactivate_related_perks()
        for key, border_frame in win.border_frames.items():
            is_active = self.state.is_perk_active(key)
            border_frame.config(bg=COLOR_ACTIVE if is_active else COLOR_INACTIVE)

    def _activate_related_perks(self, win):
        self.state.activate_related_perks()
        for key, border_frame in win.border_frames.items():
            is_active = self.state.is_perk_active(key)
            border_frame.config(bg=COLOR_ACTIVE if is_active else COLOR_INACTIVE)
