"""
Energy Data Cleaner — Chapter 1: Canada's Energy Landscape
-----------------------------------------------------------
Cleans the NRCan Transportation Energy Use spreadsheet.

Handles sheets: Transportation3, Passenger1-4, Freight1-4, Electricity1-2

What it does:
  1. Finds the real header row (where years 2000-2023 live)
  2. Strips blank rows at top and footnotes at bottom
  3. Melts wide → long (one row per category + year)
  4. Tags each row with its source sheet and sector
  5. Outputs a single clean CSV ready for EDA

Usage:
  1. Place your NRCan Excel file in the same folder as this script
  2. Run: python clean_energy_data.py
  3. Output: energy_clean.csv

"""

import sys
import re
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("pandas not installed. Run: pip install pandas openpyxl")

try:
    import openpyxl  # noqa: F401
except ImportError:
    sys.exit("openpyxl not installed. Run: pip install openpyxl")


# ── Configuration ─────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent
OUTPUT_FILE = DATA_DIR / "energy_clean.csv"

# Sheets to process — in order
TARGET_SHEETS = [
    "Transportation3",
    "Passenger1", "Passenger2", "Passenger3", "Passenger4",
    "Freight1",   "Freight2",   "Freight3",   "Freight4",
    "Electricity1", "Electricity2",
]

# Year range we expect to find
YEAR_START = 2000
YEAR_END   = 2023
EXPECTED_YEARS = set(range(YEAR_START, YEAR_END + 1))

# Sector mapping: sheet prefix → clean sector label
SECTOR_MAP = {
    "Transportation": "Total Transportation",
    "Passenger":      "Passenger",
    "Freight":        "Freight",
    "Electricity":    "Electricity",
}

