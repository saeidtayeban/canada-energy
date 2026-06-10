# data/cleaned/

Processed outputs from `scripts/02_clean.py`. These files **are committed** to the repo — they are the cleaned, analysis-ready versions that all downstream scripts read from.

---

## energy_clean.csv

**Source:** NRCan `HB2023e.xls` (11 sheets)  
**Shape:** 6,048 rows × 7 columns  
**Year range:** 2000–2023  
**Null rate:** 21.2% in `Value` — structural (blank separator rows in source, not missing data)

### Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `Sheet` | string | Source sheet name | `Freight1` |
| `Sector` | string | High-level sector tag | `Freight` |
| `Metric` | string | What is being measured | `Energy Use` |
| `Category` | string | Specific vehicle/fuel/indicator | `Heavy Trucks` |
| `Total Growth 2000–2023` | float | % change over full period | `38.5` |
| `Year` | int | Calendar year | `2023` |
| `Value` | float | Numeric measurement | `271278.6` |

### Sector values
- `Electricity` — electricity generation sector (sheets: Electricity1, Electricity2)
- `Freight` — freight transportation (sheets: Freight1–4)
- `Passenger` — passenger transportation (sheets: Passenger1–4)
- `Total Transportation` — combined transport (sheet: Transportation3)

### Metric values
- `Energy Use` — secondary energy consumption, typically in petajoules (PJ)
- `Intensity` — energy or GHG per unit of activity (MJ/Pkm, MJ/Tkm, tonne/TJ)
- `GHG Emissions` — greenhouse gas emissions in Mt CO2e or related units
- `Price / Other` — fuel prices, activity indicators, background data

### Notes
- Category names were cleaned to remove NRCan footnote superscripts (`Raild` → `Rail`, `Air1,b` → `Air`)
- Some categories appear multiple times across sheets with different metrics — this is intentional
- The `Total Growth 2000–2023` column comes directly from NRCan source; not calculated
