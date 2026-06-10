"""
Energy Data Inspector — Chapter 1: Canada's Energy Landscape
-------------------------------------------------------------
Drop your StatCan and NRCan files into the same folder as this script,
then run:  python inspect_energy_data.py

Supports: .csv, .xlsx, .xls
Outputs a full structural report for every file it finds.
"""

import os
import sys
import textwrap
from pathlib import Path

# ── Dependencies ─────────────────────────────────────────────────────────────

try:
    import pandas as pd
except ImportError:
    sys.exit(
        "pandas is not installed.\n"
        "Run:  pip install pandas openpyxl\n"
        "Then re-run this script."
    )

try:
    import openpyxl  # noqa: F401  — needed for .xlsx support
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


# ── Configuration ─────────────────────────────────────────────────────────────

# Where to look for data files.
# Default: same directory as this script.
DATA_DIR = Path(__file__).parent

# File patterns to scan.
EXTENSIONS = [".csv", ".xlsx", ".xls"]

# How many rows to preview.
PREVIEW_ROWS = 5

# How many characters wide to wrap text output.
LINE_WIDTH = 80


# ── Helpers ───────────────────────────────────────────────────────────────────

def separator(char="─", width=LINE_WIDTH):
    print(char * width)

def heading(text, char="═"):
    separator(char)
    print(f"  {text}")
    separator(char)

def subheading(text):
    print(f"\n{'─' * 40}")
    print(f"  {text}")
    print(f"{'─' * 40}")

def wrap(text, indent=4):
    prefix = " " * indent
    return textwrap.fill(text, width=LINE_WIDTH, initial_indent=prefix,
                         subsequent_indent=prefix)


def load_file(path: Path) -> dict:
    """
    Load a CSV or Excel file and return a dict with the DataFrame(s).
    Excel files may have multiple sheets — each becomes its own entry.
    Returns: { sheet_name: DataFrame }
    """
    ext = path.suffix.lower()
    results = {}

    try:
        if ext == ".csv":
            # Try UTF-8 first, fall back to latin-1 (common in StatCan exports)
            for encoding in ("utf-8", "latin-1", "cp1252"):
                try:
                    df = pd.read_csv(path, encoding=encoding, low_memory=False)
                    results["(CSV)"] = df
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode CSV — tried utf-8, latin-1, cp1252.")

        elif ext in (".xlsx", ".xls"):
            if not OPENPYXL_AVAILABLE and ext == ".xlsx":
                raise ImportError(
                    "openpyxl is required for .xlsx files.\n"
                    "Run:  pip install openpyxl"
                )
            xl = pd.ExcelFile(path)
            for sheet in xl.sheet_names:
                df = xl.parse(sheet, header=0)
                results[sheet] = df

        else:
            raise ValueError(f"Unsupported extension: {ext}")

    except Exception as e:
        results["__error__"] = str(e)

    return results


def infer_date_columns(df: pd.DataFrame) -> list[str]:
    """Return column names that look like they contain dates."""
    candidates = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(kw in col_lower for kw in ("year", "date", "month", "period", "time")):
            candidates.append(col)
    return candidates


def summarise_column(series: pd.Series) -> str:
    """One-line summary of a column's dtype and value distribution."""
    dtype = series.dtype
    n_null = series.isna().sum()
    n_unique = series.nunique(dropna=True)

    if pd.api.types.is_numeric_dtype(series):
        lo, hi = series.min(), series.max()
        return (f"numeric  |  range [{lo:,.2f} → {hi:,.2f}]  |  "
                f"{n_null} nulls  |  {n_unique} unique")
    elif pd.api.types.is_datetime64_any_dtype(series):
        lo, hi = series.min(), series.max()
        return f"datetime  |  [{lo} → {hi}]  |  {n_null} nulls"
    else:
        top = series.dropna().value_counts().head(3).index.tolist()
        top_str = ", ".join(f'"{v}"' for v in top)
        return (f"text  |  {n_unique} unique  |  {n_null} nulls  |  "
                f"top: {top_str}")


