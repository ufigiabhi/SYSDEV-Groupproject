import tkinter as tk
import os
from base_page import BasePage


class HomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.controller = controller
        self.original_image = None
        self.bg_photo = None

        # Solid dark background, prevents bleed-through from other pages
        self.config(bg="#0D0D0D")
        self.content.config(bg="#0D0D0D")

        # Background image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "assets", "pink_cafe_new.webp")
        self.bg_label = tk.Label(self, bg="#0D0D0D")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        try:
            from PIL import Image, ImageTk, ImageEnhance
            img = Image.open(image_path)
            img = ImageEnhance.Brightness(img).enhance(0.35)
            self.original_image = img
            w, h = 1280, 820
            self.bg_photo = ImageTk.PhotoImage(img.resize((w, h)))
            self.bg_label.config(image=self.bg_photo)
        except Exception:
            pass

        self.navbar.lift()

        hero_outer = tk.Frame(self, bg="#0D0D0D")
        hero_outer.place(relx=0.5, rely=0.52, anchor="center")


        # Title
        tk.Label(hero_outer, text="Bristol Pink",
                 font=("Georgia", 58, "bold"), fg="#FFFFFF", bg="#0D0D0D").pack()

        tk.Label(hero_outer, text="Cafe Intelligence System",
                 font=("Georgia", 26), fg="#FF3E8A", bg="#0D0D0D").pack(pady=(0, 16))

        # Divider
        tk.Frame(hero_outer, bg="#FF3E8A", height=2, width=420).pack(pady=8)

        
        # Buttons
        btn_row = tk.Frame(hero_outer, bg="#0D0D0D")
        btn_row.pack(pady=28)
        self._cta(btn_row, "Open Dashboard", "DashboardPage", primary=True)
        self._cta(btn_row, "View Analytics",    "PageTwo",        primary=False)

        # Stats strip
        strip = tk.Frame(hero_outer, bg="#181818")
        strip.pack(fill="x", pady=16, ipady=14)
        for val, lbl in [("SARIMA", "Forecasting Engine"),
                         ("4-Week", "Prediction Window"),
                         ("Real-time", "Business Insights"),
                         ("Waste", "Reduction Focus")]:
            s = tk.Frame(strip, bg="#181818")
            s.pack(side="left", expand=True, padx=20)
            tk.Label(s, text=val, font=("Georgia", 13, "bold"),
                     fg="#FF3E8A", bg="#181818").pack()
            tk.Label(s, text=lbl, font=("Helvetica", 8),
                     fg="#555555", bg="#181818").pack()

        if self.original_image:
            self.bind("<Configure>", self._resize_bg)

    def _cta(self, parent, text, page, primary):
        bg       = "#FF3E8A" if primary else "#181818"
        hover_bg = "#D0005A" if primary else "#222222"
        btn = tk.Button(parent, text=text, command=lambda: self.controller.show_page(page),
                        font=("Helvetica", 10, "bold") if primary else ("Helvetica", 10),
                        bg=bg, fg="#FFFFFF", padx=28, pady=12,
                        bd=0, relief="flat", cursor="hand2")
        btn.pack(side="left", padx=8)
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def _resize_bg(self, event):
        if event.width <= 1 or event.height <= 1:
            return
        try:
            from PIL import ImageTk
            self.bg_photo = ImageTk.PhotoImage(
                self.original_image.resize((event.width, event.height)))
            self.bg_label.config(image=self.bg_photo)
        except Exception:
            pass
