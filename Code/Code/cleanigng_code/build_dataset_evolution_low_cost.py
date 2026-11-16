
from pathlib import Path
import pandas as pd

# Path to the data folder
DATA = Path.cwd() / "data"

# ==========================================
# 1. HISTORICAL DATA: 1998–2018
# Source: EUROCONTROL Data Snapshot #34
# ==========================================

historic = pd.read_csv(
    DATA / "C:\\Users\\desca\\OneDrive - UCL\\Erasmus cours - M2 Q1\\scientific data visualization\\final project\\Notebook_aviation_low_cost_complet\\aviation_lowcost\\data\\eurocontrol_lcc_1998_2018.csv"
)

historic = historic[["year", "lcc_share_pct"]].copy()

historic["source_group"] = "snapshot_1998_2018"
historic["lcc_flights"] = pd.NA
historic["total_ifr_flights"] = pd.NA

historic["source_url"] = (
    "https://www.eurocontrol.int/publication/"
    "eurocontrol-data-snapshot-34-rise-low-cost-carriers-europe"
)

historic["calculation_note"] = (
    "Published annual share; historic classification"
)


# ==========================================
# 2. ANNUAL DATA: 2019–2022
# Source: EUROCONTROL Standard Inputs
# ==========================================

annual_counts = pd.read_csv(
    DATA / "C:\\Users\\desca\\OneDrive - UCL\\Erasmus cours - M2 Q1\\scientific data visualization\\final project\\Notebook_aviation_low_cost_complet\\aviation_lowcost\\data\\eurocontrol_lcc_annual_2019_2022.csv"
)

# Calculate annual low-cost share
annual_counts["lcc_share_pct"] = (
    annual_counts["lcc_flights"]
    / annual_counts["total_ifr_flights"]
    * 100
).round(4)

annual_counts["source_group"] = "standard_inputs_2019_2022"

annual_counts["calculation_note"] = (
    "Annual flights ratio; updated market segment classification"
)


# ==========================================
# 3. RECENT DATA: 2024–2025
# Source: EUROCONTROL PRR reports
# ==========================================

recent = pd.read_csv(
    DATA / "C:\\Users\\desca\\OneDrive - UCL\\Erasmus cours - M2 Q1\\scientific data visualization\\final project\\Notebook_aviation_low_cost_complet\\aviation_lowcost\\data\\eurocontrol_segments_2024_2025.csv"
)

# Select only low-cost flights
recent = recent.loc[
    recent["segment"] == "Low-cost",
    ["year", "share_pct", "source_url"]
].copy()

recent = recent.rename(
    columns={"share_pct": "lcc_share_pct"}
)

recent["source_group"] = "prr_2024_2025"
recent["lcc_flights"] = pd.NA
recent["total_ifr_flights"] = pd.NA

recent["calculation_note"] = (
    "PRR published rounded share; annual average daily flights"
)


# ==========================================
# 4. COMBINE THE THREE DATASETS
# ==========================================

columns = [
    "year",
    "lcc_share_pct",
    "source_group",
    "lcc_flights",
    "total_ifr_flights",
    "source_url",
    "calculation_note"
]

full = pd.concat(
    [
        historic[columns],
        annual_counts[columns],
        recent[columns]
    ],
    ignore_index=True
)

# Sort by year
full = full.sort_values("year").reset_index(drop=True)

# Set data types
full["year"] = full["year"].astype(int)

full[["lcc_flights", "total_ifr_flights"]] = full[
    ["lcc_flights", "total_ifr_flights"]
].astype("Int64")


# ==========================================
# 5. VERIFY AND SAVE THE DATASET
# ==========================================

expected_years = set(range(1998, 2023)) | {2024, 2025}

assert set(full["year"]) == expected_years
assert full["year"].is_unique
assert full["lcc_share_pct"].between(0, 100).all()

# Save the final CSV
full.to_csv(
    DATA / "C:\\Users\\desca\\OneDrive - UCL\\Erasmus cours - M2 Q1\\scientific data visualization\\final project\\Notebook_aviation_low_cost_complet\\aviation_lowcost\\data\\eurocontrol_lcc_annual_1998_2025_by_source.csv",
    index=False
)

# Display the result
print(full[["year", "lcc_share_pct", "source_group"]])

print("Dataset created successfully!")