def inspect_sheet(name: str, df: pd.DataFrame):
    """Print the full structural report for one DataFrame."""
    subheading(f"Sheet / table: {name}")

    # ── Shape ──────────────────────────────────────────────────────────────
    print(f"\n  Shape         {df.shape[0]:,} rows  ×  {df.shape[1]} columns")
    print(f"  Memory        {df.memory_usage(deep=True).sum() / 1024:.1f} KB")

    # ── Date range ─────────────────────────────────────────────────────────
    date_cols = infer_date_columns(df)
    if date_cols:
        print(f"\n  Likely date columns: {date_cols}")
        for col in date_cols:
            vals = df[col].dropna().unique()
            try:
                parsed = pd.to_datetime(vals, errors="coerce")
                valid = parsed.dropna()
                if len(valid) > 0:
                    print(f"    {col}: {valid.min().year} → {valid.max().year}  "
                          f"({len(valid):,} parseable values)")
                else:
                    # Raw values instead
                    sample = sorted(vals)[:5]
                    print(f"    {col}: (unparseable) sample → {sample}")
            except Exception:
                pass

    # ── Missing data ───────────────────────────────────────────────────────
    null_pct = (df.isna().sum() / len(df) * 100).sort_values(ascending=False)
    high_null = null_pct[null_pct > 10]
    print(f"\n  Missing data  {df.isna().sum().sum():,} total nulls  "
          f"({df.isna().mean().mean() * 100:.1f}% overall)")
    if not high_null.empty:
        print("  Columns with >10% nulls:")
        for col, pct in high_null.items():
            print(f"    {str(col):<40}  {pct:.1f}%")

    # ── Column catalogue ───────────────────────────────────────────────────
    print(f"\n  {'Column':<35}  {'Summary'}")
    print(f"  {'─' * 35}  {'─' * 38}")
    for col in df.columns:
        summary = summarise_column(df[col])
        col_str = str(col)
        if len(col_str) > 34:
            col_str = col_str[:31] + "..."
        print(f"  {col_str:<35}  {summary}")

    # ── Units sniff ────────────────────────────────────────────────────────
    unit_keywords = ["unit", "uom", "measure", "petajoule", "gwh", "mwh",
                     "twh", "gigawatt", "megawatt", "kwh"]
    unit_cols = [c for c in df.columns
                 if any(kw in str(c).lower() for kw in unit_keywords)]
    if unit_cols:
        print(f"\n  Unit-related columns detected: {unit_cols}")
        for col in unit_cols:
            unique_units = df[col].dropna().unique()[:10]
            print(f"    {col}: {list(unique_units)}")

    # ── Geography sniff ────────────────────────────────────────────────────
    geo_keywords = ["prov", "province", "region", "geo", "location",
                    "geography", "area"]
    geo_cols = [c for c in df.columns
                if any(kw in str(c).lower() for kw in geo_keywords)]
    if geo_cols:
        print(f"\n  Geography columns detected: {geo_cols}")
        for col in geo_cols:
            vals = df[col].dropna().unique()
            print(f"    {col}: {list(vals[:12])}"
                  + (" ..." if len(vals) > 12 else ""))

    # ── Sector sniff ───────────────────────────────────────────────────────
    sector_keywords = ["sector", "industry", "type", "source", "fuel",
                       "end use", "category"]
    sector_cols = [c for c in df.columns
                   if any(kw in str(c).lower() for kw in sector_keywords)]
    if sector_cols:
        print(f"\n  Sector / category columns detected: {sector_cols}")
        for col in sector_cols:
            vals = df[col].dropna().unique()
            print(f"    {col}: {list(vals[:12])}"
                  + (" ..." if len(vals) > 12 else ""))

    # ── Preview ────────────────────────────────────────────────────────────
    print(f"\n  First {PREVIEW_ROWS} rows:")
    try:
        preview = df.head(PREVIEW_ROWS).to_string(
            index=False, max_cols=8, max_colwidth=20
        )
        for line in preview.split("\n"):
            print(f"    {line}")
    except Exception as e:
        print(f"    (preview error: {e})")

    # ── Week 2 notes ───────────────────────────────────────────────────────
    print(f"\n  ┌─ Week 2 flags ───────────────────────────────────────────┐")
    flags = []

    if df.isna().sum().sum() > 0:
        flags.append("→ Nulls present — decide fill strategy (forward-fill, "
                     "interpolate, or drop)")
    if unit_cols:
        flags.append("→ Unit column found — standardize to TWh before merging")
    if len(df.columns) > 30:
        flags.append("→ Wide table — consider melting to long format for "
                     "easier filtering")
    if not date_cols:
        flags.append("→ No obvious date column — check if year is encoded "
                     "in column headers (wide format)")
    if not geo_cols:
        flags.append("→ No geography column — may need to tag province "
                     "manually during merge")

    if not flags:
        flags.append("→ Structure looks clean — proceed to merge and filter.")

    for f in flags:
        print(wrap(f, indent=4))
    print(f"  └──────────────────────────────────────────────────────────┘")


def inspect_file(path: Path):
    """Top-level handler for one file."""
    heading(f"FILE: {path.name}")
    print(f"  Path:  {path}")
    print(f"  Size:  {path.stat().st_size / 1024:.1f} KB")

    sheets = load_file(path)

    if "__error__" in sheets:
        print(f"\n  ✗ Failed to load: {sheets['__error__']}")
        return

    print(f"  Sheets / tables found: {list(sheets.keys())}")

    for name, df in sheets.items():
        if df is None or df.empty:
            print(f"\n  Sheet '{name}' is empty — skipping.")
            continue
        inspect_sheet(name, df)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    heading("Canada Energy Data Inspector", char="═")
    print(f"  Scanning: {DATA_DIR}")
    print(f"  Looking for: {EXTENSIONS}")
    separator()

    files = sorted(
        f for f in DATA_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in EXTENSIONS
        and not f.name.startswith("~")          # skip Excel temp files
        and not f.name.startswith(".")          # skip hidden files
        and f.name != Path(__file__).name       # skip this script itself
    )

    if not files:
        print(
            "\n  No data files found.\n"
            "\n  Place your StatCan / NRCan files in the same folder as this\n"
            "  script, then re-run.\n"
            "\n  Expected files:\n"
            "    • StatCan table 25-10-0015-01 (CSV download)\n"
            "    • NRCan Comprehensive Energy Use Database (Excel or CSV)\n"
        )
        return

    print(f"\n  Found {len(files)} file(s):\n")
    for f in files:
        print(f"    {f.name}  ({f.stat().st_size / 1024:.1f} KB)")

    print()
    for path in files:
        inspect_file(path)
        print()

    separator("═")
    print("  Inspection complete.")
    print("  Review the Week 2 flags above before writing your cleaning script.")
    separator("═")


if __name__ == "__main__":
    main()
