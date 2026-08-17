# DDS Tracking Model/System for EUDR

MSc Business Analytics Capstone — UCD Michael Smurfit Graduate Business School
Sponsor: Stonehouse Marketing Ltd
Team: Shreeja Kalathur, Dalia Robin Dias, Soundhar Karthik Veerapandian
Supervisors: Dr Hippolyte Lefebvre (academic), Mr Brian Minehane (industry)

## Overview

From 30 December 2026 the EU Deforestation Regulation requires operators to prove
that products linked to seven regulated commodities are deforestation-free, evidenced
by Due Diligence Statements (DDS). This project identifies which of Stonehouse's 81
own-brand products fall in scope and builds an analytics system to generate, store,
validate, analyse, forecast and report on DDS. Since no real statements exist yet,
the system is demonstrated on synthetic data calibrated to real supplier and volume
records.

## Structure

- `src/` — Python pipeline and model benchmarking
- `data/` — source data + generated datasets
- `outputs/` — results, database, figures, benchmark output
- `dashboard/` — Power BI dashboard (.pbix) + screenshot
- `docs/` — capstone report, sponsor briefing, synthesis matrix, journals

## Pipeline
exposure map (14 of 81 in scope)
→ Annex II schema (19 fields, PK + self-referencing FK)
→ SQLite database (CRUD, archiving for 5-year retention)
→ 1,000 synthetic DDS (seed 42, ~10% seeded faults)
→ validation (818 valid / 182 flagged)
→ forecast (+1.1/month; ~60/month by early 2028)
→ ML extraction (98–100% fields; 78.6% under unseen vocabulary)
→ Power BI dashboard

## Key results

| Component | Result |

| Commodity exposure | 14 of 81 products in scope — wood (tissue, firelogs, firelighters) and pet food (cattle, soya) |
| Packaging footprint 2024 | ~326 t CO2e across 68 products (~1,040 t scaled to full range); 92% wood-derived |
| Validation | 818 valid, 182 flagged (119 missing prior reference, 33 missing geolocation, 30 invalid HS) |
| Forecast | +1.1 statements/month; ~60/month by early 2028 |
| ML extraction | 100% reference/quantity/description, 98% HS code on 60 unseen documents |
| Classifier benchmarking | Naive Bayes 78.6%, Linear SVM 78.6%, Logistic Regression 71.4% under unseen vocabulary |
| Triangulation | Wood 5.93 t computed vs 5.887 t audited (Repak) — under 1% difference |

## Deliverable

**The EUDR Compliance Analytics Framework** — a six-stage method (scope, model,
store, populate & validate, analyse & forecast, report) grounded in five design
principles derived and evaluated under Design Science Research. The framework is
potentially transferable to other operators facing similar obligations; its
transferability is argued analytically rather than empirically demonstrated, having
been instantiated in a single organisational setting.

## Reproducibility

All synthetic data is generated under fixed random seed 42; every figure in the
report regenerates identically. Run the `src/` scripts in pipeline order.

```bash
pip install pandas openpyxl xlrd matplotlib scikit-learn statsmodels
```

Full generation parameters are documented in Appendix C of the capstone report.

## Note on data

Sponsor-provided datasets are commercial in confidence. All DDS records in this
repository are synthetic; no real supplier or consignment data is processed at any
stage.
