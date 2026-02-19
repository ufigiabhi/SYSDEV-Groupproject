import tkinter as tk


class Navbar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#0D0D0D", height=64)
        self.controller = controller
        self.pack(fill="x")
        self.pack_propagate(False)

        self.menu_visible = True
        self._active_page = None

        #  Left: Brand 
        left = tk.Frame(self, bg="#0D0D0D")
        left.pack(side="left", padx=20)

        brand_dot = tk.Frame(left, bg="#FF3E8A", width=10, height=10)
        brand_dot.pack(side="left", padx=(0, 8))
        brand_dot.pack_propagate(False)

        tk.Label(
            left,
            text="Bristol Pink Cafe",
            font=("Georgia", 14, "bold"),
            bg="#0D0D0D",
            fg="#FFFFFF",
        ).pack(side="left")

    
        #  Right: Nav 
        right = tk.Frame(self, bg="#0D0D0D")
        right.pack(side="right", padx=20)

        # Hamburger (hidden menu toggle)
        self.menu_btn = tk.Button(
            right,
            text="≡",
            font=("Arial", 18),
            bg="#0D0D0D",
            fg="#666666",
            bd=0,
            relief="flat",
            cursor="hand2",
            command=self.toggle_menu,
        )
        self.menu_btn.pack(side="left", padx=(0, 12))
        self.menu_btn.bind("<Enter>", lambda e: self.menu_btn.config(fg="#FF3E8A"))
        self.menu_btn.bind("<Leave>", lambda e: self.menu_btn.config(fg="#666666"))

        self.nav_frame = tk.Frame(right, bg="#0D0D0D")
        self.nav_frame.pack(side="left")

        self._make_nav("Home", "HomePage")
        self._make_nav("Dashboard", "DashboardPage")
        self._make_nav("Analytics", "PageTwo")

        # Divider
        tk.Frame(self.nav_frame, width=1, height=20, bg="#222222").pack(
            side="left", padx=12
        )

        # Exit
        exit_btn = tk.Button(
            self.nav_frame,
            text="Exit",
            font=("Helvetica", 9),
            bg="#0D0D0D",
            fg="#E74C3C",
            bd=0,
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=controller.destroy,
        )
        exit_btn.pack(side="left")
        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg="#1A0000", fg="#FF4444"))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg="#0D0D0D", fg="#E74C3C"))

        # Bottom accent line
        accent = tk.Frame(self, bg="#FF3E8A", height=2)
        accent.place(relx=0, rely=1.0, relwidth=1, anchor="sw")

    def _make_nav(self, text, page):
        btn = tk.Button(
            self.nav_frame,
            text=text,
            font=("Helvetica", 9),
            bg="#0D0D0D",
            fg="#AAAAAA",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda p=page: self._nav_click(p, btn),
        )
        btn.pack(side="left", padx=2)
        btn.bind("<Enter>", lambda e, b=btn: b.config(fg="#FFFFFF") if b != self._active_btn else None)
        btn.bind("<Leave>", lambda e, b=btn: b.config(fg="#AAAAAA") if b != self._active_btn else None)
        btn._page = page

        if not hasattr(self, "_nav_buttons"):
            self._nav_buttons = []
            self._active_btn = None
        self._nav_buttons.append(btn)

    def _nav_click(self, page, btn):
        if self._active_btn:
            self._active_btn.config(fg="#AAAAAA", bg="#0D0D0D")
        self._active_btn = btn
        btn.config(fg="#FF3E8A", bg="#0D0D0D")
        self.controller.show_page(page)

    def set_active(self, page_name):
        if hasattr(self, "_nav_buttons"):
            for btn in self._nav_buttons:
                if btn._page == page_name:
                    self._active_btn = btn
                    btn.config(fg="#FF3E8A")
                else:
                    btn.config(fg="#AAAAAA")

    def toggle_menu(self):
        if self.menu_visible:
            self.nav_frame.pack_forget()
        else:
            self.nav_frame.pack(side="left")
        self.menu_visible = not self.menu_visible


class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  
        self.config(bg="#111111")

        self.navbar = Navbar(self, controller)
        self.content = tk.Frame(self, bg="#111111")
        self.content.pack(fill="both", expand=True)

        self.navbar.lift()