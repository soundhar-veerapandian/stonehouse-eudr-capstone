# dds_forecast.py — monthly DDS volumes + 12-month forecast
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. LOAD: submission dates from the cabinet
conn = sqlite3.connect("dds_system.db")
df = pd.read_sql("SELECT submission_date FROM dds", conn)
conn.close()

# 2. BUILD the time series: count DDS per month
df["submission_date"] = pd.to_datetime(df["submission_date"])
monthly = df.set_index("submission_date").resample("ME").size()
print("Monthly series:", len(monthly), "months, from",
      monthly.index[0].date(), "to", monthly.index[-1].date())

# 3. FIT a straight line (x = month number, y = DDS count)
x = np.arange(len(monthly))
slope, intercept = np.polyfit(x, monthly.values, 1)
print(f"Trend: {slope:+.2f} DDS per month  (growing)" )

# 4. EXTEND 12 months ahead
future_x = np.arange(len(monthly), len(monthly) + 12)
forecast = slope * future_x + intercept
future_index = pd.date_range(monthly.index[-1] + pd.offsets.MonthEnd(1),
                             periods=12, freq="ME")

# 5. PLOT: history + fitted line + forecast
plt.figure(figsize=(9, 4.5))
plt.plot(monthly.index, monthly.values, label="Actual monthly DDS", color="#1f4d3b")
plt.plot(monthly.index, slope * x + intercept, "--", label="Fitted trend", color="#c07a1e")
plt.plot(future_index, forecast, "o--", label="12-month forecast", color="#b5651d")
plt.title("DDS volume: history and 12-month forecast")
plt.ylabel("DDS per month"); plt.legend(); plt.tight_layout()
plt.savefig("dds_forecast.png", dpi=130)
plt.show()

print(f"\nForecast for final month: ~{forecast[-1]:.0f} DDS "
      f"(vs ~{monthly.values[-3:].mean():.0f}/month recently)")
