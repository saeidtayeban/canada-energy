"""
Energy EDA — Chapter 1: Canada's Energy Landscape
---------------------------------------------------
Runs exploratory data analysis on energy_clean.csv produced by
clean_energy_data.py

What it produces:
  1. Console report  — key stats, trends, rankings
  2. eda_report.txt  — same report saved to disk
  3. plots/          — folder of PNG charts ready for the portfolio

Usage:
  python eda_energy.py

Requires: pandas, matplotlib, seaborn
  pip install pandas matplotlib seaborn
"""

import sys
import os
from pathlib import Path
from io import StringIO

try:
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")           # non-interactive backend — works anywhere
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import seaborn as sns
except ImportError as e:
    sys.exit(f"Missing dependency: {e}\nRun: pip install pandas matplotlib seaborn")


# ── Configuration ─────────────────────────────────────────────────────────────

DATA_DIR   = Path(__file__).parent
INPUT_FILE = DATA_DIR / "energy_clean.csv"
PLOTS_DIR  = DATA_DIR / "plots"
REPORT_FILE = DATA_DIR / "eda_report.txt"

TREND_START = 2013      # 10-year window start
TREND_END   = 2023

# Clean energy categories to track for trend analysis
CLEAN_KEYWORDS = ["electric", "hydro", "wind", "solar", "nuclear", "renewable"]

# Seaborn style
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
PALETTE = sns.color_palette("tab10")


# ── Helpers ───────────────────────────────────────────────────────────────────

class Tee:
    """Write output to both stdout and a StringIO buffer."""
    def __init__(self):
        self.buf = StringIO()

    def write(self, msg):
        print(msg)
        self.buf.write(msg + "\n")

    def getvalue(self):
        return self.buf.getvalue()


log = Tee()

def section(title):
    log.write("\n" + "=" * 65)
    log.write(f"  {title}")
    log.write("=" * 65)

def subsection(title):
    log.write(f"\n── {title} {'─' * (60 - len(title))}")

def save_fig(fig, name):
    PLOTS_DIR.mkdir(exist_ok=True)
    path = PLOTS_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    log.write(f"  → Saved: plots/{name}.png")


# ── Load ──────────────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    if not INPUT_FILE.exists():
        sys.exit(
            f"\n  energy_clean.csv not found in {DATA_DIR}\n"
            "  Run clean_energy_data.py first.\n"
        )
    df = pd.read_csv(INPUT_FILE)
    required = {"Sheet", "Sector", "Metric", "Category", "Year", "Value"}
    missing = required - set(df.columns)
    if missing:
        sys.exit(f"  Missing columns in CSV: {missing}")
    df["Year"] = df["Year"].astype(int)
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    return df


# ── Analysis functions ────────────────────────────────────────────────────────

def overview(df: pd.DataFrame):
    section("1. DATASET OVERVIEW")
    log.write(f"  Rows          : {len(df):,}")
    log.write(f"  Year range    : {df['Year'].min()} → {df['Year'].max()}")
    log.write(f"  Sectors       : {sorted(df['Sector'].unique())}")
    log.write(f"  Metrics       : {sorted(df['Metric'].unique())}")
    log.write(f"  Categories    : {df['Category'].nunique()} unique")
    log.write(f"  Null values   : {df['Value'].isna().sum():,} "
               f"({df['Value'].isna().mean()*100:.1f}%)")


