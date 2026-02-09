import tkinter as tk
from tkinter import filedialog, ttk
from .base_page import BasePage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

# ML imports
from ml.forecasting import load_and_prepare_series, sarima_forecast


class DashboardPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        # background is pink for now 
        self.config(bg="#FFC0CB")         # main frame
        self.content.config(bg="#FFC0CB") # the content frame for widgets 

        # Controls at the top
        controls_frame = tk.Frame(self.content, bg="#FFC0CB")
        controls_frame.pack(fill="x", pady=5)

        tk.Button(
            controls_frame, text="Upload CSV", command=self.load_csv
        ).pack(side="left", padx=5)

        tk.Label(
            controls_frame, text="Select Training Weeks:", bg="#FFC0CB"
        ).pack(side="left", padx=5)

        self.training_weeks = tk.Spinbox(
            controls_frame, from_=4, to=12, width=5
        )
        self.training_weeks.pack(side="left", padx=5)

        # when user changes training weeks re run forecast
        self.training_weeks.config(command=self.update_forecast)

        # Graph in the middle
        self.figure = plt.Figure(figsize=(7, 4))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.content)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

        # Table at the bottom
        self.tree = ttk.Treeview(self.content, show="headings")
        self.tree.pack(fill="x", pady=5)

        self.data = None


    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        # Read CSV
        peek = pd.read_csv(file_path, nrows=1)

        # Coffee CSV with 2 headers
        if any("Unnamed" in str(col) for col in peek.columns):
            data = pd.read_csv(file_path, header=[0, 1])
            data.columns = [
                col[1] if "Unnamed" not in col[1] else col[0]
                for col in data.columns
            ]
        else:
            data = pd.read_csv(file_path, header=0)

        data.columns = data.columns.str.strip()

        # Identify product columns
        product_columns = [col for col in data.columns if col != "Date"]

        # Croissant CSV fix
        if len(product_columns) == 1 and product_columns[0] == "Number Sold":
            data.rename(columns={"Number Sold": "Croissant"}, inplace=True)
            product_columns = ["Croissant"]

        for col in product_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        self.data = data

        # Populate table
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.data.columns)

        for col in self.data.columns:
            self.tree.heading(col, text=col)

        for _, row in self.data.iterrows():
            self.tree.insert("", "end", values=list(row))

        # Run forecasting after loading data
        self.run_forecast()


    def update_forecast(self):
        if self.data is None:
            return
        self.run_forecast()


    def run_forecast(self):
        self.ax.clear()

        dates = pd.to_datetime(self.data["Date"], dayfirst=True)
        train_weeks = int(self.training_weeks.get())
        forecast_days = train_weeks * 7

        for col in self.data.columns:
            if col == "Date":
                continue

            series = self.data[["Date", col]].dropna()

            try:
                ts = load_and_prepare_series(series, col)
                forecast = sarima_forecast(ts, steps=forecast_days)

                future_dates = pd.date_range(
                    start=dates.iloc[-1] + pd.Timedelta(days=1),
                    periods=len(forecast)
                )

                self.ax.plot(dates, self.data[col], label=f"{col} (Actual)")
                self.ax.plot(
                    future_dates,
                    forecast,
                    linestyle="--",
                    label=f"{col} (Forecast)"
                )

            except Exception as e:
                print(f"Forecast failed for {col}: {e}")

        self.ax.set_title("Sales Forecast using SARIMA")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Number Sold")
        self.ax.legend()
        self.figure.autofmt_xdate()
        self.canvas.draw()
