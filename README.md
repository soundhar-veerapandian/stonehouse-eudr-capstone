# DDS Tracking Model/System for EUDR
MSc Business Analytics Capstone — UCD Smurfit
Sponsor: Stonehouse Marketing Ltd
Team: Shreeja Kalathur, Dalia Dias, Soundhar Karthik Veerapandian

## Structure
- `src/` — Python pipeline (schema → database → generator → validation → forecast)
- `data/` — sponsor-provided source data + generated datasets
- `outputs/` — analysis results (footprint, exposure map, database, charts)
- `dashboard/` — Power BI dashboard (.pbix) + HTML prototype
- `docs/` — reports, literature synthesis matrix, journals

## Pipeline
exposure map → Annex II schema → SQLite DB → synthetic DDS (1,000) →
validation (182 flagged) → 12-month forecast → Power BI dashboard
