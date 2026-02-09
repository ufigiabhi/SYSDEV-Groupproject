import tkinter as tk

class Navbar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#222", height=50)
        self.controller = controller
        self.pack(fill="x")

        self.menu_visible = True

        # hamburger button
        self.menu_btn = tk.Button(
            self, text="☰", font=("Arial", 14),
            bg="#222", fg="white", bd=0,
            command=self.toggle_menu
        )
        self.menu_btn.pack(side="left", padx=10)

        # frame for nav buttons
        self.menu_frame = tk.Frame(self, bg="#222")
        self.menu_frame.pack(side="left")

        #homepage buton
        self.make_nav_button("Home", "HomePage")
        #Page one button
        self.make_nav_button("Dashboard page", "DashboardPage")
        #Page two button``
        self.make_nav_button("Page Two", "PageTwo")
        # Exit button
        self.make_exit_button("Exit")

    def make_nav_button(self, text, page):
        btn = tk.Button(
            self.menu_frame,
            text=text,
            bg="#222", fg="white",
            bd=0, padx=15,
            command=lambda: self.controller.show_page(page)
        )
        btn.pack(side="left")

    def make_exit_button(self, text):
        btn = tk.Button(
            self.menu_frame,
            text=text,
            bg="#b22222", fg="white",  # red to stand out you guys can change color if you want
            bd=0, padx=15,
            command=self.controller.destroy
        )
        btn.pack(side="left")

    def toggle_menu(self):
        if self.menu_visible:
            self.menu_frame.pack_forget()
        else:
            self.menu_frame.pack(side="left")
        self.menu_visible = not self.menu_visible


class BasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.navbar = Navbar(self, controller)
        self.content = tk.Frame(self)
        self.content.pack(expand=True)