# Strings that signal a footnote / metadata row (case-insensitive)
FOOTNOTE_SIGNALS = [
    "source", "note", "footnote", "definition", "data from",
    "statistics canada", "natural resources", "nrcan", "copyright",
    "table", "figure", "see ", "refer ", "http", "www.",
    "energy efficiency", "office of", "extracted", "published",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def find_header_row(df: pd.DataFrame) -> int | None:
    """
    Scan every row for one that contains at least 10 values
    that look like years in [2000, 2023]. Return the row index.
    """
    for idx, row in df.iterrows():
        year_hits = sum(
            1 for val in row
            if _is_year(val)
        )
        if year_hits >= 10:
            return idx
    return None


def _is_year(val) -> bool:
    """Return True if val looks like a year between 2000 and 2023."""
    try:
        return YEAR_START <= int(float(str(val))) <= YEAR_END
    except (ValueError, TypeError):
        return False


def _is_footnote_row(row: pd.Series) -> bool:
    """Return True if a row looks like a footnote or metadata line."""
    text = " ".join(str(v) for v in row if pd.notna(v)).lower()
    if not text.strip():
        return True  # blank row
    return any(sig in text for sig in FOOTNOTE_SIGNALS)


def _is_blank_row(row: pd.Series) -> bool:
    return row.isna().all() or row.astype(str).str.strip().eq("").all()


def infer_sector(sheet_name: str) -> str:
    for prefix, label in SECTOR_MAP.items():
        if sheet_name.startswith(prefix):
            return label
    return sheet_name


def infer_metric(sheet_name: str) -> str:
    """
    NRCan sheet numbering convention (approximate):
      *1 → Energy use (petajoules or similar)
      *2 → Intensity
      *3 → GHG emissions
      *4 → Price / other
    Transportation3 is GHG for the whole transport sector.
    """
    match = re.search(r"(\d)$", sheet_name)
    if not match:
        return "Unknown"
    n = int(match.group(1))
    mapping = {
        1: "Energy Use",
        2: "Intensity",
        3: "GHG Emissions",
        4: "Price / Other",
    }
    # Transportation3 = GHG for the combined sheet
    if sheet_name == "Transportation3":
        return "GHG Emissions"
    return mapping.get(n, f"Metric {n}")


def clean_sheet(df_raw: pd.DataFrame, sheet_name: str) -> pd.DataFrame | None:
    """
    Full cleaning pipeline for one sheet.
    Returns a long-format DataFrame or None if the sheet can't be parsed.
    """
    print(f"  Processing: {sheet_name}")

    # ── Step 1: Find the header row ────────────────────────────────────────
    header_idx = find_header_row(df_raw)
    if header_idx is None:
        print(f"    ✗ Could not find year headers — skipping.")
        return None
    print(f"    ✓ Header row found at index {header_idx}")

    # ── Step 2: Split into header + data ──────────────────────────────────
    year_row  = df_raw.iloc[header_idx]
    data_rows = df_raw.iloc[header_idx + 1:].copy()
    data_rows.reset_index(drop=True, inplace=True)

    # ── Step 3: Build new column names ────────────────────────────────────
    # Col 0 → ignore (usually row numbers or blank)
    # Col 1 → "Category"
    # Cols with year values → the year as int
    # Last col → "Growth" (if it exists and isn't a year)
    new_cols = []
    for i, val in enumerate(year_row):
        if i == 0:
            new_cols.append("_drop")
        elif i == 1:
            new_cols.append("Category")
        elif _is_year(val):
            new_cols.append(int(float(str(val))))
        else:
            # Could be a growth/change column at the end
            label = str(val).strip()
            new_cols.append(label if label and label != "nan" else f"_col{i}")

    data_rows.columns = new_cols

    # ── Step 4: Drop junk columns ──────────────────────────────────────────
    drop_cols = [c for c in data_rows.columns
                 if str(c).startswith("_drop") or str(c).startswith("_col")]
    data_rows.drop(columns=drop_cols, inplace=True, errors="ignore")

    # ── Step 5: Drop blank and footnote rows ──────────────────────────────
    before = len(data_rows)
    data_rows = data_rows[~data_rows.apply(_is_blank_row, axis=1)]
    data_rows = data_rows[~data_rows.apply(_is_footnote_row, axis=1)]
    after = len(data_rows)
    print(f"    ✓ Dropped {before - after} blank/footnote rows "
          f"({after} rows remain)")

    if data_rows.empty:
        print(f"    ✗ No data rows left after cleaning — skipping.")
        return None

    # ── Step 6: Keep only year columns + Category ─────────────────────────
    year_cols = [c for c in data_rows.columns
                 if isinstance(c, int) and YEAR_START <= c <= YEAR_END]
    keep_cols = ["Category"] + year_cols

    # Add growth column if it exists
    growth_cols = [c for c in data_rows.columns
                   if isinstance(c, str) and c not in ("Category",)
                   and not str(c).startswith("_")]
    keep_cols += growth_cols

    data_rows = data_rows[keep_cols].copy()

    # ── Step 7: Clean the Category column ────────────────────────────────
    data_rows["Category"] = (
        data_rows["Category"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )
    # Drop rows where Category is blank or nan
    data_rows = data_rows[
        data_rows["Category"].notna() &
        (data_rows["Category"] != "") &
        (data_rows["Category"] != "nan")
    ]

    # ── Step 8: Melt wide → long ──────────────────────────────────────────
    id_vars = ["Category"] + growth_cols
    long = data_rows.melt(
        id_vars=id_vars,
        value_vars=year_cols,
        var_name="Year",
        value_name="Value",
    )

    # ── Step 9: Coerce Value to numeric ──────────────────────────────────
    long["Value"] = pd.to_numeric(long["Value"], errors="coerce")
    long["Year"]  = long["Year"].astype(int)

    # ── Step 10: Tag with source metadata ────────────────────────────────
    long.insert(0, "Sheet",  sheet_name)
    long.insert(1, "Sector", infer_sector(sheet_name))
    long.insert(2, "Metric", infer_metric(sheet_name))

    null_pct = long["Value"].isna().mean() * 100
    print(f"    ✓ Melted → {len(long):,} rows  |  "
          f"{null_pct:.1f}% null values in Value column")

    return long


def find_excel_file() -> Path | None:
    """Find the first .xlsx or .xls file in DATA_DIR."""
    for ext in (".xlsx", ".xls"):
        matches = list(DATA_DIR.glob(f"*{ext}"))
        # Skip temp files
        matches = [m for m in matches if not m.name.startswith("~")]
        if matches:
            return matches[0]
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("  NRCan Transportation Energy — Data Cleaner")
    print("=" * 70)

    # ── Locate file ───────────────────────────────────────────────────────
    excel_path = find_excel_file()
    if excel_path is None:
        sys.exit(
            "\n  No Excel file found in this directory.\n"
            "  Place your NRCan spreadsheet here and re-run.\n"
        )

    print(f"\n  File: {excel_path.name}")
    print(f"  Size: {excel_path.stat().st_size / 1024:.1f} KB\n")

    # ── Load workbook ─────────────────────────────────────────────────────
    xl = pd.ExcelFile(excel_path)
    available = xl.sheet_names
    print(f"  Available sheets: {available}\n")

    # Filter to sheets we actually want
    sheets_to_process = [s for s in TARGET_SHEETS if s in available]
    skipped = [s for s in TARGET_SHEETS if s not in available]

    if skipped:
        print(f"  Note: These sheets were not found and will be skipped:")
        for s in skipped:
            print(f"    • {s}")
        print()

    if not sheets_to_process:
        sys.exit(
            "  None of the expected sheets were found.\n"
            "  Check that this is the correct NRCan file.\n"
        )

    # ── Process each sheet ────────────────────────────────────────────────
    print("-" * 70)
    cleaned_frames = []

    for sheet_name in sheets_to_process:
        df_raw = xl.parse(sheet_name, header=None)
        result = clean_sheet(df_raw, sheet_name)
        if result is not None:
            cleaned_frames.append(result)
        print()

    # ── Combine ───────────────────────────────────────────────────────────
    if not cleaned_frames:
        sys.exit("  No sheets were successfully cleaned. Exiting.")

    print("-" * 70)
    combined = pd.concat(cleaned_frames, ignore_index=True)

    # ── Final sort & tidy ─────────────────────────────────────────────────
    combined.sort_values(
        ["Sector", "Metric", "Category", "Year"],
        inplace=True
    )
    combined.reset_index(drop=True, inplace=True)

    # ── Output ────────────────────────────────────────────────────────────
    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"\n  Output: {OUTPUT_FILE.name}")
    print(f"  Shape:  {combined.shape[0]:,} rows × {combined.shape[1]} columns")
    print(f"  Columns: {list(combined.columns)}")
    print(f"\n  Sector breakdown:")
    for sector, count in combined.groupby("Sector")["Category"].nunique().items():
        print(f"    {sector:<25} {count} unique categories")

    print(f"\n  Metric breakdown:")
    for metric, count in combined.groupby("Metric").size().items():
        print(f"    {metric:<25} {count:,} rows")

    null_total = combined["Value"].isna().sum()
    null_pct   = null_total / len(combined) * 100
    print(f"\n  Null values in Value column: {null_total:,} ({null_pct:.1f}%)")

    print(f"\n  Sample (first 10 rows of clean data):")
    print(combined.head(10).to_string(index=False))

    print("\n" + "=" * 70)
    print("  Done. energy_clean.csv is ready for Week 3 EDA.")
    print("=" * 70)


if __name__ == "__main__":
    main()
