# export_for_powerbi.py — cabinet -> CSV for Power BI
import sqlite3
import pandas as pd

conn = sqlite3.connect("dds_system.db")
df = pd.read_sql("SELECT * FROM dds", conn)
conn.close()

# one convenience column: clean status group for charting
df["status_group"] = df["status"].apply(
    lambda s: "valid" if s == "valid" else s.replace("flagged: ", ""))

df.to_csv("dds_for_powerbi.csv", index=False)
print("Exported", len(df), "records -> dds_for_powerbi.csv")