def sector_totals(df: pd.DataFrame):
    section("2. TOTAL ENERGY USE BY SECTOR (most recent year)")

    # Use Energy Use metric, most recent year
    latest = df["Year"].max()
    eu = df[(df["Metric"] == "Energy Use") & (df["Year"] == latest)]

    # Sum Value per Sector (avoid double-counting by excluding "Total" rows)
    eu_no_total = eu[~eu["Category"].str.lower().str.startswith("total")]
    by_sector = (
        eu_no_total.groupby("Sector")["Value"]
        .sum()
        .sort_values(ascending=False)
    )

    subsection(f"Energy Use — {latest} (excluding 'Total' rollup rows)")
    for sector, val in by_sector.items():
        log.write(f"  {sector:<30} {val:>12,.1f}")

    # Bar chart
    fig, ax = plt.subplots(figsize=(8, 4))
    by_sector.plot(kind="barh", ax=ax, color=PALETTE[:len(by_sector)])
    ax.set_title(f"Total Energy Use by Sector ({latest})", fontsize=13, pad=12)
    ax.set_xlabel("Energy Value")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    save_fig(fig, "01_sector_totals")

    return by_sector


def ghg_by_sector(df: pd.DataFrame):
    section("3. GHG EMISSIONS BY SECTOR")

    ghg = df[df["Metric"] == "GHG Emissions"]
    ghg_no_total = ghg[~ghg["Category"].str.lower().str.startswith("total")]

    # Annual totals per sector
    annual = (
        ghg_no_total.groupby(["Sector", "Year"])["Value"]
        .sum()
        .reset_index()
    )

    latest = annual["Year"].max()
    latest_ghg = annual[annual["Year"] == latest].sort_values("Value", ascending=False)

    subsection(f"GHG Emissions — {latest}")
    for _, row in latest_ghg.iterrows():
        log.write(f"  {row['Sector']:<30} {row['Value']:>12,.1f}")

    # Line chart: GHG trend per sector
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, sector in enumerate(annual["Sector"].unique()):
        sub = annual[annual["Sector"] == sector]
        ax.plot(sub["Year"], sub["Value"], marker="o", markersize=3,
                label=sector, color=PALETTE[i % len(PALETTE)])
    ax.set_title("GHG Emissions Trend by Sector (2000–2023)", fontsize=13, pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("GHG Emissions")
    ax.legend(fontsize=9)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(2))
    plt.tight_layout()
    save_fig(fig, "02_ghg_trend_by_sector")


def top_categories(df: pd.DataFrame):
    section("4. TOP 10 CATEGORIES BY ENERGY USE")

    latest = df["Year"].max()
    eu = df[
        (df["Metric"] == "Energy Use") &
        (df["Year"] == latest) &
        (~df["Category"].str.lower().str.startswith("total"))
    ]

    top10 = eu.groupby("Category")["Value"].sum().nlargest(10)

    subsection(f"Top 10 categories — {latest}")
    for i, (cat, val) in enumerate(top10.items(), 1):
        log.write(f"  {i:>2}. {cat:<40} {val:>10,.1f}")

    fig, ax = plt.subplots(figsize=(9, 5))
    top10.sort_values().plot(kind="barh", ax=ax, color=sns.color_palette("Blues_r", 10))
    ax.set_title(f"Top 10 Energy-Use Categories ({latest})", fontsize=13, pad=12)
    ax.set_xlabel("Energy Value")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    save_fig(fig, "03_top10_categories")


