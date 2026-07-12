import sqlite3

# 1. CONNECT — opens (or creates) the database file
conn = sqlite3.connect("dds_system.db")

# 2. CURSOR — the "pen" that executes commands
cur = conn.cursor()

# 3. EXECUTE — create a small test table
cur.execute("""
    CREATE TABLE IF NOT EXISTS test_dds (
        dds_reference TEXT PRIMARY KEY,
        commodity     TEXT,
        quantity_kg   REAL
    )
""")

# CREATE: insert two records
cur.execute("INSERT OR REPLACE INTO test_dds VALUES (?, ?, ?)",
            ("DDS-26-00001", "wood", 1840.5))
cur.execute("INSERT OR REPLACE INTO test_dds VALUES (?, ?, ?)",
            ("DDS-26-00002", "cattle", 320.0))

# 4. COMMIT — save changes to the file
conn.commit()

# READ: query it back
rows = cur.execute("SELECT * FROM test_dds").fetchall()
print("What's in the cabinet:")
for row in rows:
    print("  ", row)

# 5. CLOSE — tidy up
conn.close()
