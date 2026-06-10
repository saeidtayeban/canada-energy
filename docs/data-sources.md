# Data Sources

## 1. Statistics Canada — Table 25-10-0015-01

| Field | Value |
|-------|-------|
| **Full title** | Electric power generation, monthly generation by type of electricity |
| **URL** | https://www150.statcan.gc.ca/t1/tbl1/en/dtbl!25-10-0015-01 |
| **Geography** | Canada + all provinces/territories |
| **Coverage** | Monthly, 2008–present (some series from 2007) |
| **Unit** | Megawatt hours (MWh) |
| **Update frequency** | Monthly |
| **File used** | `2510001501-eng.csv` |

**Generation types covered:**
- Hydraulic turbine (Hydro)
- Nuclear steam turbine
- Total combustible fuels (coal, natural gas, petroleum, biomass)
- Wind power turbine
- Solar (photovoltaic + thermal)
- Tidal power turbine
- Other types

**Format quirks:**
- Wide pivot format — not a standard tidy CSV
- First 8 rows are metadata, not data
- `..` symbol = not available for that period
- Footnote numbers embedded in category names (e.g. `Hydraulic turbine 3`)
- Note: significant methodology change in January 2016 expanded coverage from ~400 to ~1,200 companies — affects historical comparisons for wind and solar especially

---

## 2. NRCan — Comprehensive Energy Use Database (CEUD)

| Field | Value |
|-------|-------|
| **Full title** | Comprehensive Energy Use Database — Transportation sector |
| **Publisher** | Natural Resources Canada, Office of Energy Efficiency |
| **URL** | https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/trends/comprehensive_tables/list.cfm |
| **Geography** | National (Canada) |
| **Coverage** | Annual, 2000–2023 |
| **Units** | PJ (petajoules), Mt CO2e, MJ/Pkm, MJ/Tkm, tonne/TJ, cents/litre |
| **Update frequency** | Annual |
| **File used** | `HB2023e.xls` |

**Sheets used (11 of 50):**

| Sheet | Content |
|-------|---------|
| Transportation3 | GHG emissions and price/background indicators for all transportation |
| Passenger1 | Passenger energy use by source and mode (PJ) |
| Passenger2 | Passenger energy intensity |
| Passenger3 | Passenger GHG emissions |
| Passenger4 | Passenger activity indicators (pkm, vehicle stock, fuel consumption) |
| Freight1 | Freight energy use by source and mode (PJ) |
| Freight2 | Freight energy intensity |
| Freight3 | Freight GHG emissions |
| Freight4 | Freight activity indicators (tkm, vehicle stock) |
| Electricity1 | Electricity generation energy use and generation by source |
| Electricity2 | Electricity GHG intensity |

**Format quirks:**
- Wide format — years 2000–2023 are column headers in row 7
- Rows 0–6 are blank or title rows
- Bottom rows contain footnotes, source citations, and definitions
- Category names contain footnote superscripts — stripped during cleaning
- `n.a.` = not applicable; `x` = suppressed; blank = zero or not reported

---

## Data Quality Notes

| Issue | Source | How handled |
|-------|--------|-------------|
| 21.2% null rate in `energy_clean.csv` | NRCan blank separator rows between sub-sections | Structural — not filled, not dropped from analysis |
| Footnote superscripts in category names | NRCan naming convention | Stripped in `02_clean.py` |
| `..` (not available) in StatCan CSV | StatCan standard notation | Treated as null in parsing |
| Wide-to-long reshape required | Both sources use wide format | Melted in `02_clean.py` |
| Methodology change Jan 2016 (StatCan) | Expanded survey coverage | Noted; affects wind/solar historical comparisons |
| Unit inconsistency across NRCan sheets | PJ, Mt, MJ/unit, cents | Metric column in cleaned CSV distinguishes types — do not aggregate across metrics |
