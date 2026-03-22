import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from base_page import BasePage
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np

DARK_BG      = "#111111"
PANEL_BG     = "#181818"
CARD_BG      = "#1E1E1E"
ACCENT_PINK  = "#FF3E8A"
ACCENT_BLUE  = "#3A9BD5"
ACCENT_GREEN = "#2ECC71"
ACCENT_AMB   = "#F0A500"
FG_PRIMARY   = "#FFFFFF"
FG_SECONDARY = "#AAAAAA"
FG_MUTED     = "#555555"


def _hover(btn, normal, hot):
    btn.bind("<Enter>", lambda e: btn.config(bg=hot))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal))


def _smart_forecast(ts_train, steps=28):
    """
    Tiered forecast:
      - 42+ days  → SARIMA (with flat-line fallback detection)
      - 14-41 days → Seasonal MA
      - < 14 days  → flat mean
    """
    n    = len(ts_train)
    vals = ts_train.values.astype(float)

    def _seasonal_ma(series, steps):
        week   = 7
        last2  = series[-week * 2:] if len(series) >= week * 2 else series
        w1     = last2[:week] if len(last2) >= week * 2 else last2
        w2     = last2[week:] if len(last2) >= week * 2 else last2
        pattern = 0.35 * w1 + 0.65 * w2
        x      = np.arange(len(last2))
        slope  = np.clip(np.polyfit(x, last2, 1)[0], -2.0, 2.0)
        return np.array([max(0.0, float(pattern[i % week]) + slope * (i + 1))
                         for i in range(steps)])

    if n >= 42:
        try:
            from ml.forecasting import sarima_forecast
            raw      = sarima_forecast(ts_train, steps=steps)
            t_mean   = float(ts_train.mean())
            t_std    = float(ts_train.std())
            raw      = raw.clip(lower=max(0, t_mean - 3 * t_std),
                                upper=t_mean + 3 * t_std)
            raw_vals = raw.values.astype(float)
            if raw_vals.std() < t_std * 0.20:
                return _seasonal_ma(vals, steps), "Seasonal MA"
            return raw_vals, "SARIMA"
        except Exception as e:
            print(f"[SARIMA failed] {e}")

    if n >= 14:
        return _seasonal_ma(vals, steps), "Seasonal MA"

    return np.full(steps, float(ts_train.mean())), "Mean"


class DashboardPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.config(bg=DARK_BG)
        self.content.config(bg=DARK_BG)
        self.data            = None
        self._plot_data      = {}
        self._forecast_start = None
        self._all_dates      = []

        self._build_header()
        self._build_controls()
        self._build_main_area()

    # Header
    def _build_header(self):
        hdr = tk.Frame(self.content, bg=DARK_BG)
        hdr.pack(fill="x", padx=30, pady=(14, 4))

        left = tk.Frame(hdr, bg=DARK_BG)
        left.pack(side="left")
        tk.Label(left, text="Sales Forecasting",
                 font=("Georgia", 20, "bold"),
                 fg=FG_PRIMARY, bg=DARK_BG).pack(anchor="w")

        right = tk.Frame(hdr, bg=DARK_BG)
        right.pack(side="right")
        self.status_dot = tk.Label(right, text="●",
                                   font=("Helvetica", 13),
                                   fg=FG_MUTED, bg=DARK_BG)
        self.status_dot.pack(side="right", padx=(4, 0))
        self.status_var = tk.StringVar(value="No data loaded")
        tk.Label(right, textvariable=self.status_var,
                 font=("Helvetica", 9, "italic"),
                 fg=FG_MUTED, bg=DARK_BG).pack(side="right")

        tk.Frame(self.content, bg="#222222", height=1).pack(fill="x",
                                                             padx=30, pady=4)

    # Controls bar
    def _build_controls(self):
        bar = tk.Frame(self.content, bg=PANEL_BG)
        bar.pack(fill="x", padx=30, pady=(0, 6), ipady=9)

        # Upload CSV
        up_btn = tk.Button(bar, text="Upload CSV",
                           command=self.load_csv,
                           font=("Helvetica", 9, "bold"),
                           bg=ACCENT_PINK, fg=FG_PRIMARY,
                           padx=18, pady=7, bd=0, relief="flat",
                           cursor="hand2")
        up_btn.pack(side="left", padx=(14, 8))
        _hover(up_btn, ACCENT_PINK, "#D0005A")

        # Training period spinner auto-runs forecast on change
        tk.Label(bar, text="Training period:",
                 font=("Helvetica", 9),
                 fg=FG_SECONDARY, bg=PANEL_BG).pack(side="left", padx=(14, 4))

        self.training_weeks = tk.Spinbox(
            bar, from_=4, to=8, width=3,
            font=("Helvetica", 10, "bold"),
            bg=CARD_BG, fg=ACCENT_PINK,
            buttonbackground=CARD_BG, relief="flat", bd=0,
            command=self._on_training_change)
        self.training_weeks.pack(side="left")

        tk.Label(bar, text="weeks",
                 font=("Helvetica", 9),
                 fg=FG_MUTED, bg=PANEL_BG).pack(side="left", padx=(2, 14))

        # NOTE: "Update Forecast" button removed spinner already triggers
        # re-forecast immediately via _on_training_change.

        # Zoom dropdown
        tk.Label(bar, text="Zoom:",
                 font=("Helvetica", 9),
                 fg=FG_SECONDARY, bg=PANEL_BG).pack(side="left", padx=(18, 4))

        self.zoom_var = tk.StringVar(value="All")
        zm = ttk.Combobox(bar, textvariable=self.zoom_var,
                          values=["All",
                                  "Last 7 days",
                                  "Last 14 days",
                                  "Last 30 days",
                                  "Forecast only"],
                          width=13, state="readonly",
                          font=("Helvetica", 9))
        zm.pack(side="left")
        zm.bind("<<ComboboxSelected>>", lambda e: self.apply_zoom())

        # Active method label
        self.method_var = tk.StringVar(value="")
        tk.Label(bar, textvariable=self.method_var,
                 font=("Helvetica", 8, "italic"),
                 fg=ACCENT_BLUE, bg=PANEL_BG).pack(side="left", padx=(16, 0))

        # Treeview style
        s = ttk.Style()
        s.configure("Pink.Treeview",
                     background=CARD_BG, foreground=FG_SECONDARY,
                     rowheight=24, fieldbackground=CARD_BG, borderwidth=0)
        s.configure("Pink.Treeview.Heading",
                     background=PANEL_BG, foreground=ACCENT_PINK,
                     font=("Helvetica", 9, "bold"), relief="flat")
        s.map("Pink.Treeview", background=[("selected", "#2A2A2A")])

    # Main area (chart + tables)
    def _build_main_area(self):
        pane = tk.PanedWindow(self.content, orient=tk.VERTICAL,
                              bg=DARK_BG, sashwidth=5,
                              sashrelief="flat", sashpad=2)
        pane.pack(fill="both", expand=True, padx=30, pady=(0, 8))

        # Chart
        chart_frame = tk.Frame(pane, bg=CARD_BG,
                               highlightbackground="#2A2A2A",
                               highlightthickness=1)
        pane.add(chart_frame, minsize=300)

        title_row = tk.Frame(chart_frame, bg=CARD_BG)
        title_row.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(title_row, text="SARIMA Sales Forecast",
                 font=("Georgia", 12, "bold"),
                 fg=FG_PRIMARY, bg=CARD_BG).pack(side="left")
        tk.Label(title_row,
                 text="  Solid = historical   Dashed = predicted",
                 font=("Helvetica", 8), fg=FG_MUTED,
                 bg=CARD_BG).pack(side="left")

        plt.style.use("dark_background")
        self.figure = plt.Figure(figsize=(11, 4.0), dpi=95, facecolor=CARD_BG)
        self.ax     = self.figure.add_subplot(111)
        self._style_ax(self.ax)

        self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True,
                                         padx=6, pady=6)

        # Tables
        tables_frame = tk.Frame(pane, bg=DARK_BG)
        pane.add(tables_frame, minsize=150)

        # Actual table (left)
        lf = tk.Frame(tables_frame, bg=CARD_BG,
                      highlightbackground="#2A2A2A", highlightthickness=1)
        lf.pack(side="left", fill="both", expand=True, padx=(0, 4), pady=2)

        lh = tk.Frame(lf, bg=PANEL_BG)
        lh.pack(fill="x")
        tk.Label(lh, text="Historical Sales Data",
                 font=("Helvetica", 9, "bold"),
                 fg=FG_PRIMARY, bg=PANEL_BG,
                 pady=7, padx=10).pack(side="left")
        tk.Label(lh, text="(first 100 rows)",
                 font=("Helvetica", 8),
                 fg=FG_MUTED, bg=PANEL_BG).pack(side="left")

        li = tk.Frame(lf, bg=CARD_BG)
        li.pack(fill="both", expand=True)
        lhs = tk.Scrollbar(li, orient=tk.HORIZONTAL)
        lvs = tk.Scrollbar(li, orient=tk.VERTICAL)
        self.tree_actual = ttk.Treeview(li, show="headings",
                                         style="Pink.Treeview",
                                         xscrollcommand=lhs.set,
                                         yscrollcommand=lvs.set, height=4)
        lhs.config(command=self.tree_actual.xview)
        lvs.config(command=self.tree_actual.yview)
        lhs.pack(side="bottom", fill="x")
        lvs.pack(side="right",  fill="y")
        self.tree_actual.pack(fill="both", expand=True)

        # Forecast table (right)
        rf = tk.Frame(tables_frame, bg=CARD_BG,
                      highlightbackground="#2A2A2A", highlightthickness=1)
        rf.pack(side="left", fill="both", expand=True, padx=(4, 0), pady=2)

        rh = tk.Frame(rf, bg=PANEL_BG)
        rh.pack(fill="x")
        tk.Label(rh, text="4-Week Forecast",
                 font=("Helvetica", 9, "bold"),
                 fg=ACCENT_GREEN, bg=PANEL_BG,
                 pady=7, padx=10).pack(side="left")
        tk.Label(rh, text="(weekly averages)",
                 font=("Helvetica", 8),
                 fg=FG_MUTED, bg=PANEL_BG).pack(side="left")

        ri = tk.Frame(rf, bg=CARD_BG)
        ri.pack(fill="both", expand=True)
        rhs = tk.Scrollbar(ri, orient=tk.HORIZONTAL)
        rvs = tk.Scrollbar(ri, orient=tk.VERTICAL)
        self.tree_forecast = ttk.Treeview(ri, show="headings",
                                           style="Pink.Treeview",
                                           xscrollcommand=rhs.set,
                                           yscrollcommand=rvs.set, height=4)
        rhs.config(command=self.tree_forecast.xview)
        rvs.config(command=self.tree_forecast.yview)
        rhs.pack(side="bottom", fill="x")
        rvs.pack(side="right",  fill="y")
        self.tree_forecast.pack(fill="both", expand=True)

        tk.Label(tables_frame,
                 text="Visit Analytics after uploading for business intelligence",
                 font=("Helvetica", 8, "italic"),
                 fg=FG_MUTED, bg=DARK_BG).pack(
            side="bottom", anchor="w", padx=4, pady=2)

    # Helpers
    def _style_ax(self, ax):
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=FG_SECONDARY, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color("#333333")
        ax.grid(True, alpha=0.15, color="#FFFFFF", linestyle="--")

    def _on_training_change(self):
        """Called whenever the spinner value changes."""
        if self.data is not None:
            self.run_forecast()

    # CSV loading
    def load_csv(self):
        path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select Sales Data CSV")
        if not path:
            return

        self._set_status("Loading...", ACCENT_AMB)
        self.content.update()
        try:
            peek = pd.read_csv(path, nrows=1)
            if any("Unnamed" in str(c) for c in peek.columns):
                data = pd.read_csv(path, header=[0, 1])
                data.columns = [c[1] if "Unnamed" not in c[1] else c[0]
                                 for c in data.columns]
            else:
                data = pd.read_csv(path, header=0)

            data.columns = data.columns.str.strip()
            product_cols = [c for c in data.columns if c != "Date"]
            if len(product_cols) == 1 and product_cols[0] == "Number Sold":
                data.rename(columns={"Number Sold": "Croissant"}, inplace=True)

            for col in [c for c in data.columns if c != "Date"]:
                data[col] = pd.to_numeric(data[col], errors="coerce")

            data["Date"] = pd.to_datetime(data["Date"], dayfirst=True)
            self.data = data
            self.controller.shared_data = self.data

            self._populate_actual_table(self.data)
            self.run_forecast()
            self._set_status(f"Loaded {len(data)} rows", ACCENT_GREEN)

        except Exception as exc:
            self._set_status("Load failed", "#E74C3C")
            messagebox.showerror("Load Error", f"Failed to read CSV:\n{exc}")

    # Forecast
    def run_forecast(self):
        if self.data is None:
            return

        self.ax.clear()
        self._style_ax(self.ax)

        train_weeks   = int(self.training_weeks.get())
        FORECAST_DAYS = 28

        COLORS = [ACCENT_PINK, ACCENT_BLUE, "#A855F7", ACCENT_AMB, "#34D399"]
        forecast_table   = {}
        self._plot_data  = {}
        self._forecast_start = None
        self._all_dates  = []
        methods_used     = set()

        for ci, col in enumerate([c for c in self.data.columns
                                   if c != "Date"]):
            try:
                full_ts = (
                    self.data[["Date", col]].dropna(subset=[col])
                    .assign(**{col: lambda df, c=col:
                                pd.to_numeric(df[c], errors="coerce")})
                    .dropna(subset=[col])
                    .set_index("Date")[col]
                )
                if full_ts.empty or len(full_ts) < 14:
                    continue

                train_days = train_weeks * 7
                ts_train   = (full_ts.tail(train_days)
                              if len(full_ts) > train_days else full_ts)

                smooth_vals, method = _smart_forecast(ts_train,
                                                       steps=FORECAST_DAYS)
                methods_used.add(method)

                # Hard-cap to exactly FORECAST_DAYS values so weekly
                # slicing always produces exactly 4 non-overlapping buckets
                smooth_vals = np.asarray(smooth_vals).flatten()[:FORECAST_DAYS]
                if len(smooth_vals) < FORECAST_DAYS:
                    smooth_vals = np.pad(smooth_vals,
                                         (0, FORECAST_DAYS - len(smooth_vals)),
                                         constant_values=smooth_vals[-1])

                t_std = float(ts_train.std())

                future_dates = pd.date_range(
                    start=full_ts.index[-1] + pd.Timedelta(days=1),
                    periods=FORECAST_DAYS)

                if self._forecast_start is None:
                    self._forecast_start = future_dates[0]

                color = COLORS[ci % len(COLORS)]

                self.ax.plot(full_ts.index, full_ts,
                             color=color, linewidth=1.8,
                             label=f"{col} - actual", zorder=3)
                self.ax.plot(future_dates, smooth_vals,
                             color=color, linewidth=2.2, linestyle="--",
                             alpha=0.9,
                             label=f"{col} - forecast", zorder=3)
                self.ax.fill_between(
                    future_dates,
                    np.maximum(0, smooth_vals - t_std * 0.6),
                    smooth_vals + t_std * 0.6,
                    color=color, alpha=0.10, zorder=2)

                self._plot_data[col] = {
                    "ts":           full_ts,
                    "smooth":       smooth_vals,
                    "future_dates": future_dates,
                    "color":        color}

                # Collect all dates for zoom
                self._all_dates.extend(full_ts.index.tolist())
                self._all_dates.extend(future_dates.tolist())

                # FIX: 4 distinct weekly buckets (days 0-6, 7-13, 14-20, 21-27)
                for w in range(4):
                    key = f"{col} - Wk {w + 1}"
                    week_slice = smooth_vals[w * 7: (w + 1) * 7]
                    forecast_table[key] = round(float(np.mean(week_slice)), 1)

            except Exception as exc:
                print(f"[Forecast] {col}: {exc}")

        if forecast_table:
            self._populate_forecast_table(forecast_table)

        if self._forecast_start:
            self.ax.axvline(self._forecast_start, color="#555555",
                            linewidth=1.2, linestyle=":",
                            label="Forecast start", zorder=1)

        method_str = " + ".join(sorted(methods_used)) if methods_used else ""
        self.method_var.set(f"Method: {method_str}" if method_str else "")

        self.ax.set_title(
            f"4-Week Sales Forecast  (trained on last {train_weeks} weeks)",
            color=FG_SECONDARY, fontsize=10, pad=10, loc="left")
        self.ax.set_xlabel("Date", color=FG_MUTED, fontsize=9)
        self.ax.set_ylabel("Units Sold", color=FG_MUTED, fontsize=9)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))

        if self.ax.lines:
            leg = self.ax.legend(loc="upper left", fontsize=8,
                                  framealpha=0.2, facecolor=CARD_BG,
                                  edgecolor="#333333")
            for t in leg.get_texts():
                t.set_color(FG_SECONDARY)

        self.figure.autofmt_xdate(rotation=25)
        self.figure.tight_layout()
        self.canvas.draw()
        self._set_status(
            f"Forecast updated  ({train_weeks}wk training · {method_str})",
            ACCENT_GREEN)

    # Zoom FIX: each option now sets a genuinely different x range
    def apply_zoom(self):
        if not self._plot_data or not self._all_dates:
            return

        zoom    = self.zoom_var.get()
        all_d   = self._all_dates
        max_d   = max(all_d)       # last forecast date
        min_d   = min(all_d)       # first historical date

        if zoom == "Last 7 days":
            # 7 historical days up to the start of the forecast
            anchor = self._forecast_start or max_d
            self.ax.set_xlim(anchor - pd.Timedelta(days=7), anchor)

        elif zoom == "Last 14 days":
            anchor = self._forecast_start or max_d
            self.ax.set_xlim(anchor - pd.Timedelta(days=14), anchor)

        elif zoom == "Last 30 days":
            anchor = self._forecast_start or max_d
            self.ax.set_xlim(anchor - pd.Timedelta(days=30), anchor)

        elif zoom == "Forecast only":
            # Show only the 28-day forecast window
            if self._forecast_start:
                self.ax.set_xlim(
                    self._forecast_start - pd.Timedelta(days=2),
                    self._forecast_start + pd.Timedelta(days=28))
            else:
                self.ax.set_xlim(min_d, max_d)

        else:  # "All"
            self.ax.set_xlim(min_d, max_d)

        self.canvas.draw()

    # Table population
    def _populate_actual_table(self, df):
        self.tree_actual.delete(*self.tree_actual.get_children())
        display = df.head(100)
        self.tree_actual["columns"] = list(display.columns)
        for col in display.columns:
            self.tree_actual.heading(col, text=col)
            self.tree_actual.column(col, width=110, anchor="center")
        for _, row in display.iterrows():
            vals = list(row)
            if display.columns[0] == "Date" and isinstance(vals[0],
                                                             pd.Timestamp):
                vals[0] = vals[0].strftime("%d %b %Y")
            self.tree_actual.insert("", "end", values=vals)

    def _populate_forecast_table(self, forecast_dict):
        """Display forecast as Week rows × Product columns."""
        self.tree_forecast.delete(*self.tree_forecast.get_children())
        if not forecast_dict:
            return

        products, weeks, data = [], [], {}
        for key, val in forecast_dict.items():
            if " - Wk " in key:
                parts   = key.split(" - Wk ")
                product = parts[0]
                wk      = int(parts[1])
            else:
                product = key
                wk      = 1

            # Only ever show weeks 1-4
            if wk > 4:
                continue

            if product not in products:
                products.append(product)
            if wk not in weeks:
                weeks.append(wk)
            data.setdefault(wk, {})[product] = val

        weeks.sort()
        weeks = weeks[:4]  # hard cap , never more than 4
        cols = ["Week"] + products
        self.tree_forecast["columns"] = cols
        self.tree_forecast.heading("Week", text="Week")
        self.tree_forecast.column("Week", width=70, anchor="center")
        for p in products:
            self.tree_forecast.heading(p, text=p)
            self.tree_forecast.column(p, width=120, anchor="center")

        for wk in weeks:
            row_vals = [f"Week {wk}"]
            for p in products:
                v = data.get(wk, {}).get(p, "")
                row_vals.append(f"{v:.1f}" if isinstance(v, float) else str(v))
            self.tree_forecast.insert("", "end", values=row_vals)

    # Status indicator
    def _set_status(self, msg, color):
        self.status_var.set(msg)
        self.status_dot.config(fg=color)
        self.content.update_idletasks()
