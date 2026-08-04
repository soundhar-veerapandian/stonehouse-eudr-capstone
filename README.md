# DDS Tracking Model/System for EUDR
MSc Business Analytics Capstone — UCD Smurfit
Sponsor: Stonehouse Marketing Ltd
Team: Shreeja Kalathur, Dalia Dias, Soundhar Karthik Veerapandian

## Structure
- `src/` — Python pipeline and model benchmarking
- `data/` — source data + generated datasets
- `outputs/` — results, database, figures, benchmark output
- `dashboard/` — Power BI dashboard (.pbix) + screenshot
- `docs/` — capstone report, sponsor briefing, synthesis matrix, journals

## Pipeline
exposure map (14/81) → Annex II schema (19 fields) → SQLite DB →
1,000 synthetic DDS → validation (818/182) → forecast (~60/month by 2028) →
ML extraction (98–100%) → Power BI dashboard

## Deliverable
The EUDR Compliance Analytics Framework — a six-stage generalisable method
(scope, model, store, populate & validate, analyse & forecast, report).

## Reproducibility
All synthetic data generated under fixed seed 42. Run src/ scripts in the
order listed above. Requires: pandas, openpyxl, xlrd, matplotlib,
scikit-learn, statsmodels.