def ten_year_trend(df: pd.DataFrame):
    section(f"5. 10-YEAR TREND ({TREND_START}–{TREND_END})")

    trend = df[
        (df["Metric"] == "Energy Use") &
        (df["Year"].between(TREND_START, TREND_END)) &
        (~df["Category"].str.lower().str.startswith("total"))
    ]

    annual_total = trend.groupby("Year")["Value"].sum().reset_index()

    # Growth calculation
    base  = annual_total.loc[annual_total["Year"] == TREND_START, "Value"].values
    end   = annual_total.loc[annual_total["Year"] == TREND_END,   "Value"].values

    if len(base) and len(end):
        growth = (end[0] - base[0]) / base[0] * 100
        log.write(f"\n  Total energy use {TREND_START}→{TREND_END}: "
                   f"{growth:+.1f}%")

    # Per-sector trend
    sector_trend = (
        trend.groupby(["Sector", "Year"])["Value"]
        .sum()
        .reset_index()
    )

    subsection("Sector growth rates over the decade")
    for sector in sector_trend["Sector"].unique():
        sub = sector_trend[sector_trend["Sector"] == sector]
        s_base = sub.loc[sub["Year"] == TREND_START, "Value"].values
        s_end  = sub.loc[sub["Year"] == TREND_END,   "Value"].values
        if len(s_base) and len(s_end) and s_base[0] != 0:
            g = (s_end[0] - s_base[0]) / s_base[0] * 100
            direction = "↑" if g > 0 else "↓"
            log.write(f"  {sector:<30} {direction} {abs(g):.1f}%")

    # Line chart
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = iter(PALETTE)
    for sector in sector_trend["Sector"].unique():
        sub = sector_trend[sector_trend["Sector"] == sector]
        ax.plot(sub["Year"], sub["Value"], marker="o", markersize=4,
                label=sector, color=next(colors))
    ax.set_title(f"10-Year Energy Use Trend by Sector ({TREND_START}–{TREND_END})",
                 fontsize=13, pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Energy Value")
    ax.legend(fontsize=9)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    save_fig(fig, "04_ten_year_trend")


def clean_energy_share(df: pd.DataFrame):
    section("6. CLEAN ENERGY CATEGORIES — TREND")

    eu = df[
        (df["Metric"] == "Energy Use") &
        (df["Year"].between(TREND_START, TREND_END))
    ]

    # Tag clean vs non-clean
    def is_clean(cat):
        cat_lower = str(cat).lower()
        return any(kw in cat_lower for kw in CLEAN_KEYWORDS)

    eu = eu.copy()
    eu["IsClean"] = eu["Category"].apply(is_clean)

    annual_split = (
        eu.groupby(["Year", "IsClean"])["Value"]
        .sum()
        .reset_index()
    )
    annual_total_val = eu.groupby("Year")["Value"].sum().reset_index()
    annual_total_val.rename(columns={"Value": "Total"}, inplace=True)

    clean_only = annual_split[annual_split["IsClean"]].merge(annual_total_val, on="Year")
    clean_only["CleanShare"] = clean_only["Value"] / clean_only["Total"] * 100

    if not clean_only.empty:
        subsection("Clean energy share (%)")
        for _, row in clean_only.iterrows():
            bar = "█" * int(row["CleanShare"] / 2)
            log.write(f"  {int(row['Year'])}  {bar:<50}  {row['CleanShare']:.1f}%")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.fill_between(clean_only["Year"], clean_only["CleanShare"],
                        alpha=0.3, color="steelblue")
        ax.plot(clean_only["Year"], clean_only["CleanShare"],
                marker="o", color="steelblue", linewidth=2)
        ax.set_title(f"Clean Energy Share of Transportation ({TREND_START}–{TREND_END})",
                     fontsize=13, pad=12)
        ax.set_xlabel("Year")
        ax.set_ylabel("Share (%)")
        ax.set_ylim(0, 100)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
        plt.xticks(rotation=45)
        plt.tight_layout()
        save_fig(fig, "05_clean_energy_share")
    else:
        log.write("  No clean energy categories detected with current keywords.")
        log.write(f"  Keywords used: {CLEAN_KEYWORDS}")
        log.write("  Check your category names and adjust CLEAN_KEYWORDS if needed.")


def ghg_intensity(df: pd.DataFrame):
    section("7. GHG INTENSITY TREND")

    intensity = df[
        (df["Metric"] == "Intensity") &
        (df["Year"].between(TREND_START, TREND_END)) &
        (~df["Category"].str.lower().str.startswith("total"))
    ]

    if intensity.empty:
        log.write("  No Intensity rows found — skipping.")
        return

    annual = intensity.groupby(["Sector", "Year"])["Value"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = iter(PALETTE)
    for sector in annual["Sector"].unique():
        sub = annual[annual["Sector"] == sector]
        ax.plot(sub["Year"], sub["Value"], marker="o", markersize=4,
                label=sector, color=next(colors))
    ax.set_title(f"Average GHG Intensity by Sector ({TREND_START}–{TREND_END})",
                 fontsize=13, pad=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Intensity (avg)")
    ax.legend(fontsize=9)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(1))
    plt.xticks(rotation=45)
    plt.tight_layout()
    save_fig(fig, "06_ghg_intensity_trend")

    subsection("Average intensity change over decade")
    for sector in annual["Sector"].unique():
        sub = annual[annual["Sector"] == sector]
        s_base = sub.loc[sub["Year"] == TREND_START, "Value"].values
        s_end  = sub.loc[sub["Year"] == TREND_END,   "Value"].values
        if len(s_base) and len(s_end) and s_base[0] != 0:
            g = (s_end[0] - s_base[0]) / s_base[0] * 100
            direction = "↑" if g > 0 else "↓"
            log.write(f"  {sector:<30} {direction} {abs(g):.1f}%")


def chapter2_bridge(df: pd.DataFrame):
    section("8. CHAPTER 2 BRIDGE — TRANSPORTATION BASELINE")

    transport = df[
        (df["Sector"].str.contains("Transport", case=False)) &
        (df["Metric"] == "Energy Use") &
        (~df["Category"].str.lower().str.startswith("total"))
    ]

    if transport.empty:
        log.write("  No transportation rows found.")
        return

    latest = transport["Year"].max()
    t_latest = transport[transport["Year"] == latest]
    t_totals = t_latest.groupby("Category")["Value"].sum().sort_values(ascending=False)

    subsection(f"Transportation energy by category — {latest}")
    for cat, val in t_totals.items():
        log.write(f"  {cat:<40} {val:>10,.1f}")

    log.write(f"\n  ┌─ Chapter 2 setup ─────────────────────────────────────────┐")
    log.write(f"  │ This is your EV demand baseline.                           │")
    log.write(f"  │ In Chapter 2 you will model what happens to these          │")
    log.write(f"  │ numbers as gasoline/diesel vehicles are replaced by EVs.   │")
    log.write(f"  │                                                             │")
    log.write(f"  │ Key categories to track into Chapter 2:                    │")

    road_cats = [c for c in t_totals.index
                 if any(kw in c.lower() for kw in
                        ["car", "truck", "light", "heavy", "vehicle", "road", "bus"])]
    for cat in road_cats[:6]:
        log.write(f"  │   • {cat:<55}│")

    log.write(f"  └─────────────────────────────────────────────────────────────┘")

    # Bar chart
    fig, ax = plt.subplots(figsize=(9, 5))
    t_totals.head(12).sort_values().plot(
        kind="barh", ax=ax,
        color=sns.color_palette("Greens_r", min(12, len(t_totals)))
    )
    ax.set_title(f"Transportation Energy Baseline — {latest}\n(Chapter 2 starting point)",
                 fontsize=13, pad=12)
    ax.set_xlabel("Energy Value")
    ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    plt.tight_layout()
    save_fig(fig, "07_chapter2_transport_baseline")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    section("CANADA ENERGY EDA — Chapter 1")
    log.write(f"  Input : {INPUT_FILE}")
    log.write(f"  Output: {PLOTS_DIR}/  +  {REPORT_FILE.name}")

    df = load_data()

    overview(df)
    sector_totals(df)
    ghg_by_sector(df)
    top_categories(df)
    ten_year_trend(df)
    clean_energy_share(df)
    ghg_intensity(df)
    chapter2_bridge(df)

    section("DONE")
    log.write(f"  Plots saved to: {PLOTS_DIR}")
    log.write(f"  Charts produced:")
    for f in sorted(PLOTS_DIR.glob("*.png")):
        log.write(f"    • {f.name}")

    log.write(f"\n  Next step → Week 4: turn these charts into")
    log.write(f"  the visual portfolio piece and write the technical summary.")

    # Save report
    REPORT_FILE.write_text(log.getvalue())
    print(f"\n  Report saved to: {REPORT_FILE.name}")


if __name__ == "__main__":
    main()
