from .base_page import BasePage
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sys
import os

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    from ml.advanced_forecasting import AdvancedForecaster
    ML_AVAILABLE = True
except ImportError as e:
    print(f"[PageTwo] ML module not available: {e}")
    ML_AVAILABLE = False

DARK_BG      = "#111111"
PANEL_BG     = "#181818"
CARD_BG      = "#1E1E1E"
ACCENT_PINK  = "#FF3E8A"
ACCENT_BLUE  = "#3A9BD5"
ACCENT_GREEN = "#2ECC71"
ACCENT_AMB   = "#F0A500"
ACCENT_PURP  = "#A855F7"
FG_PRIMARY   = "#FFFFFF"
FG_SECONDARY = "#AAAAAA"
FG_MUTED     = "#555555"

CHART_COLORS = [ACCENT_PINK, ACCENT_BLUE, ACCENT_GREEN, ACCENT_AMB, ACCENT_PURP]


def _label(parent, text, size=10, bold=False, color=FG_PRIMARY, bg=CARD_BG, pady=0):
    weight = "bold" if bold else "normal"
    return tk.Label(parent, text=text, font=("Helvetica", size, weight),
                    fg=color, bg=bg, pady=pady)


def _section_title(parent, text, bg=PANEL_BG):
    f = tk.Frame(parent, bg=bg)
    f.pack(fill="x", padx=0, pady=0)
    tk.Frame(f, bg=ACCENT_PINK, width=3).pack(side="left", fill="y")
    tk.Label(f, text=text, font=("Georgia", 12, "bold"),
             fg=FG_PRIMARY, bg=bg, padx=12, pady=10).pack(side="left")
    return f


def _card(parent, bg=CARD_BG, pad_x=0, pad_y=6):
    f = tk.Frame(parent, bg=bg,
                 highlightbackground="#2A2A2A", highlightthickness=1)
    f.pack(fill="x", padx=pad_x, pady=pad_y)
    return f


def _kpi_card(parent, title, value, subtitle, color, bg=CARD_BG):
    card = tk.Frame(parent, bg=bg,
                    highlightbackground="#2A2A2A", highlightthickness=1)
    card.pack(side="left", padx=8, ipadx=20, ipady=16, expand=True, fill="x")
    tk.Label(card, text=title, font=("Helvetica", 8),
             fg=FG_MUTED, bg=bg).pack(pady=(8, 0))
    tk.Label(card, text=value, font=("Georgia", 26, "bold"),
             fg=color, bg=bg).pack()
    tk.Label(card, text=subtitle, font=("Helvetica", 8),
             fg=FG_MUTED, bg=bg).pack(pady=(0, 8))
    return card


