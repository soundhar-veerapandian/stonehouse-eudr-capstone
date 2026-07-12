# dds_database.py — the real DDS filing cabinet (EUDR Annex II schema)
import sqlite3

def create_database(db_path="dds_system.db"):
    """Create the dds table (19 columns from Annex II). Safe to run repeatedly."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dds (
            dds_reference         TEXT PRIMARY KEY,
            operator_name         TEXT NOT NULL,
            operator_address      TEXT,
            operator_eori         TEXT,
            supplier_name         TEXT NOT NULL,
            commodity             TEXT NOT NULL,
            hs_code               TEXT,
            product_description   TEXT,
            quantity_kg           REAL,
            estimated_annual_qty  REAL,
            country_of_production TEXT,
            geolocation_lat       REAL,
            geolocation_lon       REAL,
            production_date       TEXT,
            prior_dds_reference   TEXT,
            dd_confirmation       INTEGER,
            submission_date       TEXT,
            risk_level            TEXT,
            status                TEXT
        )
    """)
    conn.commit()
    return conn

def insert_dds(conn, rec):
    """CREATE: file one DDS record. rec = tuple of 19 values in column order."""
    conn.execute("INSERT OR REPLACE INTO dds VALUES (" + ",".join("?" * 19) + ")", rec)

def count_records(conn):
    """READ: how many DDS are in the cabinet?"""
    return conn.execute("SELECT COUNT(*) FROM dds").fetchone()[0]

def flag_record(conn, ref, new_status):
    """UPDATE: change a record's status (e.g. validation flags it)."""
    conn.execute("UPDATE dds SET status = ? WHERE dds_reference = ?", (new_status, ref))
    conn.commit()

def archive_record(conn, ref):
    """'DELETE' — EUDR requires 5-year retention, so we soft-delete by marking."""
    flag_record(conn, ref, "archived")

# Run this file directly to create the table and confirm
if __name__ == "__main__":
    conn = create_database()
    print("Table 'dds' ready. Records currently:", count_records(conn))
    conn.close()
