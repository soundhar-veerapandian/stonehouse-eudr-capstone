# dds_generator.py — manufactures realistic synthetic DDS records
import random
from datetime import date, timedelta
from dds_database import create_database, insert_dds, count_records

random.seed(42)   # reproducibility: same "random" data every run — cite this in your methodology

# ---- Parameters seeded from YOUR real data ----
SUPPLIERS = ["Western Hygiene Supplies", "Killeen Paper Mills", "Longford Fuels",
             "Connolly Pet Foods", "Millbrook Oils", "Atlantic Mills"]
PRODUCTS = [  # (commodity, hs_code, description, weight%) — weights mirror your exposure map
    ("wood",   "4818", "Toilet tissue rolls",     45),
    ("wood",   "4401", "Firelogs 700g",           20),
    ("cattle", "2309", "Beef pet food complete",  15),
    ("soy",    "2309", "Complete dog food (soy)", 15),
    ("soy",    "1507", "Soybean oil blend",        5),
]
COUNTRIES = {"wood": [("IE", 80), ("SE", 15), ("BR", 5)],
             "cattle": [("IE", 90), ("BR", 10)],
             "soy": [("BR", 50), ("AR", 30), ("US", 20)]}
RISK = {"IE": "low", "SE": "low", "US": "low", "BR": "standard", "AR": "standard"}
GEO = {"IE": (53.3, -7.7), "SE": (60.1, 15.0), "BR": (-10.5, -55.0),
       "AR": (-34.0, -64.0), "US": (39.0, -95.0)}

def weighted(pairs):
    items, weights = zip(*pairs)
    return random.choices(items, weights=weights)[0]

def generate(n=1000, fault_rate=0.10):
    conn = create_database()
    start = date(2024, 1, 1)                      # 3-year synthetic history
    for i in range(n):
        commodity, hs, desc, _ = weighted([(p, p[3]) for p in PRODUCTS])
        country = weighted(COUNTRIES[commodity])
        lat, lon = GEO[country]
        lat += random.uniform(-1.5, 1.5); lon += random.uniform(-1.5, 1.5)

        # volumes RISE toward the deadline: later days more likely
        day = int((random.random() ** 0.6) * 1095)   # 0.6 skews toward the end
        sub_date = start + timedelta(days=day)

        rec = {
            "ref":  f"DDS-{sub_date.year % 100}-{i:05d}",
            "supplier": random.choice(SUPPLIERS),
            "qty": round(random.uniform(500, 25000), 1),
            "prior": f"DDS-UP-{random.randint(1000,9999)}" if random.random() < 0.7 else "",
        }

        # ---- deliberate faults (~10%) for the validation layer to catch ----
        fault = random.random() < fault_rate
        ftype = random.choice(["no_geo", "bad_hs", "no_prior_import"]) if fault else None
        if ftype == "no_geo":            lat, lon = None, None
        if ftype == "bad_hs":            hs = hs[:2] + "x" + hs[3:]
        if ftype == "no_prior_import" and country != "IE": rec["prior"] = ""

        insert_dds(conn, (
            rec["ref"], "Stonehouse Marketing Ltd", "Dublin, Ireland", "IE1234567",
            rec["supplier"], commodity, hs, desc, rec["qty"],
            rec["qty"] * random.uniform(8, 14),          # estimated annual qty
            country, lat, lon,
            str(sub_date - timedelta(days=random.randint(30, 120))),  # production predates submission
            rec["prior"], 1, str(sub_date),
            RISK[country], "pending",
        ))
    conn.commit()
    print("Cabinet now holds:", count_records(conn), "DDS records")
    conn.close()

if __name__ == "__main__":
    generate(1000)
