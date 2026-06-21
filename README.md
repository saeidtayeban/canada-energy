# Canada Energy — How Does Canada Power Its Physical Future?

> A 4-chapter data analysis portfolio grounded in real infrastructure:
> power grids, vehicles, and cities. Built with Python and public Canadian government data.

**[→ View Chapter 1 Interactive Report](canada_energy_chapter1.html)**
**[→ View Chapter 2 Interactive Report](canada_energy_chapter2.html)**

---

## The Question

Canada is simultaneously cleaning its electricity grid and growing its road freight load. These two trajectories are on a collision course. This project answers: *what does the data actually show, and what happens when EVs connect these two systems?*

The analysis is structured as an expanding spiral — starting with the macro view of what Canada has today, zooming in on how EVs shift that baseline, and using machine learning to model the resulting stress on the grid.

---

## Project Structure

```
canada-energy/
│
├── data/
│   ├── raw/                        # Source files from StatCan + NRCan (not committed)
│   │   ├── README.md               # Download instructions for all source files
│   │   └── ev/
│   │       ├── vehicle_registrations_by_type_fuel_annual/
│   │       │   ├── 23100308.csv
│   │       │   └── 23100308_MetaData.csv
│   │       └── new_vehicle_registrations_quarterly_geo/
│   │           ├── 20100025.csv
│   │           └── 20100025_MetaData.csv
│   │
│   └── cleaned/                    # Processed, analysis-ready data (committed)
│       ├── README.md               # Full schema documentation
│       ├── energy_clean.csv        # 6,048 rows × 7 cols — Ch.1 long-format unified table
│       ├── ev_annual_clean.csv     # 960 rows × 6 cols — province × segment × fuel, 2017–2024
│       ├── ev_quarterly_clean.csv  # 4,144 rows × 6 cols — quarterly new sales by province
│       ├── ev_zev_mandates.csv     # 24 rows × 4 cols — dual-scenario mandate reference
│       ├── ev_demand_projections.csv  # EV fleet + kWh demand, 2024–2035, both scenarios
│       └── grid_stress_scores.csv  # Province × year stress scores, both scenarios
│
├── scripts/
│   ├── 01_inspect.py               # Ch.1 — structural audit of raw source files
│   ├── 02_clean.py                 # Ch.1 — cleaning pipeline: wide → long format
│   ├── 03_eda.py                   # Ch.1 — EDA: trends, sector analysis, 7 charts
│   ├── 04_download_inspect_ev.py   # Ch.2 — download + inspect StatCan vehicle tables
│   ├── 05_clean_ev.py              # Ch.2 — clean registrations, build mandate reference
│   ├── 06_ev_eda.py                # Ch.2 — EDA: adoption trends, fuel mix, 5 charts
│   └── 07_ev_demand_model.py       # Ch.2 — kWh demand projection + grid stress scoring
│
├── outputs/
│   ├── plots/
│   │   ├── ch1/                    # 7 PNG charts from 03_eda.py
│   │   └── ch2/                    # 8 PNG charts from 06_ev_eda.py + 07_ev_demand_model.py
│   └── reports/
│       └── eda_report.txt          # Full console output from EDA runs
│
├── docs/
│   ├── data-sources.md             # Source citations, URLs, format quirks
│   └── findings.md                 # Key findings, Ch.1 and Ch.2
│
├── canada_energy_chapter1.html     # Self-contained interactive portfolio report — Ch.1
├── canada_energy_chapter2.html     # Self-contained interactive portfolio report — Ch.2
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## The Data Pipeline

Scripts are numbered — run them in order. Chapter 1 (01–03) and Chapter 2 (04–07) share the same pattern: download/inspect → clean → EDA → (model).

### Chapter 1 — Energy Baseline

#### `01_inspect.py` — Structural Audit

Audits every raw file before any cleaning. Surfaces column names, date ranges, unit types, null rates, geography and sector fields. Produces a "flags" report telling you exactly what the cleaning job looks like before writing any cleaning code.

```bash
python scripts/01_inspect.py
```

**Input:** Any `.csv`, `.xlsx`, or `.xls` in `data/raw/`
**Output:** Console report
**Why it exists:** Inspect before you assume. Both government sources have non-standard formats that will break naive `pd.read_csv()` calls.

---

#### `02_clean.py` — Cleaning Pipeline

Transforms the raw NRCan multi-sheet Excel workbook into a single, analysis-ready long-format CSV.

**What it handles:**
- Scans each sheet to find the real header row (years 2000–2023 are buried in row 7, not as column headers)
- Strips blank rows at top (rows 0–6 are empty/title) and footnotes at bottom
- Removes footnote superscripts from category names (`Raild` → `Rail`, `Air1,b` → `Air`)
- Melts wide format → long format (one row per category + year)
- Tags every row with `Sheet`, `Sector`, and `Metric`
- Combines all 11 sheets into one unified CSV

```bash
python scripts/02_clean.py
```

**Input:** `data/raw/HB2023e.xls`
**Output:** `data/cleaned/energy_clean.csv`
**Sheets processed:** Transportation3, Passenger1–4, Freight1–4, Electricity1–2

---

#### `03_eda.py` — Exploratory Data Analysis

Runs the full EDA. Produces 7 charts and a written report saved to disk.

```bash
python scripts/03_eda.py
```

**Input:** `data/cleaned/energy_clean.csv`
**Output:** `outputs/plots/ch1/*.png`, `outputs/reports/eda_report.txt`

| Chart | What it shows |
|-------|---------------|
| `01_sector_totals.png` | Energy use by sector, 2023 |
| `02_ghg_trend_by_sector.png` | GHG emissions trend, 2000–2023 |
| `03_top10_categories.png` | Top 10 energy-use categories |
| `04_ten_year_trend.png` | Sector growth lines, 2013–2023 |
| `05_clean_energy_share.png` | Clean energy % of transportation, 2013–2023 |
| `06_ghg_intensity_trend.png` | GHG intensity change per sector |
| `07_chapter2_transport_baseline.png` | Transportation energy baseline for Ch.2 |

---

### Chapter 2 — EV Explosion

#### `04_download_inspect_ev.py` — Download + Structural Audit

Downloads the two core StatCan vehicle registration tables as bulk CSV bundles and prints the same kind of structural inspection as `01_inspect.py` — shape, columns, dtypes, date range, and unique dimension values.

```bash
python scripts/04_download_inspect_ev.py
```

**Input:** None (downloads directly from StatCan)
**Output:** `data/raw/ev/<table_label>/*.csv`, console inspection report
**Tables:**
- `23-10-0308-01` — Annual vehicle registrations by type and fuel, 2017–2024
- `20-10-0025-01` — Quarterly new vehicle registrations by geography, 2017–2023

---

#### `05_clean_ev.py` — Cleaning Pipeline

Cleans both raw registration tables into analysis-ready datasets and builds a hand-compiled ZEV mandate reference table covering the September 2025 federal mandate pause and subsequent provincial rollbacks.

**What it handles:**
- Maps 18 raw StatCan vehicle-type categories down to 4 analysis segments: light passenger, light truck/SUV, heavy freight, urban transit
- Filters to the 10 provinces (drops territories and national totals)
- Aggregates weight sub-classes within each segment
- Chunked reading for the 7.9M-row quarterly table, filtered to province-level geography
- Builds a dual-scenario mandate table (`original` vs `revised`) reflecting the 2025–2026 federal pause and BC/Quebec target reductions

```bash
python scripts/05_clean_ev.py
```

**Input:** `data/raw/ev/*/`
**Output:** `data/cleaned/ev_annual_clean.csv`, `data/cleaned/ev_quarterly_clean.csv`, `data/cleaned/ev_zev_mandates.csv`

---

#### `06_ev_eda.py` — Exploratory Data Analysis

Runs EV-focused EDA: provincial adoption gaps, segment growth, quarterly sales trends, fuel mix, and the mandate scenario comparison.

```bash
python scripts/06_ev_eda.py
```

**Input:** `data/cleaned/ev_annual_clean.csv`, `ev_quarterly_clean.csv`, `ev_zev_mandates.csv`
**Output:** `outputs/plots/ch2/*.png`, console findings summary

| Chart | What it shows |
|-------|---------------|
| `01_ev_share_by_province_2024.png` | EV share of total registrations by province |
| `02_ev_growth_by_segment.png` | EV registration growth 2017–2024 by vehicle segment |
| `03_quarterly_ev_sales_trend.png` | Quarterly new EV sales, top 5 provinces |
| `04_fuel_mix_by_province_2024.png` | Full fuel mix breakdown per province |
| `05_zev_mandate_scenarios.png` | Original vs. revised mandate trajectories |

---

#### `07_ev_demand_model.py` — Demand Projection + Grid Stress Model

Converts registered EV counts into annual kWh demand, projects the fleet forward to 2035 under both mandate scenarios, layers in heavy freight via federal MHDV targets, and scores each province's grid stress against Chapter 1's capacity baseline.

**What it handles:**
- Applies real-world consumption rates per segment (20–170 kWh/100km) × average annual km driven
- Projects EV fleet growth using each province's historical CAGR, capped by the applicable mandate ceiling
- Substitutes federal MHDV ZEV targets (39,000 by 2030, 180,000 by 2040) for heavy freight, since registration data is near-zero for that segment
- Computes a grid stress score = incremental EV demand ÷ available grid headroom
- Flags small grids (<5 TWh) and import-dependent provinces (PEI) separately rather than blending them into the main stress ranking, since percentage-based scores get distorted by absolute scale

```bash
python scripts/07_ev_demand_model.py
```

**Input:** `data/cleaned/ev_annual_clean.csv`, `ev_quarterly_clean.csv`, `ev_zev_mandates.csv`, `energy_clean.csv`
**Output:** `data/cleaned/ev_demand_projections.csv`, `data/cleaned/grid_stress_scores.csv`, `outputs/plots/ch2/06–08*.png`

| Chart | What it shows |
|-------|---------------|
| `06_demand_projection_by_province.png` | Projected annual EV demand, original vs. revised scenario |
| `07_grid_stress_heatmap.png` | Province × year stress score heatmap |
| `08_scenario_gap.png` | Stress score difference between mandate scenarios, 2035 |

---

## Key Findings

### Chapter 1 — Energy Baseline

| Finding | Number |
|---------|--------|
| Freight energy use growth, 2013–2023 | **+10.3%** |
| Drop in electricity GHG intensity | **−23.1%** |
| Clean energy share in 2023 | **19.4%** (down from 21.1% in 2013) |
| COVID spike in clean share (2020) | **22.1%** — demand collapse, not real progress |
| Total energy use growth, 2013–2023 | **+3.7%** |

### Chapter 2 — EV Explosion

| Finding | Number |
|---------|--------|
| EV fleet growth, 2017–2024 | **+489.7%** |
| National EV share of registrations, 2024 | **5.0%** (1,270,546 of 25,620,451 vehicles) |
| Provincial leaders | **BC 7.9%, QC 7.0%** — vs. SK at 1.5% |
| Largest EV segment by volume | **Light truck/SUV — 789,339** units (vs. 481,207 light passenger) |
| Federal ZEV mandate rollback (2035 target) | **100% → 75%**, paused for 2026 (Sept 2025) |
| Quebec ZEV mandate rollback (2035 target) | **100% → 90%** |
| National incremental EV demand by 2035, revised scenario | **+19.80 TWh** (vs. +21.36 TWh original) |
| Most grid-stressed provinces by 2035 | **SK (48.8%), NB (48.2%), NS (48.0%)** — fossil-heavy, mid-sized grids |
| Least grid-stressed provinces by 2035 | **NL (7.1%), QC (16.9%)** — hydro-dominant |
| Special case | **PEI (87.4%)** — excluded from ranking; imports ~60% of power from NB, small-grid distortion |

Full findings with tables: [`docs/findings.md`](docs/findings.md)

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/saeidtayeban/canada-energy.git
cd canada-energy

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download raw data (links in data/raw/README.md)
#    - StatCan 25-10-0015-01 → data/raw/2510001501-eng.csv
#    - NRCan HB2023e.xls     → data/raw/HB2023e.xls
#    - EV tables download automatically via 04_download_inspect_ev.py

# 4. Run the Chapter 1 pipeline
python scripts/01_inspect.py
python scripts/02_clean.py
python scripts/03_eda.py

# 5. Run the Chapter 2 pipeline
python scripts/04_download_inspect_ev.py
python scripts/05_clean_ev.py
python scripts/06_ev_eda.py
python scripts/07_ev_demand_model.py
```

`energy_clean.csv` and the `ev_*_clean.csv` files are already committed — you can skip straight to the EDA/model scripts if you just want to reproduce the analysis without re-downloading or re-cleaning.

---

## Chapter Map

| Chapter | Status | Description |
|---------|--------|-------------|
| **Ch.1 — Energy Baseline** | ✅ Complete | National transportation energy landscape, 2000–2023 |
| **Ch.2 — EV Explosion** | ✅ Complete | EV adoption modeling, dual-scenario demand projection, grid stress scoring |
| **Ch.3 — AI Grid Optimization** | 📋 Planned | ML models for peak demand prediction + smart charging |
| **Ch.4 — Smart Urbanism** | 📋 Planned | City growth, zoning, and local energy infrastructure |

---

## Data Sources

| Source | File | What it provides |
|--------|------|-----------------|
| [Statistics Canada Table 25-10-0015-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501) | `2510001501-eng.csv` | Monthly electricity generation by type and province, 2008–present |
| [NRCan Comprehensive Energy Use Database](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm) | `HB2023e.xls` | Transportation energy use, GHG, intensity by mode, 2000–2023 |
| [Statistics Canada Table 23-10-0308-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310030801) | `23100308.csv` | Annual vehicle registrations by type and fuel, 2017–2024 |
| [Statistics Canada Table 20-10-0025-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010002501) | `20100025.csv` | Quarterly new vehicle registrations by geography, 2017–2023 |
| Federal & provincial ZEV mandate announcements | `ev_zev_mandates.csv` (hand-compiled) | Original and revised ZEV sales targets, 2026/2030/2035, post-Sept 2025 rollback |

Full source notes and format quirks: [`docs/data-sources.md`](docs/data-sources.md)

---

## Tools

- **Python** — pandas, matplotlib, seaborn, numpy, openpyxl, xlrd, requests
- **Data** — Statistics Canada, Natural Resources Canada Office of Energy Efficiency
- **Visualization** — Custom HTML/CSS/JS portfolio report

---

*Built by [Saeid Tayeban](https://github.com/saeidtayeban) · York University · Toronto, ON*
