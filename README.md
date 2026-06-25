# Canada Energy — How Does Canada Power Its Physical Future?

> A 4-chapter data analysis portfolio grounded in real infrastructure:
> power grids, vehicles, and cities. Built with Python and public Canadian government data.

**[→ Chapter 1: Energy Baseline](canada_energy_chapter1.html)**
**[→ Chapter 2: EV Explosion](canada_energy_chapter2.html)**
**[→ Chapter 3: AI Grid Optimization](canada_energy_chapter3.html)**

---

## The Question

Canada is simultaneously cleaning its electricity grid and growing its road freight load. These two trajectories are on a collision course. This project answers: *what does the data actually show, and what happens when EVs connect these two systems?*

The analysis is structured as an expanding spiral — starting with the macro view of what Canada has today, zooming in on how EVs shift that baseline, using AI to model the resulting stress on the grid, and finally landing at the city level where all of it becomes physical.

---

## Project Structure

```
canada-energy/
│
├── data/
│   ├── raw/                            # Source files — not committed (see download instructions)
│   │   ├── README.md                   # Download instructions for all source files
│   │   ├── ev/
│   │   │   ├── vehicle_registrations_by_type_fuel_annual/
│   │   │   │   ├── 23100308.csv
│   │   │   │   └── 23100308_MetaData.csv
│   │   │   └── new_vehicle_registrations_quarterly_geo/
│   │   │       ├── 20100025.csv
│   │   │       └── 20100025_MetaData.csv
│   │   └── grid/
│   │       ├── ieso/                   # PUB_Demand_YYYY.csv (2019–2025, from IESO)
│   │       └── aeso/                   # aeso_hourly_ail_2020_2025.csv (from AESO)
│   │
│   └── cleaned/                        # Processed, analysis-ready data — committed
│       ├── README.md                   # Full schema documentation
│       ├── energy_clean.csv            # 6,048 rows × 7 cols — Ch.1 long-format unified table
│       ├── ev_annual_clean.csv         # 960 rows × 6 cols — province × segment × fuel, 2017–2024
│       ├── ev_quarterly_clean.csv      # 4,144 rows × 6 cols — quarterly new sales by province
│       ├── ev_zev_mandates.csv         # 24 rows × 4 cols — dual-scenario mandate reference
│       ├── ev_demand_projections.csv   # EV fleet + kWh demand, 2024–2035, both scenarios
│       ├── grid_stress_scores.csv      # Province × year stress scores, both scenarios
│       └── grid_hourly_clean.csv       # 110,303 rows × 3 cols — hourly demand, ON + AB, 2019–2025
│
├── scripts/
│   ├── 01_inspect.py                   # Ch.1 — structural audit of raw source files
│   ├── 02_clean.py                     # Ch.1 — cleaning pipeline: wide → long format
│   ├── 03_eda.py                       # Ch.1 — EDA: trends, sector analysis, 7 charts
│   ├── 04_download_inspect_ev.py       # Ch.2 — download + inspect StatCan vehicle tables
│   ├── 05_clean_ev.py                  # Ch.2 — clean registrations, build mandate reference
│   ├── 06_ev_eda.py                    # Ch.2 — EDA: adoption trends, fuel mix, 5 charts
│   ├── 07_ev_demand_model.py           # Ch.2 — kWh demand projection + grid stress scoring
│   ├── 08_download_inspect_grid.py     # Ch.3 — download IESO/AESO hourly CSVs + inspect
│   ├── 09_clean_grid.py                # Ch.3 — clean both sources → unified grid_hourly_clean.csv
│   └── 10_peak_model.py                # Ch.3 — EV load overlay + smart charging simulation
│
├── data/outputs/                       # Ch.3 model outputs
│   ├── peak_summary.csv                # Headline results: province × year, MW saved, GHG avoided
│   ├── hourly_profiles.csv             # Full hourly demand traces, all province-years
│   └── charging_shift_detail.csv       # Hour-by-hour load shift, dumb vs smart charging
│
├── outputs/
│   ├── plots/
│   │   ├── ch1/                        # 7 PNG charts from 03_eda.py
│   │   └── ch2/                        # 8 PNG charts from 06_ev_eda.py + 07_ev_demand_model.py
│   └── reports/
│       └── eda_report.txt              # Full console output from EDA runs
│
├── docs/
│   ├── data-sources.md                 # Source citations, URLs, format quirks
│   └── findings.md                     # Key findings, Ch.1 through Ch.3
│
├── canada_energy_chapter1.html         # Interactive portfolio report — Ch.1
├── canada_energy_chapter2.html         # Interactive portfolio report — Ch.2
├── canada_energy_chapter3.html         # Interactive portfolio report — Ch.3
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

---

## The Data Pipeline

Scripts are numbered — run them in order within each chapter. All three chapters share the same pattern: download/inspect → clean → EDA/model.

---

### Chapter 1 — Energy Baseline

#### `01_inspect.py` — Structural Audit

Audits every raw file before any cleaning. Surfaces column names, date ranges, unit types, null rates, geography and sector fields. Produces a "flags" report telling you exactly what the cleaning job looks like before writing any cleaning code.

```bash
python scripts/01_inspect.py
```

**Input:** Any `.csv`, `.xlsx`, or `.xls` in `data/raw/`
**Output:** Console report

---

#### `02_clean.py` — Cleaning Pipeline

Transforms the raw NRCan multi-sheet Excel workbook into a single, analysis-ready long-format CSV.

**What it handles:**
- Scans each sheet to find the real header row (years 2000–2023 are buried in row 7)
- Strips blank rows and footnotes; removes footnote superscripts from category names
- Melts wide format → long format (one row per category + year)
- Tags every row with `Sheet`, `Sector`, and `Metric`
- Combines all 11 sheets into one unified CSV

```bash
python scripts/02_clean.py
```

**Input:** `data/raw/HB2023e.xls`
**Output:** `data/cleaned/energy_clean.csv`

---

#### `03_eda.py` — Exploratory Data Analysis

Runs the full EDA. Produces 7 charts and a written findings report.

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

Downloads the two core StatCan vehicle registration tables and prints a structural inspection: shape, columns, dtypes, date range, and unique dimension values.

```bash
python scripts/04_download_inspect_ev.py
```

**Input:** None (downloads directly from StatCan)
**Output:** `data/raw/ev/<table_label>/*.csv`, console inspection report

---

#### `05_clean_ev.py` — Cleaning Pipeline

Cleans both raw registration tables and builds a dual-scenario ZEV mandate reference covering the September 2025 federal pause and provincial rollbacks.

**What it handles:**
- Maps 18 raw StatCan vehicle-type categories down to 4 segments
- Filters to the 10 provinces; aggregates weight sub-classes
- Chunked reading for the 7.9M-row quarterly table
- Dual-scenario mandate table: `original` vs `revised` (post-2025 rollbacks)

```bash
python scripts/05_clean_ev.py
```

**Input:** `data/raw/ev/*/`
**Output:** `data/cleaned/ev_annual_clean.csv`, `ev_quarterly_clean.csv`, `ev_zev_mandates.csv`

---

#### `06_ev_eda.py` — Exploratory Data Analysis

EV-focused EDA: provincial adoption gaps, segment growth, quarterly sales trends, fuel mix, and mandate scenario comparison.

```bash
python scripts/06_ev_eda.py
```

**Input:** `data/cleaned/ev_annual_clean.csv`, `ev_quarterly_clean.csv`, `ev_zev_mandates.csv`
**Output:** `outputs/plots/ch2/*.png`

---

#### `07_ev_demand_model.py` — Demand Projection + Grid Stress Model

Converts registered EV counts into annual kWh demand, projects the fleet forward to 2035 under both mandate scenarios, and scores each province's grid stress against Chapter 1's capacity baseline.

```bash
python scripts/07_ev_demand_model.py
```

**Input:** `data/cleaned/ev_annual_clean.csv`, `ev_quarterly_clean.csv`, `ev_zev_mandates.csv`, `energy_clean.csv`
**Output:** `data/cleaned/ev_demand_projections.csv`, `data/cleaned/grid_stress_scores.csv`, `outputs/plots/ch2/06–08*.png`

---

### Chapter 3 — AI Grid Optimization

#### `08_download_inspect_grid.py` — Download + Structural Audit

Downloads hourly electricity demand data from two open Canadian grid operators — IESO (Ontario) and AESO (Alberta) — and runs a full structural inspection on both, flagging datetime resolution, demand column names, zero values, and time series gaps.

These two provinces were chosen because they have the best open hourly grid data in Canada and because they tell opposite stories: Ontario's nuclear-and-hydro grid is one of the cleanest in North America; Alberta runs primarily on gas and coal.

```bash
python scripts/08_download_inspect_grid.py
```

**Input:** None (downloads directly from IESO and AESO)
**Output:** `data/raw/grid/ieso/PUB_Demand_YYYY.csv` (2019–2025), `data/raw/grid/aeso/aeso_hourly_ail_2020_2025.csv`

---

#### `09_clean_grid.py` — Cleaning Pipeline

Transforms both raw grid files into a single unified long-format CSV with three columns: `timestamp` (UTC), `province`, `demand_mw`.

**What it handles:**
- IESO: skips 2-row metadata header; parses separate Date + Hour columns (1-based) into UTC datetime; localizes via `America/Toronto`
- AESO: reads only `Date_Begin_GMT` + `ACTUAL_AIL` from a 236-column generator-level file; drops all individual plant columns; uses GMT column to avoid DST duplicate-hour issue in local timestamps
- Gap audit per province: flags gaps > 1 hour; forward-fills gaps ≤ 3 hours; leaves larger gaps as NaN
- Zero MW values nulled out (not physically possible for a provincial grid)

```bash
python scripts/09_clean_grid.py
```

**Input:** `data/raw/grid/ieso/`, `data/raw/grid/aeso/`
**Output:** `data/cleaned/grid_hourly_clean.csv` — 110,303 rows × 3 cols

---

#### `10_peak_model.py` — Peak Demand Model + Smart Charging Simulation

The core Chapter 3 model. Overlays Chapter 2's EV demand projections on the historical grid baseline, identifies peak demand hours, and simulates a smart charging intervention that shifts evening EV load to overnight.

**What it handles:**
- Converts annual TWh projections → hourly MW load profiles using two charging behaviour assumptions:
  - *Dumb charging*: 70% of light vehicle energy loads 5–10pm; 30% overnight — mirrors how most EVs charge today
  - *Smart charging*: 100% of light vehicle load shifts to 10pm–6am; same total daily kWh, different clock time
- Heavy freight modeled as flat overnight depot charging regardless of scenario
- Baseline: top-100 peak hours per year, averaged across 2020–2024 (shared window for both provinces)
- Projection years: 2025, 2028, 2030, 2035
- GHG impact calculated using provincial grid intensity: 30 kg CO₂/MWh (ON) vs 490 kg CO₂/MWh (AB)

```bash
python scripts/10_peak_model.py
```

**Input:** `data/cleaned/grid_hourly_clean.csv`, `data/cleaned/ev_demand_projections.csv`
**Output:** `data/outputs/peak_summary.csv`, `data/outputs/hourly_profiles.csv`, `data/outputs/charging_shift_detail.csv`

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

**Core thesis:** Canada's grid is decarbonizing. Its roads are not.

### Chapter 2 — EV Explosion

| Finding | Number |
|---------|--------|
| EV fleet growth, 2017–2024 | **+489.7%** |
| National EV share of registrations, 2024 | **5.0%** (1,270,546 of 25,620,451 vehicles) |
| Provincial leaders | **BC 7.9%, QC 7.0%** — vs. SK at 1.5% |
| Largest EV segment by volume | **Light truck/SUV — 789,339** units |
| Federal ZEV mandate rollback (2035 target) | **100% → 75%**, paused for 2026 (Sept 2025) |
| National incremental EV demand by 2035, revised scenario | **+19.80 TWh** (vs. +21.36 TWh original) |
| Most grid-stressed provinces by 2035 | **SK (48.8%), NB (48.2%), NS (48.0%)** |
| Least grid-stressed provinces by 2035 | **NL (7.1%), QC (16.9%)** |

### Chapter 3 — AI Grid Optimization

| Finding | Number |
|---------|--------|
| Ontario baseline peak (top-100 avg) | **23,261 MW** |
| Alberta baseline peak (top-100 avg) | **12,030 MW** |
| EV load added to Ontario evening peak by 2030 | **+658 MW** |
| EV load added to Alberta evening peak by 2030 | **+405 MW** |
| Smart charging eliminates (Ontario, 2025–2030) | **100%** of EV-added peak load |
| Smart charging eliminates (Alberta, 2030) | **94%** of EV-added peak load |
| Smart charging eliminates (Alberta, 2035) | **49%** — overnight window starts crowding at scale |
| GHG avoided by smart charging, Ontario 2030 | **36,013 t CO₂/year** |
| GHG avoided by smart charging, Alberta 2030 | **339,736 t CO₂/year** |
| GHG multiplier: Alberta vs Ontario per MW peak shifted | **16×** |

**Core thesis:** Smart charging is a climate tool as much as a grid reliability tool — and it's 16× more powerful in provinces where the grid is dirtiest. Alberta has every incentive to prioritize smart charging infrastructure, even though Ontario faces higher absolute grid stress from Chapter 2. At scale (Alberta 2035), smart charging alone is insufficient — overnight windows crowd at high EV penetration, and grid investment becomes unavoidable.

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/saeidtayeban/canada-energy.git
cd canada-energy

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run Chapter 1
python scripts/01_inspect.py
python scripts/02_clean.py
python scripts/03_eda.py

# 4. Run Chapter 2
python scripts/04_download_inspect_ev.py
python scripts/05_clean_ev.py
python scripts/06_ev_eda.py
python scripts/07_ev_demand_model.py

# 5. Run Chapter 3
python scripts/08_download_inspect_grid.py
python scripts/09_clean_grid.py
python scripts/10_peak_model.py
```

`energy_clean.csv`, the `ev_*_clean.csv` files, and `grid_hourly_clean.csv` are committed — you can skip the download and cleaning scripts and run the EDA/model scripts directly to reproduce the analysis.

---

## Chapter Map

| Chapter | Status | Description |
|---------|--------|-------------|
| **Ch.1 — Energy Baseline** | ✅ Complete | National transportation energy landscape, 2000–2023 |
| **Ch.2 — EV Explosion** | ✅ Complete | EV adoption modeling, dual-scenario demand projection, grid stress scoring |
| **Ch.3 — AI Grid Optimization** | ✅ Complete | Hourly peak demand model, EV load overlay, smart charging simulation (ON + AB) |
| **Ch.4 — Smart Urbanism** | 📋 Planned | City growth, commercial zoning, and local energy infrastructure |

---

## Data Sources

| Source | File | What it provides |
|--------|------|-----------------|
| [NRCan Comprehensive Energy Use Database](https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm) | `HB2023e.xls` | Transportation energy use, GHG, intensity by mode, 2000–2023 |
| [Statistics Canada Table 25-10-0015-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510001501) | `2510001501-eng.csv` | Monthly electricity generation by type and province, 2008–present |
| [Statistics Canada Table 23-10-0308-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310030801) | `23100308.csv` | Annual vehicle registrations by type and fuel, 2017–2024 |
| [Statistics Canada Table 20-10-0025-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010002501) | `20100025.csv` | Quarterly new vehicle registrations by geography, 2017–2023 |
| [IESO Public Reports](https://reports-public.ieso.ca/public/Demand/) | `PUB_Demand_YYYY.csv` | Ontario hourly electricity demand, MW, 2019–2025 |
| [AESO Data Requests](https://www.aeso.ca/market/market-and-system-reporting/data-requests/) | `aeso_hourly_ail_2020_2025.csv` | Alberta Internal Load (AIL), MW hourly, 2020–2025 |
| Federal & provincial ZEV mandate announcements | `ev_zev_mandates.csv` (hand-compiled) | Original and revised ZEV targets, 2026/2030/2035, post-Sept 2025 rollback |

Full source notes and format quirks: [`docs/data-sources.md`](docs/data-sources.md)

---

## Tools

- **Python** — pandas, numpy, matplotlib, seaborn, openpyxl, xlrd, requests
- **Data** — Statistics Canada, NRCan Office of Energy Efficiency, IESO, AESO
- **Visualization** — Custom HTML/CSS/JS interactive portfolio reports

---

*Built by [Saeid Tayeban](https://github.com/saeidtayeban) · York University · Toronto, ON*
