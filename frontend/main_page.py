import tkinter as tk
from .home_page import HomePage
from .Dashboard_page import DashboardPage
from .page_two import PageTwo

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tkinter Navbar App")
        self.geometry("600x700")

        # Container for pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.pages = {}
        for Page in (HomePage, DashboardPage, PageTwo):
            page = Page(self.container, self)
            self.pages[Page.__name__] = page
            page.place(relwidth=1, relheight=1)

        self.show_page("HomePage")

    def show_page(self, page_name):
        self.pages[page_name].tkraise()


if __name__ == "__main__":
    app = App()
    app.mainloop()
