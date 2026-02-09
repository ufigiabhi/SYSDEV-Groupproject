import tkinter as tk
from tkinter import filedialog, ttk
from .base_page import BasePage
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

from ml.forecasting import sarima_forecast

class DashboardPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.config(bg="#FFC0CB")
        self.content.config(bg="#FFC0CB")

        #Controls
        controls_frame = tk.Frame(self.content, bg="#FFC0CB")
        controls_frame.pack(fill="x", pady=5)

        tk.Button(controls_frame, text="Upload CSV", command=self.load_csv).pack(side="left", padx=5)
        tk.Label(controls_frame, text="Select Training Weeks:", bg="#FFC0CB").pack(side="left", padx=5)

        self.training_weeks = tk.Spinbox(controls_frame, from_=4, to=12, width=5)
        self.training_weeks.pack(side="left", padx=5)
        self.training_weeks.config(command=self.update_forecast)

        # Graph
        self.figure = plt.Figure(figsize=(7,4))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.content)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

        # Actual Data Table (Top)
        top_frame = tk.Frame(self.content)
        top_frame.pack(fill="both", expand=True, pady=5)

        self.top_h_scroll = tk.Scrollbar(top_frame, orient=tk.HORIZONTAL)
        self.top_v_scroll = tk.Scrollbar(top_frame, orient=tk.VERTICAL)

        self.tree_actual = ttk.Treeview(
            top_frame, show="headings",
            xscrollcommand=self.top_h_scroll.set,
            yscrollcommand=self.top_v_scroll.set
        )
        self.top_h_scroll.config(command=self.tree_actual.xview)
        self.top_v_scroll.config(command=self.tree_actual.yview)

        self.top_h_scroll.pack(side="bottom", fill="x")
        self.top_v_scroll.pack(side="right", fill="y")
        self.tree_actual.pack(fill="both", expand=True)

        # Forecast Table (Bottom/predictive)
        bottom_frame = tk.Frame(self.content)
        bottom_frame.pack(fill="both", expand=True, pady=5)

        self.bot_h_scroll = tk.Scrollbar(bottom_frame, orient=tk.HORIZONTAL)
        self.bot_v_scroll = tk.Scrollbar(bottom_frame, orient=tk.VERTICAL)

        self.tree_forecast = ttk.Treeview(
            bottom_frame, show="headings",
            xscrollcommand=self.bot_h_scroll.set,
            yscrollcommand=self.bot_v_scroll.set
        )
        self.bot_h_scroll.config(command=self.tree_forecast.xview)
        self.bot_v_scroll.config(command=self.tree_forecast.yview)

        self.bot_h_scroll.pack(side="bottom", fill="x")
        self.bot_v_scroll.pack(side="right", fill="y")
        self.tree_forecast.pack(fill="both", expand=True)

        # Data storage
        self.data = None

    #Load The CSV
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        
        if not file_path:
            return

        peek = pd.read_csv(file_path, nrows=1)
        if any("Unnamed" in str(col) for col in peek.columns):
            data = pd.read_csv(file_path, header=[0,1])
            data.columns = [col[1] if "Unnamed" not in col[1] else col[0] for col in data.columns]
        else:
            data = pd.read_csv(file_path, header=0)

        data.columns = data.columns.str.strip()

        # Product columns
        product_columns = [c for c in data.columns if c != "Date"]
        if len(product_columns) == 1 and product_columns[0] == "Number Sold":
            data.rename(columns={"Number Sold":"Croissant"}, inplace=True)
            product_columns = ["Croissant"]

        # Numeric conversion
        for col in product_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        self.data = data  # assign first
        self.data["Date"] = pd.to_datetime(self.data["Date"], dayfirst=True)  # then convert


        # Show actual data
        self.update_actual_table(self.data)

        # Run forecast initially
        self.run_forecast()

    #Table Update Helpers 
    def update_actual_table(self, df):
        self.tree_actual.delete(*self.tree_actual.get_children())
        self.tree_actual["columns"] = list(df.columns)
        for col in df.columns:
            self.tree_actual.heading(col, text=col)
        for _, row in df.iterrows():
            self.tree_actual.insert("", "end", values=list(row))

    def update_forecast_table(self, df):
        self.tree_forecast.delete(*self.tree_forecast.get_children())
        self.tree_forecast["columns"] = list(df.columns)
        for col in df.columns:
            self.tree_forecast.heading(col, text=col)
        for _, row in df.iterrows():
            # Replace pd.NA with empty string for display
            values = ["" if pd.isna(v) else v for v in row]
            self.tree_forecast.insert("", "end", values=values)

    #Spinbox Update
    def update_forecast(self):
        if self.data is not None:
            self.run_forecast()

    #Forecasting
    def run_forecast(self):
        self.ax.clear()
        train_weeks = int(self.training_weeks.get())
        forecast_days = train_weeks * 7

        if self.data is None:
            return

        #Prepare forecast table
        forecast_table = {}
        for col in self.data.columns:
            if col == "Date":
                continue
            try:
                ts = (
                    self.data[["Date", col]]
                    .dropna(subset=[col])
                    .assign(**{col: lambda df: pd.to_numeric(df[col], errors="coerce")})
                    .dropna(subset=[col])
                    .set_index("Date")[col]
                )


                if ts.empty:
                    continue

                forecast = sarima_forecast(ts, steps=forecast_days)

                # Plot graph
                future_dates = pd.date_range(start=ts.index[-1]+pd.Timedelta(days=1), periods=len(forecast))
                self.ax.plot(ts.index, ts, label=f"{col} (Actual)")
                self.ax.plot(future_dates, forecast, linestyle="--", label=f"{col} (Forecast)")

                # Weekly averages
                for w in range(train_weeks):
                    col_name = f"{col} W{w + (int(self.training_weeks.cget('from')))}"
                    week_avg = forecast[w*7:(w+1)*7].mean()
                    forecast_table[col_name] = round(week_avg, 2)

            except Exception as e:
                print(f"Forecast failed for {col}: {e}")

        # Convert forecast_table to single-row DataFrame
        if forecast_table:
            forecast_df = pd.DataFrame([forecast_table])
            self.update_forecast_table(forecast_df)
        else:
            self.update_forecast_table(pd.DataFrame())

        #Graph settings
        self.ax.set_title("Sales Forecast using SARIMA")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Number Sold")
        if self.ax.lines:
            self.ax.legend()
        self.figure.autofmt_xdate()
        self.canvas.draw()
