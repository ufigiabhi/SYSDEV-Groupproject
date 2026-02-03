import tkinter as tk
import os
from PIL import Image, ImageTk
from base_page import BasePage

class HomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # Load background image
        current_dir = os.path.dirname(__file__)
        image_path = os.path.join(current_dir, "assets", "pink_cafe_new.webp")
        self.original_image = Image.open(image_path)

        # Initial background
        self.bg_image = ImageTk.PhotoImage(self.original_image.resize((600, 400)))
        self.bg_label = tk.Label(self, image=self.bg_image)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Raise navbar
        self.navbar.lift()

        # Heading text 
        self.content.place(relx=0.5, rely=0.5, anchor="center")
        
        heading = tk.Label(
            self.content,
            text="Bristol Pink Cafe",
            font=("Arial", 36, "bold"),
            fg="#ff69b4",       # hot pink text
            bg="black",          # black box
            bd=0,                
            padx=0, pady=0       
        )
        heading.pack()

        self.content.lift()  # making sure content is above background

        # Responsive background
        self.bind("<Configure>", self.resize_bg)

    def resize_bg(self, event):
        if event.width <= 0 or event.height <= 0:
            return
        new_width = event.width
        new_height = event.height
        resized = self.original_image.resize((new_width, new_height))
        self.bg_image = ImageTk.PhotoImage(resized)
        self.bg_label.config(image=self.bg_image)
