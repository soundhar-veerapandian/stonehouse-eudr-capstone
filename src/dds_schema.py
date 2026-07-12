# dds_schema.py — the official DDS record definition (from EUDR Annex II)
# This dataclass is the design "contract": every DDS in the system has these
# 19 fields. The database table in dds_database.py mirrors it column-for-column.

from dataclasses import dataclass
from datetime import date

@dataclass
class DDSRecord:
    # --- Identity & parties ---
    dds_reference: str          # unique ID, e.g. "DDS-26-00142"
    operator_name: str
    operator_address: str
    operator_eori: str          # EU customs ID
    supplier_name: str
    # --- Product ---
    commodity: str              # wood / cattle / soy / palm / cocoa / coffee / rubber
    hs_code: str                # e.g. "4818" (tissue)
    product_description: str
    quantity_kg: float
    estimated_annual_qty: float # 2026 simplification field — feeds forecasting
    # --- Origin (the EUDR heart) ---
    country_of_production: str  # ISO code: "IE", "BR", "ID"
    geolocation_lat: float
    geolocation_lon: float
    production_date: date
    # --- Compliance ---
    prior_dds_reference: str    # upstream DDS link ("" if none) — 2026 first-operator rule
    dd_confirmation: bool       # "due diligence carried out" statement
    submission_date: date       # feeds forecasting
    risk_level: str             # low / standard / high (country benchmarking)
    status: str                 # valid / flagged / pending (feeds validation)


from dds_schema import DDSRecord
print(len(DDSRecord.__dataclass_fields__), "fields defined")
