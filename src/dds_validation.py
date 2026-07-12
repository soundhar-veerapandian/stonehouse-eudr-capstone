# dds_validation.py — the EUDR rulebook applied to the cabinet
import sqlite3

RULES = {
    "missing_geo":   "geolocation_lat IS NULL OR geolocation_lon IS NULL",
    "invalid_hs":    "hs_code GLOB '*[a-z]*'",          # any letter in the HS code
    "missing_prior": "country_of_production != 'IE' AND prior_dds_reference = ''",
}

def validate(db_path="dds_system.db"):
    conn = sqlite3.connect(db_path)
    total_flagged = set()

    for rule_name, condition in RULES.items():
        refs = [r[0] for r in conn.execute(
            f"SELECT dds_reference FROM dds WHERE {condition}").fetchall()]
        conn.execute(f"UPDATE dds SET status = 'flagged: {rule_name}' "
                     f"WHERE {condition} AND status NOT LIKE 'flagged%'")
        total_flagged.update(refs)
        print(f"{rule_name:<14} → {len(refs)} records")

    # everything not flagged is promoted to valid
    conn.execute("UPDATE dds SET status = 'valid' WHERE status = 'pending'")
    conn.commit()

    n = conn.execute("SELECT COUNT(*) FROM dds").fetchone()[0]
    v = conn.execute("SELECT COUNT(*) FROM dds WHERE status='valid'").fetchone()[0]
    print(f"\nResult: {v}/{n} valid  |  {len(total_flagged)} unique records flagged "
          f"({len(total_flagged)/n*100:.1f}%)")
    print("\nStatus breakdown:")
    for row in conn.execute("SELECT status, COUNT(*) FROM dds GROUP BY status ORDER BY 2 DESC"):
        print(f"  {row[0]:<28} {row[1]}")
    conn.close()

if __name__ == "__main__":
    validate()