def _styled_ax(ax, bg=CARD_BG):
    ax.set_facecolor(bg)
    ax.tick_params(colors=FG_SECONDARY, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#2A2A2A")
    ax.grid(True, alpha=0.12, color="#FFFFFF", linestyle="--")


class PageTwo(BasePage):
    """Business Intelligence & Decision Support Dashboard"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.config(bg=DARK_BG)
        self.content.config(bg=DARK_BG)

        self.forecaster = AdvancedForecaster() if ML_AVAILABLE else None
        self._build_header()
        self._build_tabs()
        self._build_footer()


    def _build_header(self):
        hdr = tk.Frame(self.content, bg=DARK_BG)
        hdr.pack(fill="x", padx=30, pady=(18, 4))

        left = tk.Frame(hdr, bg=DARK_BG)
        left.pack(side="left")

        tk.Label(left, text="Business Intelligence",
                 font=("Georgia", 22, "bold"), fg=FG_PRIMARY, bg=DARK_BG).pack(anchor="w")
        tk.Label(left, text="Transform ML forecasts into actionable cafe decisions",
                 font=("Helvetica", 10), fg=FG_MUTED, bg=DARK_BG).pack(anchor="w")

        # Data source indicator
        self.data_source_lbl = tk.Label(
            hdr, text="● Sample data",
            font=("Helvetica", 8, "italic"), fg=FG_MUTED, bg=DARK_BG,
        )
        self.data_source_lbl.pack(side="right", padx=4)

        # Refresh button
        ref_btn = tk.Button(
            hdr, text="Refresh Analytics",
            font=("Helvetica", 9, "bold"),
            bg=ACCENT_BLUE, fg=FG_PRIMARY,
            padx=16, pady=8, bd=0, relief="flat", cursor="hand2",
            command=self.refresh_analytics,
        )
        ref_btn.pack(side="right", padx=8)
        ref_btn.bind("<Enter>", lambda e: ref_btn.config(bg="#2980B9"))
        ref_btn.bind("<Leave>", lambda e: ref_btn.config(bg=ACCENT_BLUE))

        tk.Frame(self.content, bg="#222222", height=1).pack(fill="x", padx=30, pady=6)

    def _build_tabs(self):
        s = ttk.Style()
        s.configure("BI.TNotebook", background=DARK_BG, borderwidth=0)
        s.configure("BI.TNotebook.Tab",
                    background=PANEL_BG, foreground=FG_MUTED,
                    padding=[20, 9], font=("Helvetica", 9, "bold"))
        s.map("BI.TNotebook.Tab",
              background=[("selected", CARD_BG)],
              foreground=[("selected", ACCENT_PINK)])

        self.nb = ttk.Notebook(self.content, style="BI.TNotebook")
        self.nb.pack(fill="both", expand=True, padx=30, pady=0)

        self._tab_overview()
        self._tab_performance()
        self._tab_trends()
        self._tab_recommendations()

    def _tab_overview(self):
        frm = tk.Frame(self.nb, bg=CARD_BG)
        self.nb.add(frm, text=" Overview ")

        # KPI row
        self.kpi_row = tk.Frame(frm, bg=CARD_BG)
        self.kpi_row.pack(fill="x", padx=20, pady=(16, 8))

        # Charts
        charts = tk.Frame(frm, bg=CARD_BG)
        charts.pack(fill="both", expand=True, padx=20, pady=4)

        # Left – daily trend
        left_wrap = tk.Frame(charts, bg=PANEL_BG,
                             highlightbackground="#2A2A2A", highlightthickness=1)
        left_wrap.pack(side="left", fill="both", expand=True, padx=(0, 6))

        _section_title(left_wrap, "Daily Sales Trend: Last 30 Days")

        self.daily_fig = plt.Figure(figsize=(5.5, 3.5), dpi=95, facecolor=PANEL_BG)
        self.daily_ax  = self.daily_fig.add_subplot(111)
        _styled_ax(self.daily_ax, PANEL_BG)
        self.daily_canvas = FigureCanvasTkAgg(self.daily_fig, left_wrap)
        self.daily_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Right – product split
        right_wrap = tk.Frame(charts, bg=PANEL_BG,
                              highlightbackground="#2A2A2A", highlightthickness=1)
        right_wrap.pack(side="left", fill="both", expand=True, padx=(6, 0))

        _section_title(right_wrap, "Product Sales Distribution")

        self.pie_fig = plt.Figure(figsize=(5, 3.5), dpi=95, facecolor=PANEL_BG)
        self.pie_ax  = self.pie_fig.add_subplot(111)
        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, right_wrap)
        self.pie_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # TAB 2: PERFORMANCE 
    def _tab_performance(self):
        frm = tk.Frame(self.nb, bg=CARD_BG)
        self.nb.add(frm, text=" Performance ")

        _section_title(frm, "Product Performance Comparison", bg=PANEL_BG)

        # Scrollable inner
        canvas = tk.Canvas(frm, bg=CARD_BG, highlightthickness=0)
        sb = tk.Scrollbar(frm, orient="vertical", command=canvas.yview)
        self.perf_inner = tk.Frame(canvas, bg=CARD_BG)

        self.perf_inner.bind("<Configure>",
                             lambda e: canvas.configure(
                                 scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.perf_inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)

        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Bar chart placeholder
        chart_wrap = tk.Frame(frm, bg=PANEL_BG,
                              highlightbackground="#2A2A2A", highlightthickness=1)
        chart_wrap.pack(fill="both", expand=True, padx=20, pady=8, in_=self.perf_inner)

        _section_title(chart_wrap, "Comparative Total Sales by Product")

        self.perf_fig = plt.Figure(figsize=(8, 3.2), dpi=95, facecolor=PANEL_BG)
        self.perf_ax  = self.perf_fig.add_subplot(111)
        _styled_ax(self.perf_ax, PANEL_BG)
        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, chart_wrap)
        self.perf_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Table container
        self.perf_table_frame = tk.Frame(self.perf_inner, bg=CARD_BG)
        self.perf_table_frame.pack(fill="x", padx=20, pady=8)

    def _tab_trends(self):
        frm = tk.Frame(self.nb, bg=CARD_BG)
        self.nb.add(frm, text=" Trends ")

        top = tk.Frame(frm, bg=CARD_BG)
        top.pack(fill="both", expand=True, padx=20, pady=8)

        # Weekly bar chart
        weekly_wrap = tk.Frame(top, bg=PANEL_BG,
                               highlightbackground="#2A2A2A", highlightthickness=1)
        weekly_wrap.pack(fill="both", expand=True, pady=(0, 6))
        _section_title(weekly_wrap, "Average Sales by Day of Week")

        self.weekly_fig = plt.Figure(figsize=(8, 3.0), dpi=95, facecolor=PANEL_BG)
        self.weekly_ax  = self.weekly_fig.add_subplot(111)
        _styled_ax(self.weekly_ax, PANEL_BG)
        self.weekly_canvas = FigureCanvasTkAgg(self.weekly_fig, weekly_wrap)
        self.weekly_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

        # Insights text card
        insights_wrap = tk.Frame(top, bg=PANEL_BG,
                                 highlightbackground="#2A2A2A", highlightthickness=1)
        insights_wrap.pack(fill="x", pady=(6, 0))
        _section_title(insights_wrap, "Key Pattern Insights")

        self.insights_text = tk.Text(
            insights_wrap, height=7,
            font=("Helvetica", 10), fg=FG_SECONDARY, bg=PANEL_BG,
            wrap="word", relief="flat", padx=16, pady=12,
            insertbackground=ACCENT_PINK,
        )
        self.insights_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _tab_recommendations(self):
        frm = tk.Frame(self.nb, bg=CARD_BG)
        self.nb.add(frm, text=" AI Recommendations ")

        pane = tk.Frame(frm, bg=CARD_BG)
        pane.pack(fill="both", expand=True, padx=20, pady=8)

        # Left – model metrics
        left = tk.Frame(pane, bg=PANEL_BG,
                        highlightbackground="#2A2A2A", highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        _section_title(left, "SARIMA Model Accuracy Metrics")
        self.metrics_container = tk.Frame(left, bg=PANEL_BG)
        self.metrics_container.pack(fill="both", expand=True, padx=12, pady=8)

        # Right – recommendations
        right = tk.Frame(pane, bg=PANEL_BG,
                         highlightbackground="#2A2A2A", highlightthickness=1)
        right.pack(side="left", fill="both", expand=True, padx=(6, 0))
        _section_title(right, "Actionable Business Recommendations")
        self.rec_text = tk.Text(
            right, font=("Helvetica", 10),
            fg=FG_SECONDARY, bg=PANEL_BG,
            wrap="word", relief="flat", padx=16, pady=12,
        )
        self.rec_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    #  Footer 
    def _build_footer(self):
        foot = tk.Frame(self.content, bg=DARK_BG)
        foot.pack(fill="x", padx=30, pady=(4, 8))
        tk.Label(
            foot,
            text="Upload sales CSV in Dashboard -> return here -> click Refresh Analytics",
            font=("Helvetica", 8, "italic"), fg=FG_MUTED, bg=DARK_BG,
        ).pack(side="left")

    #  Data routing 
    def refresh_analytics(self):
        """Pull data from controller. Show empty state if no data uploaded yet."""
        data = getattr(self.controller, "shared_data", None)

        if data is None or (hasattr(data, "empty") and data.empty):
            self.data_source_lbl.config(text="● No data loaded", fg=FG_MUTED)
            self._show_empty_state()
            return

        self.data_source_lbl.config(text=f"● Live data ({len(data)} rows)",
                                    fg=ACCENT_GREEN)
        try:
            self._render_all(data)
        except Exception as exc:
            print(f"[PageTwo] refresh error: {exc}")

    def _show_empty_state(self):
        """Show a clear prompt when no CSV has been uploaded yet."""
        # Clear KPI row
        for w in self.kpi_row.winfo_children():
            w.destroy()

        # Clear charts
        for ax, canvas in [(self.daily_ax, self.daily_canvas),
                           (self.pie_ax,   self.pie_canvas),
                           (self.perf_ax,  self.perf_canvas),
                           (self.weekly_ax, self.weekly_canvas)]:
            ax.clear()
            ax.set_facecolor(PANEL_BG)
            ax.text(0.5, 0.5, "No data loaded",
                    transform=ax.transAxes,
                    ha="center", va="center",
                    fontsize=11, color=FG_MUTED)
            for spine in ax.spines.values():
                spine.set_color("#2A2A2A")
            ax.tick_params(colors=PANEL_BG)
            ax.set_xticks([])
            ax.set_yticks([])
            canvas.draw()

        # Clear tables and text boxes
        for w in self.perf_table_frame.winfo_children():
            w.destroy()
        for w in self.metrics_container.winfo_children():
            w.destroy()

        self.insights_text.delete(1.0, tk.END)
        self.rec_text.delete(1.0, tk.END)

        # Prompt message in KPI area
        msg = tk.Frame(self.kpi_row, bg=CARD_BG)
        msg.pack(expand=True, pady=30)

        tk.Label(msg,
                 text="No sales data loaded",
                 font=("Georgia", 16, "bold"),
                 fg=FG_MUTED, bg=CARD_BG).pack()

        tk.Label(msg,
                 text="Go to Dashboard -> Upload CSV -> return here and click Refresh Analytics",
                 font=("Helvetica", 10),
                 fg=FG_MUTED, bg=CARD_BG).pack(pady=8)

        tk.Label(msg,
                 text="All charts, KPIs and recommendations will populate automatically.",
                 font=("Helvetica", 9, "italic"),
                 fg="#444444", bg=CARD_BG).pack()

    def _render_all(self, data):
        data = data.copy()
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        product_cols = [c for c in data.columns if c != "Date"]

        self._render_kpis(data, product_cols)
        self._render_daily_chart(data, product_cols)
        self._render_pie(data, product_cols)
        self._render_performance(data, product_cols)
        self._render_trends(data, product_cols)
        self._render_recommendations(data, product_cols)

    def _render_kpis(self, data, product_cols):
        for w in self.kpi_row.winfo_children():
            w.destroy()

        total = sum(pd.to_numeric(data[c], errors="coerce").sum() for c in product_cols)
        avg   = total / max(len(data), 1)
        data["_tot"] = sum(pd.to_numeric(data[c], errors="coerce").fillna(0)
                           for c in product_cols)
        best  = data["_tot"].max()
        waste = self._waste_pct(data, product_cols)
        trend = self._overall_trend(data)

        _kpi_card(self.kpi_row, "Total Units Sold", f"{int(total):,}", "all products", ACCENT_PINK)
        _kpi_card(self.kpi_row, "Avg Daily Sales",  f"{avg:.0f}", "units/day", ACCENT_BLUE)
        _kpi_card(self.kpi_row, "Peak Day",         f"{int(best)}", "max units sold", ACCENT_GREEN)
        _kpi_card(self.kpi_row, "Demand Variability", f"{waste:.0f}%", "waste reduction target", ACCENT_AMB)
        _kpi_card(self.kpi_row, "Trend",            trend, "recent vs earlier", ACCENT_PURP)

    def _render_daily_chart(self, data, product_cols):
        self.daily_ax.clear()
        _styled_ax(self.daily_ax, PANEL_BG)

        data["_tot"] = sum(pd.to_numeric(data[c], errors="coerce").fillna(0)
                           for c in product_cols)
        last30 = data.tail(30)

        self.daily_ax.plot(last30["Date"], last30["_tot"],
                           color=ACCENT_PINK, linewidth=2, zorder=3)
        self.daily_ax.fill_between(last30["Date"], 0, last30["_tot"],
                                   color=ACCENT_PINK, alpha=0.12)
        # 7-day rolling avg
        roll = last30["_tot"].rolling(7, min_periods=1).mean()
        self.daily_ax.plot(last30["Date"], roll,
                           color=ACCENT_AMB, linewidth=1.2, linestyle="--",
                           label="7-day avg")
        self.daily_ax.legend(fontsize=7, framealpha=0.1,
                             facecolor=PANEL_BG, edgecolor="#333")
        self.daily_ax.set_ylabel("Units Sold", color=FG_SECONDARY, fontsize=8)
        self.daily_fig.autofmt_xdate(rotation=25)
        self.daily_fig.tight_layout()
        self.daily_canvas.draw()

    def _render_pie(self, data, product_cols):
        self.pie_ax.clear()
        self.pie_fig.patch.set_facecolor(PANEL_BG)

        labels, vals = [], []
        for col in product_cols[:6]:
            v = pd.to_numeric(data[col], errors="coerce").sum()
            if v > 0:
                labels.append(col)
                vals.append(v)

        if vals:
            wedges, texts, autotexts = self.pie_ax.pie(
                vals, labels=None,
                colors=CHART_COLORS[:len(vals)],
                autopct="%1.1f%%",
                startangle=140,
                pctdistance=0.8,
                wedgeprops={"linewidth": 1.5, "edgecolor": PANEL_BG},
            )
            for at in autotexts:
                at.set_fontsize(8)
                at.set_color(FG_PRIMARY)
            # Custom legend
            patches = [mpatches.Patch(color=CHART_COLORS[i], label=labels[i])
                       for i in range(len(labels))]
            self.pie_ax.legend(handles=patches, loc="lower center",
                               fontsize=7, framealpha=0.1,
                               facecolor=PANEL_BG, edgecolor="#333",
                               ncol=2, bbox_to_anchor=(0.5, -0.08))

        self.pie_fig.tight_layout()
        self.pie_canvas.draw()

    #  Performance rendering 
    def _render_performance(self, data, product_cols):
        # Clear existing
        for w in self.perf_table_frame.winfo_children():
            w.destroy()

        # Bar chart
        self.perf_ax.clear()
        _styled_ax(self.perf_ax, PANEL_BG)

        totals = [pd.to_numeric(data[c], errors="coerce").sum() for c in product_cols[:6]]
        x = range(len(product_cols[:6]))
        bars = self.perf_ax.bar(x, totals,
                                color=CHART_COLORS[:len(product_cols[:6])],
                                width=0.6, edgecolor=PANEL_BG, linewidth=1.2)
        self.perf_ax.set_xticks(list(x))
        self.perf_ax.set_xticklabels(product_cols[:6],
                                     color=FG_SECONDARY, fontsize=9, rotation=15)
        self.perf_ax.set_ylabel("Total Units Sold", color=FG_SECONDARY, fontsize=8)

        # Value labels on bars
        for bar, val in zip(bars, totals):
            self.perf_ax.text(bar.get_x() + bar.get_width() / 2,
                              bar.get_height() + 5,
                              f"{int(val):,}",
                              ha="center", va="bottom",
                              color=FG_SECONDARY, fontsize=8)
        self.perf_fig.tight_layout()
        self.perf_canvas.draw()

        # Data table
        headers = ["Product", "Total Sold", "Avg/Day", "Std Dev", "Trend", "Variability"]
        hdr_row = tk.Frame(self.perf_table_frame, bg="#2A2A2A")
        hdr_row.pack(fill="x", pady=(0, 2))
        for h in headers:
            tk.Label(hdr_row, text=h, font=("Helvetica", 9, "bold"),
                     fg=ACCENT_PINK, bg="#2A2A2A",
                     padx=14, pady=8).pack(side="left", expand=True, fill="x")

        for idx, col in enumerate(product_cols[:6]):
            series = pd.to_numeric(data[col], errors="coerce").dropna()
            if len(series) == 0:
                continue

            bg = CARD_BG if idx % 2 == 0 else "#242424"
            row = tk.Frame(self.perf_table_frame, bg=bg)
            row.pack(fill="x", pady=1)

            cv = (series.std() / series.mean() * 100) if series.mean() > 0 else 0
            trend = self._trend_arrow(series)

            vals = [col, f"{int(series.sum()):,}", f"{series.mean():.1f}",
                    f"{series.std():.1f}", trend, f"{cv:.1f}%"]
            colors = [FG_PRIMARY, FG_SECONDARY, FG_SECONDARY, FG_SECONDARY,
                      ACCENT_GREEN if "↑" in trend else (
                          "#E74C3C" if "↓" in trend else FG_MUTED),
                      ACCENT_AMB if cv > 30 else ACCENT_GREEN]

            for v, c in zip(vals, colors):
                tk.Label(row, text=v, font=("Helvetica", 9),
                         fg=c, bg=bg, padx=14, pady=7).pack(
                    side="left", expand=True, fill="x")

    #  Trends rendering 
    def _render_trends(self, data, product_cols):
        self.weekly_ax.clear()
        _styled_ax(self.weekly_ax, PANEL_BG)

        data["_tot"] = sum(pd.to_numeric(data[c], errors="coerce").fillna(0)
                           for c in product_cols)
        data["_dow"] = data["Date"].dt.dayofweek
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

        weekly = data.groupby("_dow")["_tot"].mean()

        if len(weekly) > 0:
            bar_colors = [ACCENT_PINK if i >= 5 else ACCENT_BLUE
                          for i in weekly.index]
            bars = self.weekly_ax.bar(
                range(len(weekly)), weekly.values,
                color=bar_colors, width=0.65,
                edgecolor=PANEL_BG, linewidth=1.5,
            )
            self.weekly_ax.set_xticks(range(len(weekly)))
            self.weekly_ax.set_xticklabels(
                [day_names[i] for i in weekly.index],
                color=FG_SECONDARY, fontsize=9,
            )
            self.weekly_ax.set_ylabel("Avg Units Sold", color=FG_SECONDARY, fontsize=8)

            # Peak annotation
            peak_idx = weekly.values.argmax()
            self.weekly_ax.annotate(
                "PEAK",
                xy=(peak_idx, weekly.values[peak_idx]),
                xytext=(peak_idx, weekly.values[peak_idx] * 1.08),
                fontsize=7, color=ACCENT_PINK, ha="center",
            )

            wkd_lbl = mpatches.Patch(color=ACCENT_BLUE, label="Weekday")
            wke_lbl = mpatches.Patch(color=ACCENT_PINK, label="Weekend")
            self.weekly_ax.legend(handles=[wkd_lbl, wke_lbl],
                                  fontsize=7, framealpha=0.1,
                                  facecolor=PANEL_BG, edgecolor="#333")

        self.weekly_fig.tight_layout()
        self.weekly_canvas.draw()

        # Insights text
        self.insights_text.delete(1.0, tk.END)
        self.insights_text.insert(1.0, self._generate_insights(data, product_cols))

    #  Recommendations rendering 
    def _render_recommendations(self, data, product_cols):
        # Clear metrics container
        for w in self.metrics_container.winfo_children():
            w.destroy()

        # Metrics table
        hdr_row = tk.Frame(self.metrics_container, bg="#2A2A2A")
        hdr_row.pack(fill="x", pady=(0, 4))
        for h in ["Product", "MAPE (%)", "MAE", "Data Points", "Status"]:
            tk.Label(hdr_row, text=h, font=("Helvetica", 9, "bold"),
                     fg=ACCENT_PINK, bg="#2A2A2A",
                     padx=10, pady=6).pack(side="left", expand=True, fill="x")

        if ML_AVAILABLE and self.forecaster:
            for idx, col in enumerate(product_cols[:4]):
                try:
                    series_df = self.forecaster.prepare_series(data, col)
                    if series_df is None:
                        continue
                    _, metrics = self.forecaster.sarima_forecast(
                        series_df, steps=7, product_name=col)

                    mape   = metrics.get("MAPE", 0)
                    mae    = metrics.get("MAE", 0)
                    points = metrics.get("Data_Points", 0)

                    if mape < 20:
                        status, sc = "Excellent", ACCENT_GREEN
                    elif mape < 40:
                        status, sc = "Good", ACCENT_AMB
                    elif mape < 55:
                        status, sc = "Acceptable", "#F39C12"
                    else:
                        status, sc = "Needs more data", "#E74C3C"

                    bg = CARD_BG if idx % 2 == 0 else "#242424"
                    row = tk.Frame(self.metrics_container, bg=bg)
                    row.pack(fill="x", pady=1)

                    for val, color in zip(
                        [col, f"{mape:.1f}", f"{mae:.1f}", str(points), status],
                        [FG_PRIMARY, FG_SECONDARY, FG_SECONDARY, FG_MUTED, sc],
                    ):
                        tk.Label(row, text=val, font=("Helvetica", 9),
                                 fg=color, bg=bg,
                                 padx=10, pady=6).pack(
                            side="left", expand=True, fill="x")

                except Exception as exc:
                    print(f"[PageTwo metrics] {col}: {exc}")
        else:
            tk.Label(self.metrics_container,
                     text=" ML module not available: Install statsmodels",
                     font=("Helvetica", 10), fg=ACCENT_AMB, bg=PANEL_BG,
                     pady=20).pack()

        # Recommendations text
        self.rec_text.delete(1.0, tk.END)
        self.rec_text.insert(1.0, self._generate_recommendations(data, product_cols))

    #  Analytics helpers 
    def _waste_pct(self, data, product_cols):
        cvs = []
        for col in product_cols:
            s = pd.to_numeric(data[col], errors="coerce").dropna()
            if len(s) >= 7 and s.mean() > 0:
                cvs.append(s.std() / s.mean() * 100)
        return min(40, np.mean(cvs)) if cvs else 0

    def _overall_trend(self, data):
        data["_tot"] = sum(pd.to_numeric(data[c], errors="coerce").fillna(0)
                           for c in [c for c in data.columns if c not in ("Date", "_tot")])
        if len(data) < 14:
            return "—"
        recent  = data["_tot"].tail(14).mean()
        earlier = data["_tot"].tail(28).head(14).mean() if len(data) >= 28 else \
                  data["_tot"].head(max(1, len(data) - 14)).mean()
        if recent > earlier * 1.08:
            return " Rising"
        elif recent < earlier * 0.92:
            return " Falling"
        return " Stable"

    def _trend_arrow(self, series):
        if len(series) < 14:
            return "—"
        recent  = series.tail(14).mean()
        earlier = series.tail(28).head(14).mean() if len(series) >= 28 else series.head(len(series) - 14).mean()
        if recent > earlier * 1.08:
            return " Up"
        elif recent < earlier * 0.92:
            return " Down"
        return " Stable"

    def _generate_insights(self, data, product_cols):
        lines = []
        data["_tot"] = sum(pd.to_numeric(data[c], errors="coerce").fillna(0) for c in product_cols)
        data["_day"] = data["Date"].dt.day_name()
        data["_dow"] = data["Date"].dt.dayofweek

        daily_avg = data.groupby("_day")["_tot"].mean()
        if len(daily_avg) > 0:
            best  = daily_avg.idxmax()
            worst = daily_avg.idxmin()
            lines.append(f"• Best sales day: {best} (avg {daily_avg.max():.0f} units)")
            lines.append(f"• Lowest sales day: {worst} (avg {daily_avg.min():.0f} units)")

        wknd = data[data["_dow"] >= 5]["_tot"].mean()
        wkdy = data[data["_dow"] < 5]["_tot"].mean()
        if wkdy > 0:
            diff = (wknd - wkdy) / wkdy * 100
            direction = "higher" if diff > 0 else "lower"
            lines.append(f"• Weekend demand is {abs(diff):.0f}% {direction} than weekdays")

        cv = (data["_tot"].std() / data["_tot"].mean() * 100) if data["_tot"].mean() > 0 else 0
        if cv > 35:
            lines.append(f"• Demand variability is HIGH ({cv:.0f}%), daily adjustments recommended")
        elif cv < 20:
            lines.append(f"• Demand is STABLE ({cv:.0f}%), well-suited to weekly batch planning")

        lines.append(f"• Dataset spans {len(data)} days of sales history")
        lines.append(f"• SARIMA model trained with weekly (7-day) seasonal cycle")
        lines.append(f"• ML forecasting: {'Active' if ML_AVAILABLE else 'Not available'}")

        return "\n".join(lines) if lines else "No insights available."

    def _generate_recommendations(self, data, product_cols):
        rec = []
        data = data.copy()
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        data["_tot"] = sum(pd.to_numeric(data[c], errors="coerce").fillna(0) for c in product_cols)
        data["_dow"] = data["Date"].dt.dayofweek

        wknd = data[data["_dow"] >= 5]["_tot"].mean()
        wkdy = data[data["_dow"] < 5]["_tot"].mean()

        rec.append("OPERATIONAL RECOMMENDATIONS\n")

        if wkdy > 0:
            diff = (wknd - wkdy) / wkdy * 100
            if diff > 20:
                rec.append(f"1. INCREASE WEEKEND PRODUCTION")
                rec.append(f"Weekend demand is {diff:.0f}% above weekday average.")
                rec.append(f"-> Prepare 20–30% additional inventory for Sat/Sun.\n")
            elif diff < -20:
                rec.append(f"1. REDUCE WEEKEND INVENTORY")
                rec.append(f"Weekday demand outpaces weekends by {abs(diff):.0f}%.")
                rec.append(f"-> Redirect weekend production to Mon–Fri.\n")
            else:
                rec.append(f"1. BALANCED SCHEDULE")
                rec.append(f"Weekend and weekday demand are broadly similar.")
                rec.append(f"-> Maintain consistent production levels.\n")

        rec.append("2. PRODUCT-LEVEL STRATEGY")
        for col in product_cols[:3]:
            s = pd.to_numeric(data[col], errors="coerce").dropna()
            if len(s) > 7:
                cv = (s.std() / s.mean() * 100) if s.mean() > 0 else 0
                if cv > 40:
                    rec.append(f"• {col}:HIGH variability ({cv:.0f}%), use daily SARIMA forecasts")
                elif cv < 20:
                    rec.append(f"• {col}:STABLE ({cv:.0f}%), weekly planning sufficient")
                else:
                    rec.append(f"• {col}:MODERATE variability, review bi-weekly")

        rec.append("")
        rec.append("3. WASTE REDUCTION ACTIONS")
        rec.append("• Review SARIMA forecasts each morning before production")
        rec.append("• Adjust batch sizes by day-of-week (use Trends tab)")
        rec.append("• Track actual vs forecast weekly to improve model accuracy")
        rec.append("• Target 15-25% waste reduction in first month")

        rec.append("")
        rec.append("4. DATA & MODEL QUALITY")
        days = len(data)
        if days < 60:
            rec.append(f"Only {days} days of data loaded, 60+ days strongly recommended")
        else:
            rec.append(f"Good data coverage ({days} days)")
        rec.append(f"SARIMA: {'Active' if ML_AVAILABLE else 'Not available (install statsmodels)'}")
        rec.append(f"Seasonal period: 7 days (captures weekly patterns)")

        return "\n".join(rec)