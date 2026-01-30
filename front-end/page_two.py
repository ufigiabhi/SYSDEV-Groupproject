from base_page import BasePage
import tkinter as tk
# WIP
class PageTwo(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(
            self.content,
            text="Page Two",
            font=("Arial", 24)
        ).pack(pady=50)
