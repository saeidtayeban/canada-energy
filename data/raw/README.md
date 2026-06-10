# data/raw/

Raw source files downloaded directly from government databases.
**Not committed to the repo** due to file size — download them locally using the instructions below.

---

## File 1 — StatCan Table 25-10-0015-01

**What it is:** Monthly electric power generation by type of electricity, Canada and provinces.

**Download:**
1. Go to: https://www150.statcan.gc.ca/t1/tbl1/en/dtbl!25-10-0015-01
2. Click **Download options → Download entire table (CSV)**
3. Save as: `data/raw/2510001501-eng.csv`

**Format notes:**
- Wide pivot table format — years are column headers, not a column
- First 8 rows are metadata (title, frequency, release date) — skip during parsing
- `..` means data not available for that period
- Unit: Megawatt hours (MWh)
- Coverage: Canada + all provinces/territories, monthly from ~2008

---

## File 2 — NRCan Comprehensive Energy Use Database (HB2023e.xls)

**What it is:** Canada's full transportation energy use, GHG emissions, intensity, and prices by mode, 2000–2023.

**Download:**
1. Go to: https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm
2. Under **Transportation**, download the Excel workbook
3. Save as: `data/raw/HB2023e.xls`

**Format notes:**
- 50 sheets total; this project uses 11 (see below)
- Each sheet is a wide-format table — years 2000–2023 as column headers (row 7)
- Rows 0–6 are blank/title rows; bottom rows are footnotes
- Category names contain footnote superscripts (e.g. `Raild`, `Air1,b`) — stripped during cleaning
- Units vary by sheet: PJ (petajoules), Mt CO2e, MJ/Pkm, cents/litre

**Sheets used:**

| Sheet | Sector | Metric |
|-------|--------|--------|
| `Transportation3` | Total Transportation | GHG Emissions / Prices |
| `Passenger1` | Passenger | Energy Use (PJ) |
| `Passenger2` | Passenger | Intensity |
| `Passenger3` | Passenger | GHG Emissions |
| `Passenger4` | Passenger | Activity / Background |
| `Freight1` | Freight | Energy Use (PJ) |
| `Freight2` | Freight | Intensity |
| `Freight3` | Freight | GHG Emissions |
| `Freight4` | Freight | Activity / Background |
| `Electricity1` | Electricity | Energy Use / Generation |
| `Electricity2` | Electricity | Intensity / GHG |

---

## Once downloaded

Run the inspection script first — always before touching the data:

```bash
cd scripts
python 01_inspect.py
```

This audits both files and tells you exactly what the cleaning job looks like before you write a line of cleaning code.
