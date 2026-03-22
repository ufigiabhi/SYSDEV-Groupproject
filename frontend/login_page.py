import tkinter as tk

DARK_BG      = "#111111"
PANEL_BG     = "#181818"
CARD_BG      = "#1E1E1E"
ACCENT_PINK  = "#FF3E8A"
FG_PRIMARY   = "#FFFFFF"
FG_SECONDARY = "#AAAAAA"
FG_MUTED     = "#555555"

VALID_USERS = {
    "admin":   "bristol2026",
    "manager": "pinkcafe1",
}


def _hover(btn, normal, hot):
    btn.bind("<Enter>", lambda e: btn.config(bg=hot))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal))


class LoginPage(tk.Frame):
    """
    Login screen shown before the main application loads.
    Restricts access to authorised cafe staff only — NF3.
    No default credentials are displayed to the user.
    """

    def __init__(self, parent, on_success):
        super().__init__(parent, bg=DARK_BG)
        self.on_success = on_success
        self._attempts  = 0
        self._build_ui()

    def _build_ui(self):
        card = tk.Frame(self, bg=CARD_BG,
                        highlightbackground="#2A2A2A", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tk.Frame(card, bg=ACCENT_PINK, height=4).pack(fill="x")

        inner = tk.Frame(card, bg=CARD_BG)
        inner.pack(padx=48, pady=40)

        tk.Label(inner, text="Bristol Pink",
                 font=("Georgia", 22, "bold"),
                 fg=FG_PRIMARY, bg=CARD_BG).pack()
        tk.Label(inner, text="Cafe Intelligence System",
                 font=("Georgia", 12),
                 fg=ACCENT_PINK, bg=CARD_BG).pack(pady=(0, 24))

        tk.Frame(inner, bg="#2A2A2A", height=1).pack(fill="x", pady=(0, 24))

        # Username
        tk.Label(inner, text="Username",
                 font=("Helvetica", 9),
                 fg=FG_SECONDARY, bg=CARD_BG, anchor="w").pack(fill="x")
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(
            inner, textvariable=self.username_var,
            font=("Helvetica", 11),
            bg=PANEL_BG, fg=FG_PRIMARY,
            insertbackground=ACCENT_PINK,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground="#333333",
            highlightcolor=ACCENT_PINK,
            width=28)
        username_entry.pack(ipady=8, pady=(4, 16))
        username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Password
        tk.Label(inner, text="Password",
                 font=("Helvetica", 9),
                 fg=FG_SECONDARY, bg=CARD_BG, anchor="w").pack(fill="x")
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            inner, textvariable=self.password_var,
            show="*",
            font=("Helvetica", 11),
            bg=PANEL_BG, fg=FG_PRIMARY,
            insertbackground=ACCENT_PINK,
            relief="flat", bd=0,
            highlightthickness=1,
            highlightbackground="#333333",
            highlightcolor=ACCENT_PINK,
            width=28)
        self.password_entry.pack(ipady=8, pady=(4, 8))
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())

        # Error label (hidden until needed)
        self.error_var = tk.StringVar()
        tk.Label(inner,
                 textvariable=self.error_var,
                 font=("Helvetica", 9),
                 fg="#E74C3C", bg=CARD_BG).pack(pady=(0, 12))

        # Sign in button
        login_btn = tk.Button(
            inner, text="Sign In",
            command=self._attempt_login,
            font=("Helvetica", 10, "bold"),
            bg=ACCENT_PINK, fg=FG_PRIMARY,
            padx=24, pady=10,
            bd=0, relief="flat", cursor="hand2",
            width=24)
        login_btn.pack()
        _hover(login_btn, ACCENT_PINK, "#D0005A")

        # Security note, deliberately no credentials shown
        tk.Label(inner,
                 text="Contact your system administrator for access.",
                 font=("Helvetica", 8, "italic"),
                 fg=FG_MUTED, bg=CARD_BG).pack(pady=(16, 0))

        username_entry.focus()

    def _attempt_login(self):
        username = self.username_var.get().strip().lower()
        password = self.password_var.get().strip()

        if VALID_USERS.get(username) == password:
            self.error_var.set("")
            self.on_success()
        else:
            self._attempts += 1
            if self._attempts >= 3:
                self.error_var.set(
                    f"Access locked after {self._attempts} failed attempts. "
                    "Contact your system administrator.")
            else:
                self.error_var.set(
                    f"Incorrect username or password.  "
                    f"Attempt {self._attempts} of 3.")
            self.password_var.set("")
            self.password_entry.focus()
