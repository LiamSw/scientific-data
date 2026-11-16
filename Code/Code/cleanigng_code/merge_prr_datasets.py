# Merge EUROCONTROL PRR datasets (2019, 2022–2025)
# Requires: pandas (already imported in your notebook as pd)
# Source CSV files are stored in datas/datas/evolution_low_cost/.
from pathlib import Path
import pandas as pd

DATA = Path(__file__).resolve().parents[3] / "datas" / "datas" / "evolution_low_cost"
source_files = [
    "prr_2022_lowcost_mainline.csv",
    "prr_2023_lowcost_mainline.csv",
    "prr_2024_lowcost_mainline.csv",
    "prr_2025_lowcost_mainline.csv",
]

# 1) Stack rows from separate source reports: CONCAT, not a SQL join.
frames = [pd.read_csv(DATA / filename) for filename in source_files]
all_observations = pd.concat(frames, ignore_index=True)

# 2) Validate that each (year, segment) combination appears only once.
if all_observations.duplicated(["year", "market_segment"]).any():
    raise ValueError("Duplicate year/segment: choose one published revision before merging.")

# 3) Convert LONG -> WIDE: one row per year, two columns for segments.
merged = (
    all_observations
    .pivot(index="year", columns="market_segment", values="average_daily_ifr_flights")
    .rename(columns={
        "Low-cost": "low_cost_daily_flights",
        "Mainline": "mainline_daily_flights"
    })
    .reset_index()
    .sort_values("year")
)

# 4) Preserve methodological context from original report.
metadata = (
    all_observations
    .drop_duplicates("year")
    [["year", "unit", "report_edition", "data_status", "classification_version", "source_url"]]
    .rename(columns={"report_edition": "source_report"})
)
merged = merged.merge(metadata, on="year", how="left", validate="one_to_one")
merged["low_cost_minus_mainline"] = (
    merged["low_cost_daily_flights"] - merged["mainline_daily_flights"]
)

merged = merged[[
    "year", "low_cost_daily_flights", "mainline_daily_flights",
    "low_cost_minus_mainline", "unit", "source_report", "data_status",
    "classification_version", "source_url"
]]

# 5) Export your finished CSV in data/.
output = DATA / "eurocontrol_lowcost_mainline_merged.csv"
merged.to_csv(output, index=False, encoding="utf-8-sig")
print(merged.to_string(index=False))
print(f"Saved: {output}")

# OPTIONAL chart in your notebook (plt and COLORS already defined there):
# fig, ax = plt.subplots(figsize=(10, 5))
# ax.plot(merged["year"], merged["low_cost_daily_flights"], "o-",
#         label="Low-cost", color=COLORS["Low-cost"])
# ax.plot(merged["year"], merged["mainline_daily_flights"], "s-",
#         label="Mainline", color=COLORS["Mainline"])
# ax.set_xticks(merged["year"])
# ax.set_xlabel("Year")
# ax.set_ylabel("Average daily IFR flights")
# ax.set_title("Low-cost vs Mainline (published EUROCONTROL PRR editions)")
# ax.legend()
# ax.text(0.01, -0.16, "2020–2021 missing; methodological revision from 2024 in PRR 2025.",
#         transform=ax.transAxes, fontsize=9)
# plt.show()

# CAUTION: Years 2020 and 2021 are not included; do not interpolate them.
# CAUTION: 2024 (PRR 2024) and 2025 (PRR 2025) use revised classifications.
# Do not calculate a precise 2024->2025 growth rate from these two rows.
# Use the growth rates explicitly reported on a harmonized basis in PRR 2025:
# Low-cost +6.4% and Mainline +4.3% vs 2024.
