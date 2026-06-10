# Chapter 1 Findings — Canada's Transportation Energy Baseline

## Dataset Summary

| Metric | Value |
|--------|-------|
| Source | NRCan Comprehensive Energy Use Database (HB2023e.xls) |
| Rows (cleaned) | 6,048 |
| Year range | 2000–2023 |
| Unique categories | 125 |
| Sectors | Electricity, Freight, Passenger, Total Transportation |
| Metrics | Energy Use, Intensity, GHG Emissions, Price / Other |
| Null rate | 21.2% (structural — blank separator rows in source) |

---

## Finding 1 — Freight is the fastest-growing energy sector

Freight energy use grew **+10.3%** from 2013 to 2023, the fastest of any sector. The top categories by energy use in 2023:

| Category | 2023 Energy Use |
|----------|----------------|
| Light Trucks | 336,290 units |
| Heavy Trucks | 271,279 units |
| Rail | 437,083 units |
| Marine | 214,221 units |

Light and heavy trucks together represent the bulk of freight's energy demand — and neither electrifies cheaply or quickly at commercial scale.

---

## Finding 2 — The electricity grid is genuinely decarbonizing

Electricity GHG intensity dropped **−23.1%** from 2013 to 2023. This is the strongest directional signal in the dataset. Canada's power grid is on a real decarbonization trajectory — renewables and nuclear are displacing fossil fuel generation in measurable terms.

This matters for Chapter 2: a cleaner grid means electrifying transportation has increasing real-world impact over time, not just shifting emissions from tailpipe to smokestack.

---

## Finding 3 — Clean energy share is declining despite grid improvements

Clean energy's share of transportation energy peaked at **22.1% in 2020** — not because Canada got cleaner, but because COVID-19 collapsed overall demand. By 2023 it had fallen back to **19.4%**, lower than any year since 2013.

**The COVID distortion matters:** the 2020 spike must be treated as an anomaly, not a trend, in any modeling work.

| Year | Clean Share |
|------|------------|
| 2013 | 21.1% |
| 2017 | 19.7% |
| 2019 | 19.0% |
| 2020 | 22.1% ← COVID |
| 2023 | 19.4% |

---

## Finding 4 — GHG intensity: roads are moving in the wrong direction

| Sector | Intensity change 2013–2023 |
|--------|---------------------------|
| Electricity | **−23.1%** ✓ |
| Passenger | **+0.6%** ✗ |
| Freight | **+2.5%** ✗ |

The electricity grid is cleaning up. Road transportation is not. Efficiency gains from fuel economy improvements are being cancelled by the shift toward larger vehicles and more kilometres driven.

---

## Finding 5 — Total energy use grew +3.7% but the story is in the mix

Overall transportation energy use grew **+3.7%** from 2013 to 2023. But this headline hides a divergence:

- Electricity sector: **−0.4%** (efficiency gains, grid optimization)
- Passenger: **+2.7%** (more travel, larger vehicles)
- Freight: **+10.3%** (e-commerce, supply chain intensification)

---

## The Core Tension

Canada is simultaneously:
1. Cleaning its electricity grid (−23.1% GHG intensity)
2. Growing its road freight load (+10.3% energy use)

These two trajectories are on a collision course. Chapter 2 models what happens when EV adoption connects them — pushing new electrical demand onto a grid that is getting cleaner but isn't sized for the load.

---

## Chapter 2 Bridge — Transportation Baseline

The following categories carry the most weight into the EV demand shock model:

| Category | Why it matters in Chapter 2 |
|----------|----------------------------|
| Light Trucks (336K units) | Fastest-growing segment, lowest current EV penetration |
| Heavy Trucks (271K units) | Highest intensity growth, hardest to electrify |
| Cars | Primary EV substitution target, largest fleet |
| Urban Transit | Highest clean energy upside, partially electric already |
| Rail | Already electrified in parts — model for others |
